import json
import time
from typing import Dict, Any, Optional, List
import streamlit as st
from anthropic import Anthropic, APIError
import os


def get_client() -> Anthropic:
    """Get Anthropic client with API key."""
    from utils.state import get_api_key

    api_key = get_api_key()
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or session")
    return Anthropic(api_key=api_key)


def extract_tender_data(tender_text: str) -> Dict[str, Any]:
    """
    Extract structured tender/RFP data using Claude API.

    Args:
        tender_text: Full text extracted from tender document

    Returns:
        Structured tender data as dictionary
    """
    client = get_client()

    system_prompt = """Extract tender information from the document and return ONLY valid JSON (no other text).

Return this exact JSON structure:
{
  "tender_title": "title or 'Not specified'",
  "issuing_organization": "organization name or 'Not specified'",
  "tender_reference": "reference number or 'Not specified'",
  "submission_deadline": "deadline date or 'Not specified'",
  "scope_of_work": "brief summary or 'Not specified'",
  "evaluation_criteria": [
    {"criterion": "name", "weight_percentage": 0, "category": "technical"}
  ],
  "mandatory_requirements": ["requirement 1", "requirement 2"],
  "technical_specifications": ["spec 1", "spec 2"],
  "commercial_requirements": ["term 1", "term 2"],
  "compliance_requirements": ["requirement 1", "requirement 2"],
  "deliverables": ["deliverable 1", "deliverable 2"],
  "contract_duration": "duration or 'Not specified'"
}

IMPORTANT: Return ONLY the JSON, nothing else. No explanation, no markdown, just the JSON."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": tender_text}],
        )

        response_text = message.content[0].text

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        print(f"DEBUG: Claude response: {response_text[:500]}")  # Print first 500 chars
        tender_data = json.loads(response_text)
        return tender_data
    except APIError as e:
        raise ValueError(f"Claude API error: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"DEBUG: Failed to parse response: {response_text[:1000]}")  # Print for debugging
        raise ValueError(f"Error parsing JSON response: {str(e)}")


def evaluate_supplier_bid(
    bid_text: str, tender_data: Dict[str, Any], criteria: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate a supplier bid against tender requirements.

    Args:
        bid_text: Full text of supplier bid
        tender_data: Tender information
        criteria: Evaluation criteria with weights

    Returns:
        Supplier evaluation as dictionary
    """
    client = get_client()

    system_prompt = f"""You MUST return ONLY a single valid JSON object. No other text.

Evaluate the bid. Return this exact structure:
{{
  "supplier_name": "company name",
  "supplier_country": "country",
  "bid_reference": "reference or na",
  "overall_score": 75,
  "category_scores": {{
    "technical": {{"score": 75, "summary": "score summary", "strengths": [], "gaps": []}},
    "commercial": {{"score": 75, "summary": "score summary", "strengths": [], "gaps": []}},
    "compliance": {{"score": 75, "summary": "score summary", "strengths": [], "gaps": []}}
  }},
  "criterion_scores": [{{"criterion": "name", "score": 75, "evidence": "evidence text", "flag": "met"}}],
  "mandatory_requirements_status": [{{"requirement": "requirement", "status": "compliant", "evidence": "evidence text"}}],
  "hse_compliance": {{"status": "compliant", "details": "details"}},
  "esg_compliance": {{"status": "compliant", "details": "details"}},
  "iso_certifications": [],
  "proposed_price": "price or na",
  "proposed_timeline": "timeline or na",
  "key_risks": [],
  "recommendation": "brief recommendation",
  "completeness_percentage": 75
}}

Rules:
- Return ONLY the JSON object, nothing else
- Keep all text values SHORT and SIMPLE
- Use empty arrays [] if no items
- Use "na" for missing values
- Do NOT use quotes, apostrophes, or special characters inside text values"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": bid_text}],
        )

        response_text = message.content[0].text

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Clean up common JSON issues
        import re
        # Extract just the JSON part (between first { and last })
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)

        # Try to parse JSON
        try:
            evaluation = json.loads(response_text)
            return evaluation
        except json.JSONDecodeError as json_err:
            print(f"DEBUG: Failed to parse JSON. First 1000 chars: {response_text[:1000]}")
            print(f"DEBUG: Error details: {str(json_err)}")
            raise ValueError(f"Error parsing JSON response: {str(json_err)}")
    except APIError as api_err:
        raise ValueError(f"Claude API error: {str(api_err)}")


def generate_trade_off_analysis(
    tender_title: str, evaluation_data: Dict[str, Any]
) -> str:
    """
    Generate trade-off analysis between top suppliers.

    Args:
        tender_title: Title of the tender
        evaluation_data: All evaluation data

    Returns:
        Trade-off analysis text
    """
    client = get_client()

    prompt = f"""Based on the following evaluation data for {tender_title}, provide a concise trade-off analysis comparing the top suppliers. Highlight what each prioritizes differently and what Borouge would gain or trade off by selecting each.

{json.dumps(evaluation_data, indent=2)}

Provide a professional narrative analysis suitable for a procurement committee."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
    except APIError as e:
        raise ValueError(f"Claude API error: {str(e)}")


def chat_with_evaluation_data(
    user_message: str,
    tender_data: Dict[str, Any],
    supplier_evaluations: List[Dict[str, Any]],
    criteria: List[Dict[str, Any]],
    chat_history: List[Dict[str, str]],
) -> str:
    """
    Chat with Claude using full evaluation context.

    Args:
        user_message: User's question
        tender_data: Tender information
        supplier_evaluations: All supplier evaluations
        criteria: Evaluation criteria
        chat_history: Previous messages for context

    Returns:
        Assistant response
    """
    client = get_client()

    system_prompt = f"""You are Airo's Bid Intelligence Assistant for Borouge PLC's procurement team. You have access to the following tender and bid evaluation data:

TENDER DETAILS:
{json.dumps(tender_data, indent=2)}

SUPPLIER EVALUATIONS:
{json.dumps(supplier_evaluations, indent=2)}

EVALUATION CRITERIA AND WEIGHTS:
{json.dumps(criteria, indent=2)}

You can answer any question about the bids, suppliers, evaluation scores, compliance status, risks, comparisons, and recommendations. Always cite specific evidence from the bid documents when answering.

Guidelines:
- Be precise and data-driven in your answers
- When comparing suppliers, use actual scores and evidence
- Flag if information was not found in a supplier's bid
- For compliance questions (HSE, ESG, ISO), clearly state compliant/non-compliant with evidence
- You can suggest adjustments to evaluation criteria weights and show how rankings would change
- Always maintain a professional, procurement-advisor tone
- When uncertain, say so clearly rather than guessing"""

    # Prepare message history
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )

        return message.content[0].text
    except APIError as e:
        raise ValueError(f"Claude API error: {str(e)}")


def generate_sample_tender_data() -> Dict[str, Any]:
    """Generate realistic sample tender data."""
    return {
        "tender_title": "RFQ-2026-BRG-001: Supply and Maintenance of Industrial Control Valves for Borouge Polyolefin Plant, Ruwais, Abu Dhabi",
        "issuing_organization": "Borouge PLC",
        "tender_reference": "RFQ-2026-BRG-001",
        "submission_deadline": "2026-03-30",
        "scope_of_work": "Supply and maintenance of industrial control valves including installation, testing, and after-sales support for a petrochemical polyolefin production facility in Ruwais, UAE.",
        "evaluation_criteria": [
            {
                "criterion": "Technical Capability",
                "weight_percentage": 25,
                "category": "technical",
            },
            {
                "criterion": "Delivery & Logistics",
                "weight_percentage": 15,
                "category": "technical",
            },
            {
                "criterion": "Commercial Terms",
                "weight_percentage": 25,
                "category": "commercial",
            },
            {
                "criterion": "HSE Compliance",
                "weight_percentage": 15,
                "category": "compliance",
            },
            {
                "criterion": "ESG & Sustainability",
                "weight_percentage": 10,
                "category": "compliance",
            },
            {
                "criterion": "Past Performance & References",
                "weight_percentage": 10,
                "category": "technical",
            },
        ],
        "mandatory_requirements": [
            "ISO 9001 certification",
            "HSE policy and documentation",
            "Product warranty minimum 24 months",
            "24/7 after-sales support",
            "Local spares availability",
        ],
        "technical_specifications": [
            "Control valve size range: 1/2 inch to 4 inches",
            "Operating pressure: up to 100 bar",
            "Temperature range: -20°C to 200°C",
            "Materials: Stainless steel (316L) and carbon steel",
            "API 6D/ISO 17292 compliance",
        ],
        "commercial_requirements": [
            "Competitive unit pricing",
            "Flexible payment terms (Net 30/60)",
            "Volume discounts for orders >50 units",
            "Spare parts pricing schedule",
        ],
        "compliance_requirements": [
            "OSHA/UAE labor law compliance",
            "Environmental management certification (ISO 14001 preferred)",
            "Carbon footprint disclosure",
            "ICV (In-Country Value) compliance for UAE",
        ],
        "deliverables": [
            "Product specifications and datasheets",
            "Installation manual and technical documentation",
            "Training for Borouge maintenance team",
            "Spare parts list and availability schedule",
        ],
        "contract_duration": "3 years with 2-year renewal option",
    }


def generate_sample_supplier_evaluations() -> List[Dict[str, Any]]:
    """Generate realistic sample supplier evaluations."""
    return [
        {
            "supplier_name": "ValveTech Industries",
            "supplier_country": "Germany",
            "bid_reference": "VT-BRG-2026-001",
            "overall_score": 87,
            "category_scores": {
                "technical": {
                    "score": 92,
                    "summary": "Excellent technical capability with decades of petrochemical experience.",
                    "strengths": [
                        "ISO 9001, ISO 14001 certified",
                        "Advanced manufacturing facility",
                        "Comprehensive product range",
                    ],
                    "gaps": [],
                },
                "commercial": {
                    "score": 75,
                    "summary": "Competitive pricing but limited volume discounts.",
                    "strengths": [
                        "Clear pricing structure",
                        "Flexible payment terms",
                    ],
                    "gaps": [
                        "No volume discount beyond 10%",
                        "Premium pricing vs competitors",
                    ],
                },
                "compliance": {
                    "score": 92,
                    "summary": "Excellent HSE and ESG compliance.",
                    "strengths": [
                        "Strong HSE record",
                        "Carbon-neutral operations",
                        "Full ISO 14001 certification",
                    ],
                    "gaps": [],
                },
            },
            "criterion_scores": [
                {
                    "criterion": "Technical Capability",
                    "score": 92,
                    "evidence": "30+ years in petrochemical valves, multiple certifications",
                    "flag": "met",
                },
                {
                    "criterion": "Delivery & Logistics",
                    "score": 88,
                    "evidence": "8-week lead time, established UAE distribution",
                    "flag": "met",
                },
                {
                    "criterion": "Commercial Terms",
                    "score": 75,
                    "evidence": "EUR pricing, limited volume discounts",
                    "flag": "partially_met",
                },
                {
                    "criterion": "HSE Compliance",
                    "score": 95,
                    "evidence": "Zero lost-time incidents, OSHA certified",
                    "flag": "met",
                },
                {
                    "criterion": "ESG & Sustainability",
                    "score": 90,
                    "evidence": "Carbon-neutral facility, ISO 14001 certified",
                    "flag": "met",
                },
                {
                    "criterion": "Past Performance & References",
                    "score": 85,
                    "evidence": "5 similar projects in Middle East, positive references",
                    "flag": "met",
                },
            ],
            "mandatory_requirements_status": [
                {
                    "requirement": "ISO 9001 certification",
                    "status": "compliant",
                    "evidence": "Current certification valid until 2027",
                },
                {
                    "requirement": "HSE policy and documentation",
                    "status": "compliant",
                    "evidence": "Comprehensive HSE manual provided",
                },
                {
                    "requirement": "Product warranty minimum 24 months",
                    "status": "compliant",
                    "evidence": "Standard 36-month warranty offered",
                },
                {
                    "requirement": "24/7 after-sales support",
                    "status": "compliant",
                    "evidence": "Regional support center in Dubai",
                },
                {
                    "requirement": "Local spares availability",
                    "status": "compliant",
                    "evidence": "Warehouse in Jebel Ali, 48-hour delivery",
                },
            ],
            "hse_compliance": {
                "status": "compliant",
                "details": "Excellent HSE record with zero major incidents in past 5 years",
            },
            "esg_compliance": {
                "status": "compliant",
                "details": "Certified carbon-neutral operations, 100% renewable energy in manufacturing",
            },
            "iso_certifications": [
                "ISO 9001:2015",
                "ISO 14001:2015",
                "ISO 45001:2018",
                "API Q1",
            ],
            "proposed_price": "€450 per unit (FOB Hamburg)",
            "proposed_timeline": "8 weeks after PO",
            "key_risks": ["Currency fluctuation (EUR)", "Geopolitical tensions"],
            "recommendation": "Highly recommended for quality-first approach",
            "completeness_percentage": 98,
        },
        {
            "supplier_name": "PetroFlow Solutions",
            "supplier_country": "UAE",
            "bid_reference": "PFS-BRG-2026-001",
            "overall_score": 84,
            "category_scores": {
                "technical": {
                    "score": 82,
                    "summary": "Good technical capability with local market knowledge.",
                    "strengths": [
                        "Strong local presence",
                        "Quick response time",
                        "Familiar with Borouge operations",
                    ],
                    "gaps": [
                        "Limited international certifications",
                        "Smaller manufacturing capacity",
                    ],
                },
                "commercial": {
                    "score": 89,
                    "summary": "Excellent commercial terms with competitive pricing.",
                    "strengths": [
                        "AED pricing (local currency advantage)",
                        "Volume discounts up to 15%",
                        "Flexible payment terms (Net 60)",
                    ],
                    "gaps": [],
                },
                "compliance": {
                    "score": 82,
                    "summary": "Good compliance with strong local alignment.",
                    "strengths": [
                        "UAE labour law compliant",
                        "Strong local ICV",
                        "Local spares support",
                    ],
                    "gaps": [
                        "ESG documentation limited",
                        "No international environmental certification",
                    ],
                },
            },
            "criterion_scores": [
                {
                    "criterion": "Technical Capability",
                    "score": 82,
                    "evidence": "15 years local experience, ISO 9001 certified",
                    "flag": "met",
                },
                {
                    "criterion": "Delivery & Logistics",
                    "score": 95,
                    "evidence": "Local stock, 2-week lead time",
                    "flag": "met",
                },
                {
                    "criterion": "Commercial Terms",
                    "score": 89,
                    "evidence": "Competitive AED pricing, best volume discounts",
                    "flag": "met",
                },
                {
                    "criterion": "HSE Compliance",
                    "score": 85,
                    "evidence": "Compliant with UAE safety standards",
                    "flag": "met",
                },
                {
                    "criterion": "ESG & Sustainability",
                    "score": 68,
                    "evidence": "Basic environmental policy, no formal certification",
                    "flag": "partially_met",
                },
                {
                    "criterion": "Past Performance & References",
                    "score": 80,
                    "evidence": "3 similar projects with positive feedback",
                    "flag": "met",
                },
            ],
            "mandatory_requirements_status": [
                {
                    "requirement": "ISO 9001 certification",
                    "status": "compliant",
                    "evidence": "Current certification",
                },
                {
                    "requirement": "HSE policy and documentation",
                    "status": "compliant",
                    "evidence": "Basic HSE documentation provided",
                },
                {
                    "requirement": "Product warranty minimum 24 months",
                    "status": "compliant",
                    "evidence": "24-month warranty standard",
                },
                {
                    "requirement": "24/7 after-sales support",
                    "status": "compliant",
                    "evidence": "Local support team available",
                },
                {
                    "requirement": "Local spares availability",
                    "status": "compliant",
                    "evidence": "Local stock maintained",
                },
            ],
            "hse_compliance": {
                "status": "compliant",
                "details": "Good safety record, compliant with UAE labour law",
            },
            "esg_compliance": {
                "status": "partially",
                "details": "Basic environmental policy but lacks formal certification",
            },
            "iso_certifications": ["ISO 9001:2015"],
            "proposed_price": "AED 1,750 per unit (CIF Dubai)",
            "proposed_timeline": "2 weeks from order (local stock)",
            "key_risks": [
                "Limited manufacturing scale",
                "Dependency on single facility",
            ],
            "recommendation": "Recommended for cost and agility",
            "completeness_percentage": 92,
        },
        {
            "supplier_name": "Shanghai Industrial Valves",
            "supplier_country": "China",
            "bid_reference": "SIV-BRG-2026-001",
            "overall_score": 71,
            "category_scores": {
                "technical": {
                    "score": 75,
                    "summary": "Adequate technical capability with cost-focused approach.",
                    "strengths": [
                        "Large production capacity",
                        "Cost-effective solutions",
                        "API 6D certified",
                    ],
                    "gaps": [
                        "Limited petrochemical-specific experience",
                        "Quality consistency concerns",
                    ],
                },
                "commercial": {
                    "score": 92,
                    "summary": "Best commercial terms with lowest pricing.",
                    "strengths": [
                        "Lowest unit price",
                        "High volume discounts",
                        "Flexible payment options",
                    ],
                    "gaps": [],
                },
                "compliance": {
                    "score": 55,
                    "summary": "Significant compliance gaps in HSE and ESG.",
                    "strengths": [
                        "Basic ISO 9001 certification",
                    ],
                    "gaps": [
                        "Limited ESG documentation",
                        "HSE concerns in bid",
                        "No international environmental cert",
                    ],
                },
            },
            "criterion_scores": [
                {
                    "criterion": "Technical Capability",
                    "score": 75,
                    "evidence": "Large factory but generic valve experience",
                    "flag": "partially_met",
                },
                {
                    "criterion": "Delivery & Logistics",
                    "score": 70,
                    "evidence": "12-14 week lead time, shipping complex",
                    "flag": "partially_met",
                },
                {
                    "criterion": "Commercial Terms",
                    "score": 92,
                    "evidence": "USD 280/unit, best volume discounts available",
                    "flag": "met",
                },
                {
                    "criterion": "HSE Compliance",
                    "score": 60,
                    "evidence": "Limited HSE documentation, concerns noted",
                    "flag": "partially_met",
                },
                {
                    "criterion": "ESG & Sustainability",
                    "score": 45,
                    "evidence": "No formal ESG commitment or certification",
                    "flag": "not_met",
                },
                {
                    "criterion": "Past Performance & References",
                    "score": 70,
                    "evidence": "Generic industrial references, limited petrochemical",
                    "flag": "partially_met",
                },
            ],
            "mandatory_requirements_status": [
                {
                    "requirement": "ISO 9001 certification",
                    "status": "compliant",
                    "evidence": "Current certification",
                },
                {
                    "requirement": "HSE policy and documentation",
                    "status": "non_compliant",
                    "evidence": "Minimal HSE documentation provided",
                },
                {
                    "requirement": "Product warranty minimum 24 months",
                    "status": "compliant",
                    "evidence": "24-month warranty offered",
                },
                {
                    "requirement": "24/7 after-sales support",
                    "status": "unclear",
                    "evidence": "Support structure unclear, language barriers potential",
                },
                {
                    "requirement": "Local spares availability",
                    "status": "non_compliant",
                    "evidence": "No local stock, long lead times for spares",
                },
            ],
            "hse_compliance": {
                "status": "partially",
                "details": "Limited HSE documentation, concerns about safety culture",
            },
            "esg_compliance": {
                "status": "non_compliant",
                "details": "No formal ESG policy or environmental commitment",
            },
            "iso_certifications": ["ISO 9001:2015"],
            "proposed_price": "USD 280 per unit (FOB Shanghai)",
            "proposed_timeline": "12-14 weeks lead time",
            "key_risks": [
                "Quality inconsistency",
                "Long supply chain",
                "Language/support barriers",
                "Limited after-sales support",
            ],
            "recommendation": "Not recommended due to compliance gaps",
            "completeness_percentage": 78,
        },
        {
            "supplier_name": "Flowserve Middle East",
            "supplier_country": "USA/UAE",
            "bid_reference": "FSM-BRG-2026-001",
            "overall_score": 86,
            "category_scores": {
                "technical": {
                    "score": 94,
                    "summary": "Excellent technical capability from global leader.",
                    "strengths": [
                        "Global brand recognition",
                        "Extensive R&D",
                        "Premium quality assurance",
                        "Comprehensive certifications",
                    ],
                    "gaps": [],
                },
                "commercial": {
                    "score": 70,
                    "summary": "Premium pricing limits value proposition.",
                    "strengths": [
                        "Global financing options",
                        "Flexible contract terms",
                    ],
                    "gaps": [
                        "Highest unit price",
                        "Limited volume discounts",
                    ],
                },
                "compliance": {
                    "score": 88,
                    "summary": "Strong HSE and ESG compliance.",
                    "strengths": [
                        "Multiple certifications",
                        "Strong ESG commitment",
                        "Excellent safety record",
                    ],
                    "gaps": [],
                },
            },
            "criterion_scores": [
                {
                    "criterion": "Technical Capability",
                    "score": 94,
                    "evidence": "Global leader, extensive petrochemical experience",
                    "flag": "met",
                },
                {
                    "criterion": "Delivery & Logistics",
                    "score": 85,
                    "evidence": "Established UAE operations, 6-week lead time",
                    "flag": "met",
                },
                {
                    "criterion": "Commercial Terms",
                    "score": 70,
                    "evidence": "USD 520/unit, premium pricing",
                    "flag": "partially_met",
                },
                {
                    "criterion": "HSE Compliance",
                    "score": 93,
                    "evidence": "Excellent safety record, multiple certifications",
                    "flag": "met",
                },
                {
                    "criterion": "ESG & Sustainability",
                    "score": 88,
                    "evidence": "ISO 14001 certified, strong ESG commitment",
                    "flag": "met",
                },
                {
                    "criterion": "Past Performance & References",
                    "score": 82,
                    "evidence": "15+ petrochemical projects in region",
                    "flag": "met",
                },
            ],
            "mandatory_requirements_status": [
                {
                    "requirement": "ISO 9001 certification",
                    "status": "compliant",
                    "evidence": "Multiple facility certifications",
                },
                {
                    "requirement": "HSE policy and documentation",
                    "status": "compliant",
                    "evidence": "Comprehensive HSE program",
                },
                {
                    "requirement": "Product warranty minimum 24 months",
                    "status": "compliant",
                    "evidence": "36-month warranty standard",
                },
                {
                    "requirement": "24/7 after-sales support",
                    "status": "compliant",
                    "evidence": "Global support network with UAE presence",
                },
                {
                    "requirement": "Local spares availability",
                    "status": "compliant",
                    "evidence": "Regional distribution center",
                },
            ],
            "hse_compliance": {
                "status": "compliant",
                "details": "Excellent safety record, OSHA certified facilities",
            },
            "esg_compliance": {
                "status": "compliant",
                "details": "Strong ESG program, carbon-neutral operations target",
            },
            "iso_certifications": [
                "ISO 9001:2015",
                "ISO 14001:2015",
                "ISO 45001:2018",
                "API Q1",
            ],
            "proposed_price": "USD 520 per unit (CIF Abu Dhabi)",
            "proposed_timeline": "6 weeks from PO",
            "key_risks": ["Premium cost", "Overspecification for needs"],
            "recommendation": "Recommended for mission-critical quality",
            "completeness_percentage": 95,
        },
        {
            "supplier_name": "Al Mansoori Valve Systems",
            "supplier_country": "UAE",
            "bid_reference": "AMVS-BRG-2026-001",
            "overall_score": 79,
            "category_scores": {
                "technical": {
                    "score": 78,
                    "summary": "Good technical capability with local specialization.",
                    "strengths": [
                        "Local manufacturing",
                        "Customization capability",
                        "Quick adaptation",
                    ],
                    "gaps": [
                        "Limited international experience",
                        "Smaller technical team",
                    ],
                },
                "commercial": {
                    "score": 85,
                    "summary": "Good commercial terms with local advantage.",
                    "strengths": [
                        "Competitive AED pricing",
                        "Volume discounts",
                        "Flexible terms for local supplier",
                    ],
                    "gaps": [],
                },
                "compliance": {
                    "score": 78,
                    "summary": "Adequate HSE compliance, developing ESG.",
                    "strengths": [
                        "UAE labour law compliant",
                        "Local stakeholder",
                        "Good ICV score",
                    ],
                    "gaps": [
                        "Limited ESG certification",
                        "No international environmental cert",
                    ],
                },
            },
            "criterion_scores": [
                {
                    "criterion": "Technical Capability",
                    "score": 78,
                    "evidence": "Local manufacturing, 12 years experience",
                    "flag": "met",
                },
                {
                    "criterion": "Delivery & Logistics",
                    "score": 92,
                    "evidence": "Local production, 1-2 week lead time",
                    "flag": "met",
                },
                {
                    "criterion": "Commercial Terms",
                    "score": 85,
                    "evidence": "AED 1,600/unit with volume discounts",
                    "flag": "met",
                },
                {
                    "criterion": "HSE Compliance",
                    "score": 80,
                    "evidence": "Compliant with UAE standards",
                    "flag": "met",
                },
                {
                    "criterion": "ESG & Sustainability",
                    "score": 70,
                    "evidence": "Developing ESG policy, no formal certification yet",
                    "flag": "partially_met",
                },
                {
                    "criterion": "Past Performance & References",
                    "score": 75,
                    "evidence": "2 major local projects, limited international references",
                    "flag": "partially_met",
                },
            ],
            "mandatory_requirements_status": [
                {
                    "requirement": "ISO 9001 certification",
                    "status": "compliant",
                    "evidence": "Current certification",
                },
                {
                    "requirement": "HSE policy and documentation",
                    "status": "compliant",
                    "evidence": "Basic HSE documentation",
                },
                {
                    "requirement": "Product warranty minimum 24 months",
                    "status": "compliant",
                    "evidence": "24-month warranty offered",
                },
                {
                    "requirement": "24/7 after-sales support",
                    "status": "compliant",
                    "evidence": "Local support team",
                },
                {
                    "requirement": "Local spares availability",
                    "status": "compliant",
                    "evidence": "Local manufacturing supports spares",
                },
            ],
            "hse_compliance": {
                "status": "compliant",
                "details": "Good safety record, fully compliant with UAE labour law",
            },
            "esg_compliance": {
                "status": "partially",
                "details": "Developing ESG commitment but no formal certification",
            },
            "iso_certifications": ["ISO 9001:2015"],
            "proposed_price": "AED 1,600 per unit (Local)",
            "proposed_timeline": "1-2 weeks lead time",
            "key_risks": [
                "Limited international track record",
                "Smaller manufacturing scale",
            ],
            "recommendation": "Recommended for local partnership and agility",
            "completeness_percentage": 88,
        },
    ]
