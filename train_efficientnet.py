"""
DermLens — EfficientNet-B3 Fine-tuning Script
================================================
Fine-tunes EfficientNet-B3 on the ACNE04 dataset for IGA severity grading.

Dataset: https://github.com/xpwu95/LDL
Classes: 0=Clear, 1=Mild, 2=Moderate, 3=Severe (mapped from ACNE04 grades)

Usage:
    python train_efficientnet.py --data-dir /path/to/ACNE04 --epochs 30

Expected ACNE04 folder structure:
    ACNE04/
        Classification/
            Level_0/   (Clear)
            Level_1/   (Mild)
            Level_2/   (Moderate)
            Level_3/   (Severe)
"""

import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

try:
    import timm
except ImportError:
    raise SystemExit("Install timm: pip install timm")


def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.Resize((320, 320)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
            transforms.RandomCrop(300),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    return transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def train(data_dir: str, epochs: int = 30, batch_size: int = 16, lr: float = 3e-4):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Dataset
    full_dataset = datasets.ImageFolder(
        root=os.path.join(data_dir, "Classification"),
        transform=get_transforms(train=True),
    )
    n_train = int(0.85 * len(full_dataset))
    n_val   = len(full_dataset) - n_train
    train_ds, val_ds = random_split(full_dataset, [n_train, n_val])
    val_ds.dataset.transform = get_transforms(train=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=4, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)

    # Model
    model = timm.create_model("efficientnet_b3", pretrained=True, num_classes=4)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    out_path = os.path.join("backend", "models", "efficientnet_acne.pt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    for epoch in range(1, epochs + 1):
        # ── Train ────────────────────────────────────────────────────
        model.train()
        train_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # ── Val ──────────────────────────────────────────────────────
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                preds = model(imgs).argmax(1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        val_acc = correct / total
        scheduler.step()

        print(f"Epoch {epoch:3d}/{epochs}  train_loss={train_loss/len(train_loader):.4f}  val_acc={val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), out_path)
            print(f"  ✓ Saved best model (val_acc={val_acc:.4f}) → {out_path}")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.4f}")
    print(f"Model saved to: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir",   default="./ACNE04",   help="Path to ACNE04 dataset root")
    parser.add_argument("--epochs",     default=30, type=int)
    parser.add_argument("--batch-size", default=16, type=int)
    parser.add_argument("--lr",         default=3e-4, type=float)
    args = parser.parse_args()
    train(args.data_dir, args.epochs, args.batch_size, args.lr)
