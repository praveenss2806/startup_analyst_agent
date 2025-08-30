from google.adk.agents import Agent
from ...tools.file_ingestion_tools.pdf_ingestion_tool import pdf_ingestion_tool

prompt = """
Extract text and data from the PDF file at '/path/to/your/document.pdf' using the pdf_ingestion_tool. 
Process all pages and provide the extracted content with layout preservation.
"""

data_ingestion_agent = Agent(
    name="data_ingestion_agent",
    model="gemini-2.5-flash",
    description=(
        "This is a data ingestion agent that ingests data from various file types and extract the data."
    ),
    instruction=prompt,
    tools=[pdf_ingestion_tool],
)