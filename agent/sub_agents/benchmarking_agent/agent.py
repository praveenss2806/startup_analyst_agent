from google.adk.agents import Agent
from ...tools.benchmarking_tools.create_benchmarks import get_benchmark

prompt = """
You are a benchmarking subagent that compares startups against their sector peers.

Configuration:
- input_keys: ["company_name"]   # Take company_name from the agent state
- output_key: "benchmarking_results"  # Store results under this key in the state

Your task:
- Input: a company_name (string).
- Action: Query a BigQuery table that contains structured startup data (financial_multiples, hiring_data, traction_signals).
- Output: A JSON object with the following:
    - company_name
    - benchmarking metrics (16 metrics covering valuations, funding, revenue, hiring, traction ratios).
    - sector_median (median benchmarks for that sector).
- Handle missing values gracefully (if a field is missing, return null instead of error).
- Ensure safe division (no divide-by-zero).

"""

benchmarking_agent = Agent(
    name="benchmarking_agent",
    model="gemini-2.5-flash",
    description="This is a benchmarking subagent that compares startups against their sector peers.",
    instruction=prompt,
    tools=[get_benchmark],   
)
