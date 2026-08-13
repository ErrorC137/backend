"""Golden test set execution and validation for MatDAO IP Engine."""

import asyncio
import sys
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class TestCase:
    """Test case definition."""
    name: str
    document_type: str
    abstract: str
    methodology: str
    claims_outcomes: str
    expected_trl_range: tuple[int, int]
    expected_sector: str
    expected_originality_range: tuple[float, float]
    expected_valuation_range: tuple[float, float]

# Golden test cases
TEST_CASES = [
    TestCase(
        name="Graphene Battery Research",
        document_type="research_paper",
        abstract="We present a novel graphene-based supercapacitor with enhanced energy density and rapid charging capabilities. Our methodology combines chemical vapor deposition graphene synthesis with advanced electrolyte formulation to achieve specific energy density of 25 Wh/kg and power density of 10 kW/kg. Experimental validation demonstrates 95% capacity retention after 10,000 charge-discharge cycles. The technology shows potential for electric vehicle and grid storage applications with significant performance improvements over conventional lithium-ion batteries.",
        methodology="Chemical vapor deposition graphene synthesis with advanced electrolyte formulation. Experimental validation includes charge-discharge cycling testing and performance characterization.",
        claims_outcomes="Achieved specific energy density of 25 Wh/kg and power density of 10 kW/kg with 95% capacity retention after 10,000 cycles.",
        expected_trl_range=(4, 5),
        expected_sector="Energy Storage",
        expected_originality_range=(0.0, 0.4),
        expected_valuation_range=(2_000_000, 5_000_000),
    ),
    TestCase(
        name="Perovskite Solar Cells",
        document_type="preprint",
        abstract="This work demonstrates mixed-dimensional perovskite heterostructures for enhanced stability in photovoltaic applications. Our approach combines 2D perovskite passivation layers with 3D perovskite bulk to achieve power conversion efficiency of 24.2% under AM1.5G illumination. Stability testing shows 90% efficiency retention after 1000 hours at 85°C. The methodology involves solution processing with controlled crystallization kinetics. Results indicate potential for commercial solar cell manufacturing with improved environmental stability compared to conventional perovskite devices.",
        methodology="Solution processing with controlled crystallization kinetics for mixed-dimensional perovskite heterostructures. Stability testing at elevated temperatures.",
        claims_outcomes="Power conversion efficiency of 24.2% with 90% efficiency retention after 1000 hours at 85°C.",
        expected_trl_range=(3, 4),
        expected_sector="Energy Storage",
        expected_originality_range=(0.4, 0.6),
        expected_valuation_range=(1_000_000, 3_000_000),
    ),
    TestCase(
        name="CRISPR Gene Editing",
        document_type="published_paper",
        abstract="We report a novel CRISPR-Cas9 variant with enhanced specificity and reduced off-target effects for therapeutic gene editing applications. Our engineered Cas9 protein incorporates amino acid modifications that improve DNA recognition accuracy while maintaining high editing efficiency. In vitro validation in human cell lines demonstrates 85% editing efficiency with off-target events below 0.1%. In vivo testing in mouse models shows successful gene correction with minimal immune response. The technology shows potential for treating genetic disorders with improved safety profiles compared to wild-type CRISPR systems.",
        methodology="Protein engineering of Cas9 with amino acid modifications. In vitro validation in human cell lines and in vivo testing in mouse models.",
        claims_outcomes="85% editing efficiency with off-target events below 0.1% in human cell lines. Successful gene correction in mouse models with minimal immune response.",
        expected_trl_range=(5, 6),
        expected_sector="Biotechnology",
        expected_originality_range=(0.0, 0.4),
        expected_valuation_range=(5_000_000, 10_000_000),
    ),
    TestCase(
        name="Carbon Capture Materials",
        document_type="technical_report",
        abstract="This report describes metal-organic framework (MOF) materials optimized for carbon dioxide capture from industrial flue gas streams. Our synthesis approach produces MOFs with high surface area (2000 m²/g) and selective CO₂ adsorption capacity of 3.5 mmol/g at 1 bar and 25°C. Testing with simulated flue gas shows 90% CO₂ capture efficiency with good cyclic stability over 100 adsorption-desorption cycles. The materials demonstrate potential for industrial carbon capture applications with improved energy efficiency compared to conventional amine-based systems.",
        methodology="MOF synthesis with controlled pore structure. Adsorption testing with simulated flue gas and cyclic stability testing.",
        claims_outcomes="High surface area (2000 m²/g) with selective CO₂ adsorption capacity of 3.5 mmol/g. 90% CO₂ capture efficiency with good cyclic stability.",
        expected_trl_range=(3, 4),
        expected_sector="Carbon Capture",
        expected_originality_range=(0.4, 0.6),
        expected_valuation_range=(1_500_000, 4_000_000),
    ),
    TestCase(
        name="Quantum Dot Displays",
        document_type="research_paper",
        abstract="We present cadmium-free quantum dot materials for next-generation display applications. Our synthesis produces InP-based quantum dots with narrow emission spectra (FWHM 35 nm) and high quantum yield (>80%). Device fabrication demonstrates display panels with wide color gamut (110% NTSC) and improved stability compared to conventional CdSe quantum dots. The manufacturing process uses solution processing compatible with roll-to-roll production. Results indicate potential for commercial display applications with environmental benefits and regulatory advantages over cadmium-based alternatives.",
        methodology="InP-based quantum dot synthesis with solution processing. Device fabrication for display panels with roll-to-roll compatibility.",
        claims_outcomes="Narrow emission spectra (FWHM 35 nm) with high quantum yield (>80%). Display panels with 110% NTSC color gamut and improved stability.",
        expected_trl_range=(4, 5),
        expected_sector="Advanced Materials",
        expected_originality_range=(0.0, 0.4),
        expected_valuation_range=(3_000_000, 7_000_000),
    ),
]


class MockDoc:
    """Mock document object for testing."""
    def __init__(self, test_case: TestCase):
        self.abstract = test_case.abstract
        self.methodology = test_case.methodology
        self.claims_outcomes = test_case.claims_outcomes
        self.raw_text = f"{test_case.abstract} {test_case.methodology} {test_case.claims_outcomes}"
        self.document_type = test_case.document_type


def validate_analysis(
    result: Dict[str, Any],
    test_case: TestCase,
) -> Dict[str, Any]:
    """Validate analysis output against expected characteristics."""
    validation = {
        "test_case": test_case.name,
        "passed": True,
        "failures": [],
    }
    
    # Check that all expected sections are present
    expected_sections = [
        "executive_summary",
        "technical_analysis",
        "market_analysis",
        "ip_competitive_analysis",
        "development_roadmap",
        "risk_assessment",
        "strategic_recommendations",
        "investment_thesis",
    ]
    
    for section in expected_sections:
        if section not in result:
            validation["failures"].append(f"Missing section: {section}")
            validation["passed"] = False
    
    # Validate executive summary length
    exec_summary = result.get("executive_summary", "")
    if len(exec_summary) < 2000 or len(exec_summary) > 4000:
        validation["failures"].append(
            f"Executive summary length {len(exec_summary)} outside expected range 2000-4000"
        )
        validation["passed"] = False
    
    # Check that executive summary mentions relevant keywords
    if "energy storage" in test_case.name.lower() or "solar" in test_case.name.lower():
        if "energy" not in exec_summary.lower():
            validation["failures"].append("Executive summary missing energy-related content")
            validation["passed"] = False
    
    if "gene editing" in test_case.name.lower():
        if "therapeutic" not in exec_summary.lower():
            validation["failures"].append("Executive summary missing therapeutic content")
            validation["passed"] = False
    
    if "carbon capture" in test_case.name.lower():
        if "carbon" not in exec_summary.lower():
            validation["failures"].append("Executive summary missing carbon-related content")
            validation["passed"] = False
    
    if "quantum dot" in test_case.name.lower():
        if "display" not in exec_summary.lower():
            validation["failures"].append("Executive summary missing display-related content")
            validation["passed"] = False
    
    return validation


async def run_test_case(test_case: TestCase) -> Dict[str, Any]:
    """Run a single test case."""
    print(f"\n{'='*60}")
    print(f"Running test case: {test_case.name}")
    print(f"{'='*60}")
    
    try:
        from app.comprehensive_analysis import generate_comprehensive_analysis
        from app.classifier import classify_document
        from app.originality import compute_originality
        from app.fto import analyze_fto
        from app.valuation import calculate_valuation
        from app.trl import evaluate_trl
        from app.market_mapping import analyze_market_mapping
        from app.nlp_analysis import nlp_analyzer
        
        # Create mock document
        doc = MockDoc(test_case)
        analysis_text = f"{doc.abstract}\n{doc.methodology}\n{doc.claims_outcomes}"
        
        # Run pipeline components
        classification = classify_document(analysis_text)
        originality = compute_originality(analysis_text)
        fto = await analyze_fto(doc.methodology, originality.get("top_matches", []))
        valuation = calculate_valuation(
            classification.get("ipc_primary", "C01B"),
            originality.get("originality_premium_s", 0.5),
            fto.get("r_fto", 0.5),
            fto.get("expert_consultation_required", False),
            classification=classification,
            originality=originality,
            fto=fto,
        )
        trl_evaluation = evaluate_trl(
            analysis_text,
            classification=classification,
            valuation=valuation,
            title_hint=doc.abstract[:120],
            doc=doc,
        )
        market_mapping = analyze_market_mapping(
            analysis_text,
            classification,
            trl_evaluation.get("estimated_trl", 3),
            doc.document_type,
        )
        nlp_analysis = nlp_analyzer.comprehensive_analysis(analysis_text)
        
        # Run comprehensive analysis with rule-based fallback
        result = await generate_comprehensive_analysis(
            doc=doc,
            classification=classification,
            originality=originality,
            fto=fto,
            valuation=valuation,
            trl_evaluation=trl_evaluation,
            market_mapping=market_mapping,
            nlp_analysis=nlp_analysis,
            title=test_case.name,
            use_multi_agent=False,  # Use rule-based for consistent testing
        )
        
        # Validate results
        validation = validate_analysis(result, test_case)
        
        # Print intermediate results
        print(f"Classification: {classification.get('sector_name', 'Unknown')}")
        print(f"TRL: {trl_evaluation.get('trl', 'Unknown')}")
        print(f"Originality Score: {originality.get('max_cosine_similarity', 'Unknown')}")
        print(f"Valuation: ${valuation.get('v_target_usd', 0):,.0f}")
        print(f"Market Field: {market_mapping.get('working_field', 'Unknown')}")
        
        print(f"\nValidation: {'PASSED' if validation['passed'] else 'FAILED'}")
        if validation["failures"]:
            for failure in validation["failures"]:
                print(f"  - {failure}")
        
        return validation
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "test_case": test_case.name,
            "passed": False,
            "failures": [f"Exception: {str(e)}"],
        }


async def main():
    """Run all golden test cases."""
    print("="*60)
    print("Golden Test Set Execution")
    print("="*60)
    
    results = []
    for test_case in TEST_CASES:
        result = await run_test_case(test_case)
        results.append(result)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed:")
        for result in results:
            if not result["passed"]:
                print(f"  - {result['test_case']}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
