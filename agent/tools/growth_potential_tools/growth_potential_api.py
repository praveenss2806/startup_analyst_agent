# growth_potential_api.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import json
from google.adk.tools import ToolContext

# --- Pydantic Models ---
class GrowthPotential(BaseModel):
    summary: str
    potential_score: float

class Recommendation(BaseModel):
    headline: str
    details: str

class InvestorRecommendations(BaseModel):
    company_name: str
    growth_potential: GrowthPotential
    recommendations: List[Recommendation]

class InvestmentWeights(BaseModel):
    """
    Customizable weights for different investment factors.
    Values should be between 0 and 1.
    """
    valuation: float = Field(default=0.3, ge=0, le=1)
    traction: float = Field(default=0.4, ge=0, le=1)
    hiring: float = Field(default=0.1, ge=0, le=1)
    risk: float = Field(default=0.2, ge=0, le=1)
    
    def normalize_weights(self):
        total = sum(self.model_dump().values())
        if total > 0:
            for key in self.model_dump().keys():
                setattr(self, key, getattr(self, key) / total)


# --- Tool Function ---
def generate_recommendations(
    benchmark_data: dict,
    risk_data: dict,
    tool_context: ToolContext,
    weights: InvestmentWeights = InvestmentWeights()
    ) -> Dict[dict,Any]:
    """
    Generates a growth potential summary and investor-ready recommendations.
    
    Args:
        benchmark_data (dict): Output from the benchmarking tool.
        risk_data (dict): Output from the risk indicator tool.
        weights (InvestmentWeights): Customizable weights for recommendation criteria.
        
    Returns:
        A JSON string with growth potential and recommendations.
    """
    weights.normalize_weights()
    
    company_name = benchmark_data.get("company_name", "Unknown Company")
    company_metrics = benchmark_data.get("metrics", {})
    sector_median = benchmark_data.get("sector_median", {})
    risk_indicators = risk_data.get("risk_indicators", {})

    # --- 1. Calculate a Potential Score based on weighted metrics ---
    
    # Raw scores (higher is better)
    score_traction = (company_metrics.get("user_base", 0) / sector_median.get("user_base", 1)) if sector_median.get("user_base") else 0
    score_valuation = (sector_median.get("valuation_to_revenue", 1) / company_metrics.get("valuation_to_revenue", 1)) if company_metrics.get("valuation_to_revenue") else 0
    score_hiring = (company_metrics.get("revenue_per_employee", 0) / sector_median.get("revenue_per_employee", 1)) if sector_median.get("revenue_per_employee") else 0
    
    # Risk is an inverse factor. A flagged risk reduces the risk score.
    flagged_risks_count = sum(1 for flag in risk_indicators.values() if flag['is_flagged'])
    score_risk = 1.0 - (flagged_risks_count / len(risk_indicators)) if len(risk_indicators) > 0 else 1.0

    # Cap scores at 2.0 to prevent a single outlier from dominating
    score_traction = min(score_traction, 2.0)
    score_valuation = min(score_valuation, 2.0)
    score_hiring = min(score_hiring, 2.0)

    # Weighted composite score
    composite_score = (
        weights.traction * score_traction +
        weights.valuation * score_valuation +
        weights.hiring * score_hiring +
        weights.risk * score_risk
    )

    # Convert to a 1-10 scale for better readability
    potential_score = round(composite_score * 5, 2)
    
    # --- 2. Generate Summary based on score and key metrics ---
    
    if potential_score >= 8.0:
        summary_text = f"{company_name} shows strong growth potential. Key metrics indicate solid market traction and efficiency. The company is well-positioned to be a leader in its sector."
    elif potential_score >= 5.0:
        summary_text = f"{company_name} demonstrates moderate growth potential. While some metrics are solid, there are areas for improvement, particularly compared to sector benchmarks. Investment could be promising with a clear strategy to mitigate existing risks."
    else:
        summary_text = f"{company_name} has limited growth potential based on current metrics. The company faces significant challenges, including low efficiency and/or notable risks that could impede future growth. Further due diligence is strongly advised."

    growth_potential = GrowthPotential(summary=summary_text, potential_score=potential_score)

    # --- 3. Generate Investor-Ready Recommendations ---
    
    recommendations = []
    
    # Recommendation based on score
    if potential_score >= 7.0:
        recommendations.append(Recommendation(
            headline="Strong Investment Opportunity",
            details=f"The company demonstrates robust growth signals. Key metrics like user growth and revenue per employee are strong relative to the market median. This is a potential top-tier investment in its sector."
        ))
    elif potential_score >= 4.0:
        recommendations.append(Recommendation(
            headline="Conditional Investment with Due Diligence",
            details=f"The company has potential but is not a clear home run. It is essential to conduct deep due diligence on flagged risks. Consider a smaller initial investment or a phased approach tied to specific performance milestones."
        ))
    else:
        recommendations.append(Recommendation(
            headline="High-Risk Investment / Pass",
            details=f"Given the analysis, the company's risk profile is high and its growth potential appears limited. It is a high-risk investment that requires significant operational improvements to justify a venture capital investment."
        ))

    # Recommendations based on specific flagged risks
    if risk_indicators.get("inflated_valuation", {}).get("is_flagged"):
        recommendations.append(Recommendation(
            headline="Address Valuation Discrepancy",
            details="The company's valuation appears out of sync with its current revenue and/or funding. A critical part of the deal memo should be a detailed valuation analysis and negotiation to ensure the price reflects fundamentals."
        ))

    if risk_indicators.get("inflated_market_size", {}).get("is_flagged"):
        recommendations.append(Recommendation(
            headline="Scrutinize Market Size Projections",
            details="The company's stated market size is an outlier. Verify the TAM with independent market research and focus on the bottom-up, not top-down, analysis of their addressable market."
        ))

    if risk_indicators.get("hiring_inefficiency", {}).get("is_flagged"):
        recommendations.append(Recommendation(
            headline="Evaluate Operational Efficiency and Hiring Strategy",
            details="The company's revenue-per-employee is significantly below the median, suggesting potential over-hiring or low efficiency. Recommend a review of the company's burn rate and a plan for improving capital efficiency."
        ))

    final_response = InvestorRecommendations(
        company_name=company_name,
        growth_potential=growth_potential,
        recommendations=recommendations,
    ).model_dump_json(indent=2)
    
    return final_response