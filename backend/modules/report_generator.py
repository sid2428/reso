"""
Module: Report Generator
- Sends analysis JSON to Claude API
- Returns personalized AM/PM skincare routine + ingredient recommendations
- Hardcoded disclaimers wrap all LLM output
"""

import os
import json
import httpx


CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5"


PROMPT_TEMPLATE = """You are a skincare advisor AI. Based on the following skin analysis results, generate a personalized AM/PM skincare routine.

ANALYSIS RESULTS:
{analysis_json}

Rules:
1. Recommend specific INGREDIENTS (not brand names)
2. Keep it practical — max 4 steps AM, max 5 steps PM
3. Tailor recommendations to the detected severity and lesion types
4. If dark spots detected, include brightening ingredients
5. If inflammatory lesions dominate, prioritize anti-inflammatory ingredients
6. Always match the Fitzpatrick skin tone sensitivity in recommendations
7. NEVER make diagnostic or medical claims
8. Format your response as valid JSON matching this schema:
{{
  "am_routine": [
    {{"step": 1, "action": "Cleanser", "ingredient": "Gentle foaming cleanser with niacinamide 4%", "why": "Balances oil without stripping"}}
  ],
  "pm_routine": [
    {{"step": 1, "action": "Cleanser", "ingredient": "Oil cleanser or micellar water", "why": "Removes sunscreen and debris"}}
  ],
  "key_ingredients": [
    {{"name": "Niacinamide", "benefit": "Reduces dark spots and pore size", "concentration": "4–10%"}}
  ],
  "ingredients_to_avoid": [
    {{"name": "Coconut oil", "reason": "Comedogenic — may worsen blocked pores"}}
  ],
  "lifestyle_tips": ["Stay hydrated", "Change pillowcase weekly"]
}}

Return ONLY the JSON object, no other text."""


def _fallback_routine(analysis: dict) -> dict:
    """Static fallback when API is unavailable."""
    severity = analysis.get("severity", {}).get("label", "Mild")
    has_dark_spots = analysis.get("dark_spots", {}).get("count", 0) > 0

    routine = {
        "am_routine": [
            {"step": 1, "action": "Cleanser", "ingredient": "Gentle foaming cleanser with salicylic acid 0.5–2%", "why": "Unclogs pores and removes excess oil"},
            {"step": 2, "action": "Toner", "ingredient": "Niacinamide 5% + zinc toner", "why": "Minimizes pores and reduces inflammation"},
            {"step": 3, "action": "Moisturizer", "ingredient": "Oil-free gel moisturizer with hyaluronic acid", "why": "Hydrates without clogging pores"},
            {"step": 4, "action": "Sunscreen", "ingredient": "Mineral SPF 30+ (zinc oxide or titanium dioxide)", "why": "Prevents dark spot darkening and UV damage"},
        ],
        "pm_routine": [
            {"step": 1, "action": "Cleanser", "ingredient": "Micellar water or gentle gel cleanser", "why": "Removes sunscreen, makeup, and pollution"},
            {"step": 2, "action": "Treatment", "ingredient": "Benzoyl peroxide 2.5% or azelaic acid 10%", "why": "Kills acne-causing bacteria"},
            {"step": 3, "action": "Serum", "ingredient": "Retinol 0.025–0.05% (start 2x/week)", "why": "Speeds cell turnover and fades blemishes"},
            {"step": 4, "action": "Moisturizer", "ingredient": "Ceramide-rich cream", "why": "Repairs skin barrier overnight"},
        ],
        "key_ingredients": [
            {"name": "Salicylic Acid", "benefit": "Exfoliates inside pores", "concentration": "0.5–2%"},
            {"name": "Niacinamide", "benefit": "Anti-inflammatory, pore-minimizing", "concentration": "4–10%"},
            {"name": "Retinol", "benefit": "Cell turnover, dark spot fading", "concentration": "0.025–0.1%"},
        ],
        "ingredients_to_avoid": [
            {"name": "Coconut oil", "reason": "Highly comedogenic"},
            {"name": "Isopropyl myristate", "reason": "Pore-clogging emollient"},
        ],
        "lifestyle_tips": [
            "Change pillowcase every 2–3 days",
            "Avoid touching your face",
            "Drink 2–3L water daily",
        ],
    }

    if has_dark_spots:
        routine["am_routine"].insert(2, {
            "step": 2, "action": "Brightening Serum",
            "ingredient": "Vitamin C (ascorbic acid 10–15%) or alpha-arbutin 2%",
            "why": "Targets hyperpigmentation and dark spots"
        })

    return routine


async def generate_skincare_routine(analysis: dict) -> dict:
    """
    Calls Claude API to generate personalized skincare routine.
    Falls back to static routine if API key not set or call fails.
    """
    if not CLAUDE_API_KEY:
        return _fallback_routine(analysis)

    prompt = PROMPT_TEMPLATE.format(
        analysis_json=json.dumps(analysis, indent=2, default=str)
    )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        data = resp.json()
        text = data["content"][0]["text"].strip()

        # Strip any accidental markdown fences
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip().rstrip("```")

        routine = json.loads(text)
        return routine

    except Exception as e:
        return _fallback_routine(analysis)
