from google.adk.agents import SequentialAgent

from .sub_agents.file_ingestion_agent.agent import data_ingestion_agent

root_agent = SequentialAgent(
    name="startup_analyst_agent",
    description=(
        "This is a startup analyst agent that helps analyze startup data and provide insights."
    ),
    sub_agents=[data_ingestion_agent]
)