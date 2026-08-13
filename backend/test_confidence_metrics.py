"""Test confidence metrics calculation."""

from app.pipeline import _calculate_originality_confidence, _calculate_valuation_confidence, _calculate_fto_confidence

class MockDoc:
    def __init__(self):
        self.abstract = "Test abstract for materials science research with comprehensive content"
        self.methodology = "Detailed experimental methodology with multiple validation steps and comprehensive analysis"
        self.claims_outcomes = "Key results and outcomes with statistical significance"
        self.raw_text = "Full document text with comprehensive content covering all aspects of the research"
        self.document_type = "research_paper"
        self.parsing_confidence = 0.85

# Test originality confidence
print("=== Testing Originality Confidence ===")
originality_data = {
    "max_cosine_similarity": 0.3,
    "originality_premium_s": 0.8,
    "embedding_model": "openai",
    "patent_corpus_size": 1500,
    "top_matches": [
        {"patent_id": "US12345", "title": "Similar Patent", "cosine_similarity": 0.3}
    ],
    "similarity_method": "embedding"
}

doc = MockDoc()
originality_confidence = _calculate_originality_confidence(originality_data, doc)
print(f"Originality Confidence Score: {originality_confidence['score']:.2f}")
print(f"Confidence Level: {originality_confidence['level']}")
print(f"Factors: {originality_confidence['factors']}")

# Test FTO confidence
print("\n=== Testing FTO Confidence ===")
fto_data = {
    "risk_tier_pct": 25,
    "expert_consultation_required": False,
    "r_fto": 0.75
}

fto_confidence = _calculate_fto_confidence(fto_data, originality_data, doc)
print(f"FTO Confidence Score: {fto_confidence['score']:.2f}")
print(f"Confidence Level: {fto_confidence['level']}")
print(f"Factors: {fto_confidence['factors']}")

# Test valuation confidence
print("\n=== Testing Valuation Confidence ===")
valuation_data = {
    "v_baseline_usd": 4000000,
    "v_target_usd": 5000000,
    "market_potential": "High",
    "investment_attractiveness": "Strong"
}

trl_evaluation = {
    "trl": 5,
    "confidence": 0.8
}

valuation_confidence = _calculate_valuation_confidence(valuation_data, trl_evaluation, doc)
print(f"Valuation Confidence Score: {valuation_confidence['score']:.2f}")
print(f"Confidence Level: {valuation_confidence['level']}")
print(f"Factors: {valuation_confidence['factors']}")

# Test overall confidence
print("\n=== Overall Confidence ===")
overall_confidence = (originality_confidence["score"] + fto_confidence["score"] + valuation_confidence["score"]) / 3
print(f"Overall Confidence Score: {overall_confidence:.2f}")

if overall_confidence >= 0.8:
    print("Overall Confidence Level: HIGH")
elif overall_confidence >= 0.6:
    print("Overall Confidence Level: MEDIUM")
else:
    print("Overall Confidence Level: LOW")

print("\n=== All confidence metrics tests completed successfully ===")
