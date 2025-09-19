from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext

# --- Pydantic Models ---
class RiskFlag(BaseModel):
    is_flagged: bool = False
    reason: Optional[str] = None

class RiskIndicatorsResponse(BaseModel):
    company_name: str
    risk_indicators: Dict[str, RiskFlag] = Field(default_factory=dict)
    
# --- Tool Function ---
def flag_risk_indicators(benchmark_data: dict, tool_context: ToolContext) -> Dict[dict, Any]:
    """
    Analyzes a startup's metrics against sector benchmarks to flag potential risks.
    
    Args:
        benchmark_data (dict): The output from the get_benchmark tool, containing
                               company metrics and sector medians.
    
    Returns:
        A JSON string of risk indicators.
    """
    company_metrics = benchmark_data.get("metrics", {})
    sector_median = benchmark_data.get("sector_median", {})
    company_name = benchmark_data.get("company_name", "Unknown Company")
    
    risk_indicators = {}
    
    # 1. Valuation Risk: Compare Valuation-to-Revenue and Valuation-to-Funding ratios.
    val_to_rev_comp = company_metrics.get("valuation_to_revenue")
    val_to_fund_comp = company_metrics.get("valuation_to_funding")
    val_to_rev_median = sector_median.get("valuation_to_revenue")
    val_to_fund_median = sector_median.get("valuation_to_funding")
    
    valuation_risk_flag = RiskFlag()
    if val_to_rev_comp and val_to_rev_median and val_to_rev_comp > 2.0 * val_to_rev_median:
        valuation_risk_flag.is_flagged = True
        valuation_risk_flag.reason = "Valuation-to-Revenue ratio is more than double the sector median, indicating a potentially inflated valuation."
    
    if val_to_fund_comp and val_to_fund_median and val_to_fund_comp > 2.0 * val_to_fund_median:
        if valuation_risk_flag.is_flagged:
            valuation_risk_flag.reason += " Also, the Valuation-to-Funding ratio is significantly higher than the sector median."
        else:
            valuation_risk_flag.is_flagged = True
            valuation_risk_flag.reason = "Valuation-to-Funding ratio is significantly higher than the sector median, indicating a potentially over-leveraged valuation."
    
    risk_indicators["inflated_valuation"] = valuation_risk_flag
    
    # 2. Market Size Risk: Flag if the company's market size is a major outlier.
    market_size_comp = company_metrics.get("market_size")
    market_size_median = sector_median.get("market_size")
    
    market_size_risk_flag = RiskFlag()
    if market_size_comp and market_size_median and market_size_comp > 10.0 * market_size_median:
        market_size_risk_flag.is_flagged = True
        market_size_risk_flag.reason = "Stated market size is more than 10x the sector median, which may be an inflated or unrealistic projection."
        
    risk_indicators["inflated_market_size"] = market_size_risk_flag
    
    # 3. Efficiency & Hiring Risk: Check Revenue-per-Employee.
    rev_per_employee_comp = company_metrics.get("revenue_per_employee")
    rev_per_employee_median = sector_median.get("revenue_per_employee")
    
    hiring_risk_flag = RiskFlag()
    if rev_per_employee_comp and rev_per_employee_median and rev_per_employee_comp < 0.5 * rev_per_employee_median:
        hiring_risk_flag.is_flagged = True
        hiring_risk_flag.reason = "Revenue per employee is less than half the sector median, suggesting low capital efficiency or a recent, unsustainable hiring increase."
        
    risk_indicators["hiring_inefficiency"] = hiring_risk_flag
    
    # 4. Growth vs. Market: Check if growth is consistent with market potential.
    growth_to_market_comp = company_metrics.get("growth_to_market_size")
    growth_to_market_median = sector_median.get("growth_to_market_size")
    
    growth_risk_flag = RiskFlag()
    if growth_to_market_comp is not None and growth_to_market_median is not None:
        if growth_to_market_comp < 0.5 * growth_to_market_median:
            growth_risk_flag.is_flagged = True
            growth_risk_flag.reason = "Growth-to-Market Size ratio is significantly lower than the sector median, which could mean the company is underperforming in a high-growth market."
    
    risk_indicators["underperforming_growth"] = growth_risk_flag
    
    # Final response
    response = RiskIndicatorsResponse(
        company_name=company_name,
        risk_indicators=risk_indicators,
    ).model_dump_json()
    tool_context.state['risk_data'] = response
    return response