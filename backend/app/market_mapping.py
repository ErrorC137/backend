"""Market mapping analysis for identifying potential market opportunities."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass


@dataclass
class MarketOpportunity:
    """Represents a potential market opportunity."""
    market_name: str
    market_size: str  # e.g., "$50B by 2030"
    growth_rate: str  # e.g., "12% CAGR"
    fit_score: float  # 0-100 based on technology alignment
    entry_difficulty: str  # "Low", "Medium", "High"
    key_competitors: list[str]
    accuracy_score: float  # 0-100 based on development stage


# Market database organized by technology categories
MARKET_DATABASE = {
    "Energy Storage": [
        {
            "market_name": "Electric Vehicle Batteries",
            "market_size": "$120B by 2030",
            "growth_rate": "15% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["CATL", "LG Energy Solution", "Panasonic", "Tesla"],
        },
        {
            "market_name": "Grid Energy Storage",
            "market_size": "$25B by 2030",
            "growth_rate": "20% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Fluence", "Tesla Energy", "BYD", "Samsung SDI"],
        },
        {
            "market_name": "Consumer Electronics",
            "market_size": "$35B by 2030",
            "growth_rate": "8% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Samsung", "Apple", "Sony", "Panasonic"],
        },
        {
            "market_name": "Aerospace & Defense",
            "market_size": "$8B by 2030",
            "growth_rate": "10% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Boeing", "Lockheed Martin", "Airbus", "Saft"],
        },
    ],
    "Nanomaterials": [
        {
            "market_name": "Electronics & Semiconductors",
            "market_size": "$45B by 2030",
            "growth_rate": "12% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Intel", "Samsung", "TSMC", "Applied Materials"],
        },
        {
            "market_name": "Coatings & Paints",
            "market_size": "$15B by 2030",
            "growth_rate": "6% CAGR",
            "entry_difficulty": "Low",
            "key_competitors": ["PPG", "Sherwin-Williams", "AkzoNobel", "BASF"],
        },
        {
            "market_name": "Medical Devices",
            "market_size": "$20B by 2030",
            "growth_rate": "9% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Medtronic", "Johnson & Johnson", "Abbott", "Boston Scientific"],
        },
        {
            "market_name": "Automotive Components",
            "market_size": "$30B by 2030",
            "growth_rate": "11% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Bosch", "Continental", "Denso", "Magna"],
        },
    ],
    "Biomaterials": [
        {
            "market_name": "Medical Implants",
            "market_size": "$40B by 2030",
            "growth_rate": "10% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Zimmer Biomet", "Stryker", "Johnson & Johnson", "Medtronic"],
        },
        {
            "market_name": "Tissue Engineering",
            "market_size": "$12B by 2030",
            "growth_rate": "18% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Organovo", "Tissue Regeneration Systems", "Baxter", "Fujifilm"],
        },
        {
            "market_name": "Drug Delivery Systems",
            "market_size": "$25B by 2030",
            "growth_rate": "8% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Pfizer", "Novartis", "Roche", "Merck"],
        },
    ],
    "Polymers": [
        {
            "market_name": "Packaging",
            "market_size": "$35B by 2030",
            "growth_rate": "5% CAGR",
            "entry_difficulty": "Low",
            "key_competitors": ["Amcor", "Sealed Air", "Berry Global", "Sonoco"],
        },
        {
            "market_name": "Automotive",
            "market_size": "$45B by 2030",
            "growth_rate": "7% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["BASF", "Dow", "SABIC", "LyondellBasell"],
        },
        {
            "market_name": "Construction",
            "market_size": "$30B by 2030",
            "growth_rate": "6% CAGR",
            "entry_difficulty": "Low",
            "key_competitors": ["Dow", "BASF", "Sika", "PPG"],
        },
    ],
    "Ceramics": [
        {
            "market_name": "Electronics",
            "market_size": "$20B by 2030",
            "growth_rate": "9% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Kyocera", "Murata", "TDK", "Coorstek"],
        },
        {
            "market_name": "Aerospace",
            "market_size": "$8B by 2030",
            "growth_rate": "11% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Coorstek", "CeramTec", "Morgan Advanced Materials", "Kyocera"],
        },
        {
            "market_name": "Medical",
            "market_size": "$15B by 2030",
            "growth_rate": "10% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Coorstek", "CeramTec", "3M", "Saint-Gobain"],
        },
    ],
    "Composites": [
        {
            "market_name": "Aerospace",
            "market_size": "$25B by 2030",
            "growth_rate": "12% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Hexcel", "Solvay", "Toray", "Teijin"],
        },
        {
            "market_name": "Automotive",
            "market_size": "$20B by 2030",
            "growth_rate": "14% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Solvay", "Toray", "Mitsubishi Chemical", "Teijin"],
        },
        {
            "market_name": "Wind Energy",
            "market_size": "$12B by 2030",
            "growth_rate": "15% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Owens Corning", "SGL Carbon", "Toray", "Mitsubishi Chemical"],
        },
    ],
    "Metals & Alloys": [
        {
            "market_name": "Aerospace",
            "market_size": "$30B by 2030",
            "growth_rate": "8% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Alcoa", "Constellium", "Nucor", "ArcelorMittal"],
        },
        {
            "market_name": "Automotive",
            "market_size": "$40B by 2030",
            "growth_rate": "7% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Nucor", "ArcelorMittal", "ThyssenKrupp", "POSCO"],
        },
        {
            "market_name": "Construction",
            "market_size": "$50B by 2030",
            "growth_rate": "5% CAGR",
            "entry_difficulty": "Low",
            "key_competitors": ["ArcelorMittal", "Nucor", "Tata Steel", "Baosteel"],
        },
    ],
    "Semiconductors": [
        {
            "market_name": "Consumer Electronics",
            "market_size": "$80B by 2030",
            "growth_rate": "10% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Intel", "Samsung", "TSMC", "NVIDIA"],
        },
        {
            "market_name": "Automotive",
            "market_size": "$25B by 2030",
            "growth_rate": "15% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["Infineon", "NXP", "STMicroelectronics", "Renesas"],
        },
        {
            "market_name": "Industrial",
            "market_size": "$20B by 2030",
            "growth_rate": "8% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["Texas Instruments", "Analog Devices", "Infineon", "STMicroelectronics"],
        },
    ],
    "Catalysis": [
        {
            "market_name": "Chemical Industry",
            "market_size": "$35B by 2030",
            "growth_rate": "6% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["BASF", "Dow", "Clariant", "Johnson Matthey"],
        },
        {
            "market_name": "Petroleum Refining",
            "market_size": "$20B by 2030",
            "growth_rate": "4% CAGR",
            "entry_difficulty": "High",
            "key_competitors": ["BASF", "Clariant", "Haldor Topsoe", "Johnson Matthey"],
        },
        {
            "market_name": "Environmental",
            "market_size": "$15B by 2030",
            "growth_rate": "12% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["BASF", "Clariant", "Johnson Matthey", "UOP"],
        },
    ],
    "Photovoltaics": [
        {
            "market_name": "Utility-Scale Solar",
            "market_size": "$60B by 2030",
            "growth_rate": "18% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["First Solar", "JinkoSolar", "Trina Solar", "LONGi"],
        },
        {
            "market_name": "Residential Solar",
            "market_size": "$25B by 2030",
            "growth_rate": "15% CAGR",
            "entry_difficulty": "Low",
            "key_competitors": ["SunPower", "Tesla", "LG", "Hanwha Q CELLS"],
        },
        {
            "market_name": "Building Integration",
            "market_size": "$10B by 2030",
            "growth_rate": "20% CAGR",
            "entry_difficulty": "Medium",
            "key_competitors": ["SunPower", "Tesla", "Hanwha Q CELLS", "Trina Solar"],
        },
    ],
}


def calculate_accuracy_score(trl: int, document_type: str) -> float:
    """
    Calculate accuracy score based on development stage.
    
    Higher TRL and more developed products = higher accuracy.
    Paper-only research = lower accuracy.
    
    Args:
        trl: Technology Readiness Level (1-9)
        document_type: Type of document (paper, patent, technical report, etc.)
    
    Returns:
        Accuracy score as percentage (0-100)
    """
    # Base score from TRL
    trl_score = (trl / 9) * 50  # TRL contributes up to 50 points
    
    # Bonus for document type
    doc_type_bonus = 0
    if document_type.lower() in ["patent", "patent_application"]:
        doc_type_bonus = 30  # Patents are more concrete
    elif document_type.lower() in ["technical_report", "product_specification"]:
        doc_type_bonus = 25
    elif document_type.lower() in ["preprint", "conference_paper"]:
        doc_type_bonus = 15
    elif document_type.lower() in ["journal_paper", "article"]:
        doc_type_bonus = 10
    
    # Bonus for high TRL (TRL 7+ indicates prototype/demo)
    if trl >= 7:
        doc_type_bonus += 20
    
    # Cap at 100
    accuracy = min(trl_score + doc_type_bonus, 100)
    
    # Minimum of 20% (even early research has some market insight)
    return max(accuracy, 20)


def calculate_fit_score(analysis_text: str, market_keywords: list[str]) -> float:
    """
    Calculate fit score based on keyword matching in the analysis text.
    
    Args:
        analysis_text: The document text to analyze
        market_keywords: Keywords relevant to the market
    
    Returns:
        Fit score as percentage (0-100)
    """
    text_lower = analysis_text.lower()
    matches = sum(1 for keyword in market_keywords if keyword.lower() in text_lower)
    
    # Normalize based on number of keywords
    if not market_keywords:
        return 50  # Default moderate fit
    
    match_ratio = matches / len(market_keywords)
    return min(match_ratio * 100 + 30, 100)  # Base 30% + match bonus


def analyze_market_mapping(
    analysis_text: str,
    classification: dict[str, Any],
    trl: int,
    document_type: str,
) -> dict[str, Any]:
    """
    Analyze potential market opportunities for a technology.
    
    Args:
        analysis_text: The document text to analyze
        classification: IPC classification results
        trl: Technology Readiness Level
        document_type: Type of document
    
    Returns:
        Dictionary with market mapping analysis results
    """
    # Get the working field from classification or infer from IPC
    working_field = classification.get("working_field", classification.get("ipc_primary", "General"))
    
    # Map IPC to working field if needed
    ipc_to_field = {
        "H01M": "Energy Storage",
        "C01B": "Nanomaterials",
        "A61L": "Biomaterials",
        "C08": "Polymers",
        "C04": "Ceramics",
        "B32B": "Composites",
        "C22": "Metals & Alloys",
        "H01L": "Semiconductors",
        "B01J": "Catalysis",
        "H02S": "Photovoltaics",
    }
    
    # Try to find matching field
    matched_field = None
    for ipc_prefix, field in ipc_to_field.items():
        if classification.get("ipc_primary", "").startswith(ipc_prefix):
            matched_field = field
            break
    
    if not matched_field:
        matched_field = working_field
    
    # Get markets for this field
    markets = MARKET_DATABASE.get(matched_field, MARKET_DATABASE.get("Energy Storage", []))
    
    # Calculate overall accuracy score
    accuracy_score = calculate_accuracy_score(trl, document_type)
    
    # Analyze each market opportunity
    opportunities = []
    for market in markets:
        # Simple keyword matching for fit score
        # In production, this would use more sophisticated NLP
        keywords = [
            market["market_name"].lower().replace(" ", ""),
            "market",
            "application",
            "commercial",
            "industry",
        ]
        
        fit_score = calculate_fit_score(analysis_text, keywords)
        
        # Adjust fit score based on TRL (higher TRL = better fit for established markets)
        if trl >= 6:
            fit_score = min(fit_score + 10, 100)
        
        opportunity = MarketOpportunity(
            market_name=market["market_name"],
            market_size=market["market_size"],
            growth_rate=market["growth_rate"],
            fit_score=fit_score,
            entry_difficulty=market["entry_difficulty"],
            key_competitors=market["key_competitors"],
            accuracy_score=accuracy_score,
        )
        opportunities.append(opportunity)
    
    # Sort by fit score
    opportunities.sort(key=lambda x: x.fit_score, reverse=True)
    
    return {
        "working_field": matched_field,
        "overall_accuracy_score": accuracy_score,
        "accuracy_factors": {
            "trl_contribution": (trl / 9) * 50,
            "document_type_bonus": accuracy_score - (trl / 9) * 50,
            "trl_level": trl,
            "document_type": document_type,
        },
        "market_opportunities": [
            {
                "market_name": opp.market_name,
                "market_size": opp.market_size,
                "growth_rate": opp.growth_rate,
                "fit_score": opp.fit_score,
                "entry_difficulty": opp.entry_difficulty,
                "key_competitors": opp.key_competitors,
                "accuracy_score": opp.accuracy_score,
            }
            for opp in opportunities
        ],
        "total_opportunities": len(opportunities),
        "top_opportunity": opportunities[0].market_name if opportunities else None,
    }
