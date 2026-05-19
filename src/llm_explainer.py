"""Optional Claude-powered explanation layer.

The app works without an API key. Claude is used only to translate model outputs into
business-friendly language, not to make banking decisions.
"""

from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv

from src.explainability import analyst_explanation, customer_support_explanation

load_dotenv()


def generate_explanation_with_optional_claude(transaction: Dict, prediction, reason_text: str) -> Dict[str, str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

    fallback = {
        "analyst": analyst_explanation(transaction, prediction.fraud_score, prediction.recommended_action),
        "customer_support": customer_support_explanation(transaction, prediction.recommended_action),
        "mode": "Template explanation; Claude API key not configured.",
    }

    if not api_key:
        return fallback

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""
You are helping a bank explain an AI-assisted card fraud decision.
Do not make a decision. Only explain the provided model outputs.
Use clear, non-technical, compliance-friendly language.

Transaction summary:
{transaction}

Fraud score: {prediction.fraud_score:.2f}
Risk level: {prediction.risk_level}
Recommended action: {prediction.recommended_action}
Human review required: {prediction.human_review_required}
Reason codes:
{reason_text}

Return two short sections:
1. Fraud analyst explanation
2. Customer support explanation
"""
        msg = client.messages.create(
            model=model,
            max_tokens=450,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text
        return {"analyst": text, "customer_support": "See Claude-generated explanation above.", "mode": f"Claude explanation via {model}"}
    except Exception as exc:
        fallback["mode"] = f"Claude unavailable; template used. Error: {exc}"
        return fallback
