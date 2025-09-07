from google.adk.agents import Agent

from ...tools.store_to_state_tools.result_to_state import result_to_state

prompt = """
Instructions:
1. You will receive the response from the previous sub-agent (data gather agent) directly in the conversation context
2. Use the result_to_state tool to store the response.
"""

# Create the agent with the tools
store_to_state_agent = Agent(
    name="store_to_state_agent",
    model="gemini-2.5-flash",
    description=(
        "This is an agent to capture the response of the previous agent which uses an in-built py library to process the output"
    ),
    instruction=prompt,
    tools=[result_to_state],
)