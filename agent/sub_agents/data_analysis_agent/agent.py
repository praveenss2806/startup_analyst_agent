from google.adk.agents import LlmAgent
from .schema import StartupAnalysis

prompt = """
You are a data analysis agent that transforms gathered startup data into a comprehensive investment analysis report.

Instructions:
1. Use the data gathered by the data_gather_agent from the state.
2. Analyze and synthesize the information to create a structured investment analysis.
3. Transform the raw data into the standardized format using the provided schema.

Your task is to:
- Process and clean the gathered data
- Calculate derived metrics and scores
- Identify risks and opportunities
- Generate investment recommendations
- Create a comprehensive analysis report

Key Requirements:
- Calculate investment scores (0-10 scale)
- Generate confidence scores (0-1 scale)
- Identify and categorize risks by severity
- Create actionable recommendations with timelines
- Provide detailed financial projections
- Include comprehensive competitor analysis
- Generate investment thesis and next steps
- Add metadata for tracking and versioning

Ensure all data is properly structured according to the schema and all required fields are populated.
"""

# Create the agent with output schema and key
data_analysis_agent = LlmAgent(
    name="data_analysis_agent",
    model="gemini-2.5-flash",
    description=(
        "This is a data analysis agent that transforms gathered startup data into a comprehensive investment analysis report "
        "with structured JSON output including financial metrics, risk assessment, growth potential, and investment recommendations."
    ),
    instruction=prompt,
    output_schema=StartupAnalysis,
    output_key="comprehensive_analysis",
)