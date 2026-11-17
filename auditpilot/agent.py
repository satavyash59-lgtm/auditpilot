from google.adk.agents import SequentialAgent

from auditpilot.agents.intake import intake_agent
from auditpilot.agents.specialists import specialist_agent
from auditpilot.agents.reporting import reporting_agent

root_agent = SequentialAgent(
    name="audit_pipeline",
    sub_agents=[
        intake_agent,
        specialist_agent,
        reporting_agent,
    ],
)
