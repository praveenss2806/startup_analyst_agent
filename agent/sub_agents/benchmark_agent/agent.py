from google.adk.agents import Agent

from ...tools.benchmark_agent.result_to_state import result_to_state

prompt = """
You are a benchmark agent that performs comprehensive competitive analysis and benchmarking for startups based on previously gathered data.

Instructions:
1. You will receive the response from the previous sub-agent (data gather agent) directly in the conversation context
2. Use the result_to_state tool to store the response.
"""

# Create the agent with the tools
benchmark_agent = Agent(
    name="benchmark_agent",
    model="gemini-2.5-flash",
    description=(
        "This is a benchmark agent that performs comprehensive competitive analysis and benchmarking "
        "for startups based on previously gathered startup information and market data."
    ),
    instruction=prompt,
    tools=[result_to_state],
)