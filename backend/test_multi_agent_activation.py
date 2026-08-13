"""Test script for debugging multi-agent activation in isolation."""

import os
import asyncio
import sys

# Set environment variables for testing
os.environ["ENABLE_MULTI_AGENT"] = "true"
os.environ["AGENT_FALLBACK_TO_RULES"] = "true"

# Test 1: Check environment variable parsing
print("=== Test 1: Environment Variable Parsing ===")
enable_multi_agent = os.getenv("ENABLE_MULTI_AGENT", "true").lower() == "true"
fallback_to_rules = os.getenv("AGENT_FALLBACK_TO_RULES", "true").lower() == "true"
print(f"ENABLE_MULTI_AGENT: {enable_multi_agent}")
print(f"AGENT_FALLBACK_TO_RULES: {fallback_to_rules}")

# Test 2: Check API key availability
print("\n=== Test 2: API Key Availability ===")
api_keys = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
}
for key, value in api_keys.items():
    status = "✓ Available" if value else "✗ Not set"
    print(f"{key}: {status}")

# Test 3: Try to initialize multi-agent system
print("\n=== Test 3: Multi-Agent System Initialization ===")
try:
    from app.ai_services.integration import get_multi_agent_system
    
    system = get_multi_agent_system()
    print(f"Multi-agent system available: {system.available}")
    print(f"Multi-agent system enabled: {system.enabled}")
    print(f"Fallback to rules: {system.fallback_to_rules}")
    
    if hasattr(system, 'ai_service') and system.ai_service:
        print(f"AI Service providers: {list(system.ai_service.providers.keys())}")
        print(f"Provider priority: {system.ai_service.provider_priority}")
    else:
        print("AI Service not initialized (no API keys available)")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Multi-agent system module not available")
except Exception as e:
    print(f"✗ Initialization error: {e}")

# Test 4: Test rule-based fallback
print("\n=== Test 4: Rule-Based Fallback ===")
try:
    from app.comprehensive_analysis import _generate_rule_based_analysis
    print("✓ Rule-based analysis module imported successfully")
    
    # Create mock data for testing
    class MockDoc:
        def __init__(self):
            self.abstract = "Test abstract for materials science research"
            self.methodology = "Experimental methodology with validation"
            self.claims_outcomes = "Key results and outcomes"
            self.raw_text = "Full document text"
            self.document_type = "research_paper"
    
    mock_doc = MockDoc()
    mock_classification = {"sector_name": "Deep Tech", "ipc_primary": "C01B", "novelty_score": 0.7}
    mock_originality = {"max_cosine_similarity": 0.3, "originality_premium_s": 0.8, "top_matches": []}
    mock_fto = {"risk_tier_pct": 25, "expert_consultation_required": False}
    mock_valuation = {"v_target_usd": 5000000, "market_potential": "High"}
    mock_trl = {"trl": 4, "confidence": 0.75}
    mock_market = {"working_field": "Energy Storage", "total_opportunities": 5}
    mock_nlp = {"sentiment": "positive", "key_topics": ["materials", "energy"]}
    
    result = _generate_rule_based_analysis(
        mock_doc, mock_classification, mock_originality, mock_fto,
        mock_valuation, mock_trl, mock_market, mock_nlp
    )
    
    print(f"✓ Rule-based analysis generated successfully")
    print(f"Generated sections: {list(result.keys())}")
    print(f"Executive summary length: {len(result.get('executive_summary', ''))} chars")
    
except Exception as e:
    print(f"✗ Rule-based fallback error: {e}")

# Test 5: Test with use_multi_agent=False explicitly
async def test_use_multi_agent_false():
    print("\n=== Test 5: Explicit use_multi_agent=False ===")
    try:
        from app.comprehensive_analysis import generate_comprehensive_analysis
        
        # Test with use_multi_agent=False
        result = await generate_comprehensive_analysis(
            doc=mock_doc,
            classification=mock_classification,
            originality=mock_originality,
            fto=mock_fto,
            valuation=mock_valuation,
            trl_evaluation=mock_trl,
            market_mapping=mock_market,
            nlp_analysis=mock_nlp,
            title="Test Document",
            use_multi_agent=False,
        )
        
        print(f"✓ Analysis completed with use_multi_agent=False")
        print(f"System used: {result.get('ai_analysis_metadata', {}).get('system_used', 'unknown')}")
        
    except Exception as e:
        print(f"✗ Analysis error: {e}")

# Run async test
asyncio.run(test_use_multi_agent_false())

print("\n=== Test Summary ===")
print("Multi-agent activation debugging complete")
print("Check results above to identify any issues with multi-agent system initialization")
