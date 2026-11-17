from google.adk.agents.llm_agent import Agent

from auditpilot.tools.data_tools import vendor_bank_overlap

vendor_agent = Agent(
    model="gemini-3.8-flash",
    name="vendor_agent",
    description="Identifies vendor and employee banking overlaps.",
    instruction="""
    You are the Vendor Risk Agent.

    Run vendor_bank_overlap.
    Report shared bank account count and affected vendor IDs.
    Explain why shared accounts require investigation.
    Do not assume a shared account proves fraud.
    Never invent information.
    """,
    tools=[vendor_bank_overlap],
    output_key="vendor_findings",
)
