from google.adk.agents import SequentialAgent

from .sub_agents.file_ingestion_agent.agent import data_ingestion_agent
from .sub_agents.data_gather_agent.agent import data_gather_agent
from .sub_agents.data_analysis_agent.agent import data_analysis_agent

root_agent = SequentialAgent(
    name="startup_analyst_agent",
    description=(
        "This is a startup analyst agent that helps analyze startup data and provide insights."
    ),
    sub_agents=[data_ingestion_agent, data_gather_agent, data_analysis_agent]
)