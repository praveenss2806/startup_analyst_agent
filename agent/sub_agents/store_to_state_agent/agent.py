from google.adk.agents import Agent

from ...tools.store_to_state_tools.result_to_state import result_to_state
from ...tools.store_to_state_tools.jsonTOjsonl import convert_json_to_json_lines
from ...tools.store_to_state_tools.StoreToBigquery import store_to_bigquery

prompt = """
Instructions:
1. You will receive the response from the previous sub-agent (data gather agent) directly in the conversation context
2. Use the result_to_state tool to store the response.
3. Use the convert_json_to_json_lines tool to convert the response to JSON Lines format.
4. Use the store_to_bigquery tool to store the JSON Lines data in BigQuery.
"""

# Create the agent with the tools
store_to_state_agent = Agent(
    name="store_to_state_agent",
    model="gemini-2.5-flash",
    description=(
        "This is an agent to capture the response of the previous agent which uses an in-built py library to process the output"
    ),
    instruction=prompt,
    tools=[result_to_state, convert_json_to_json_lines, store_to_bigquery],
)