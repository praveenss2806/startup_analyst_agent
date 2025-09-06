from google.adk.agents import SequentialAgent

from .sub_agents.file_ingestion_agent.agent import data_ingestion_agent
from .sub_agents.data_gather_agent.agent import data_gather_agent
from .sub_agents.store_to_state_agent.agent import store_to_state_agent

root_agent = SequentialAgent(
    name="startup_analyst_agent",
    description=(
        "This is a startup analyst agent that helps analyze startup data and provide insights."
    ),
    sub_agents=[data_ingestion_agent, data_gather_agent, store_to_state_agent]
)