# benchmark_api.py
import re
import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import Optional, Dict, Any
from google.cloud import bigquery
from google.adk.tools import ToolContext
from fastapi import HTTPException

# --- Utility Functions ---
def safe_divide(a, b):
    """Safe division returning None if denominator is 0 or missing."""
    try:
        if a is None or b is None or b == 0:
            return None
        return a / b
    except Exception:
        return None

def parse_numeric(value):
    """Extract numeric value from strings like '$1.27 Billion'."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Use a more robust check for missing data strings
        if "not applicable" in str(value).lower() or "not available" in str(value).lower():
            return None
            
        value = str(value).replace(",", "").lower()
        multiplier = 1
        if "billion" in value:
            multiplier = 1e9
        elif "million" in value:
            multiplier = 1e6

        match = re.search(r"([\d.]+)", value)
        return float(match.group(1)) * multiplier if match else None
    except Exception:
        return None


# --- Benchmark Metrics ---
def calculate_metrics(row: pd.Series) -> Dict[str, Optional[float]]:
    """
    Calculates metrics by accessing nested data from the BigQuery row.
    """
    financial_data = row.get("financial_multiples", {})
    hiring_data = row.get("hiring_data", {})
    traction_data = row.get("traction_signals", {})
    
    valuation = parse_numeric(financial_data.get("current_valuation"))
    funding = parse_numeric(financial_data.get("funding_total"))
    # Using 'revenue_multiple' key which contains a numeric value
    revenue = parse_numeric(financial_data.get("revenue_multiple"))
    employees = parse_numeric(hiring_data.get("employee_count"))
    user_base = parse_numeric(traction_data.get("user_growth"))
    growth_rate = parse_numeric(financial_data.get("growth_rate"))
    market_size = parse_numeric(financial_data.get("market_size"))

    return {
        "valuation": valuation,
        "funding_total": funding,
        "revenue": revenue,
        "employee_count": employees,
        "user_base": user_base,
        "growth_rate": growth_rate,
        "market_size": market_size,
        "valuation_to_funding": safe_divide(valuation, funding),
        "valuation_to_revenue": safe_divide(valuation, revenue),
        "funding_to_revenue": safe_divide(funding, revenue),
        "revenue_per_employee": safe_divide(revenue, employees),
        "funding_per_employee": safe_divide(funding, employees),
        "users_per_employee": safe_divide(user_base, employees),
        "revenue_per_user": safe_divide(revenue, user_base),
        "growth_to_market_size": safe_divide(growth_rate, market_size),
    }

def compute_market_benchmarks(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute median values per metric for the entire market (DataFrame).
    """
    if df.empty:
        return {}
    
    # We apply the calculate_metrics function to each row
    all_metrics = df.apply(calculate_metrics, axis=1).tolist()
    metrics_df = pd.DataFrame(all_metrics)

    return metrics_df.median(numeric_only=True).to_dict()


# --- BigQuery details ---
bq_client = bigquery.Client()
PROJECT_ID = "quiet-sum-470418-r7"
DATASET = "genai_hack_startup_analysis"
TABLE = "startup_analysis"

class BenchmarkResponse(BaseModel):
    company_name: str
    metrics: Dict[str, Optional[float]]
    sector_median: Dict[str, Optional[float]]


def get_benchmark(company_name: str, tool_context: ToolContext) -> Dict[str, Any]:
#def get_benchmark(company_name):
    """
    Get market-wide benchmark metrics for a given startup.
    """
    # Query all data from the table to perform a market-wide benchmark
    # Note: This is inefficient for a very large dataset, but necessary
    # since there is no 'sector' field to filter by.
    query_all_data = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
    """
    all_data_df = bq_client.query(query_all_data).to_dataframe()

    if all_data_df.empty:
        raise HTTPException(status_code=404, detail="No data available for benchmarking.")

    # Find the target company's row
    company_row_series = all_data_df[all_data_df["company_name"] == company_name]
    
    if company_row_series.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_row = company_row_series.iloc[0]

    # Calculate metrics for the specific company
    company_metrics = calculate_metrics(company_row)

    # Calculate median benchmarks for the entire dataset
    market_median = compute_market_benchmarks(all_data_df)
    
    response = BenchmarkResponse(
        company_name=company_name,
        metrics=company_metrics,
        sector_median=market_median,
    ).model_dump_json()
    print(response)
    return response

