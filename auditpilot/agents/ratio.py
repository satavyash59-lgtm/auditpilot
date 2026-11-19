from google.adk.agents.llm_agent import Agent

from auditpilot.tools.data_tools import ratio_table

ratio_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="ratio_agent",
    description="Analyzes company financial ratios.",
    instruction="""
    You are the Financial Ratio Agent.

    Run ratio_table.
    Report total revenue, total expenses and expense-to-revenue ratio.
    Explain the results clearly.
    Use only actual tool outputs.
    Do not invent financial figures.
    """,
    tools=[ratio_table],
    output_key="ratio_findings",
)
