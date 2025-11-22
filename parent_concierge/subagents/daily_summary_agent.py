from google.adk.agents import SequentialAgent

from .care_event_fetcher import care_event_fetcher
from .parallel_summary_team import parallel_summary_team
from .summary_output_agent import summary_output_agent


# --- AGENT DEFINITIONS ---

daily_summary_agent = SequentialAgent(
    name="daily_summary_agent",
    sub_agents=[care_event_fetcher, parallel_summary_team, summary_output_agent],
    description="""
        Execute the full daily summary pipeline in three ordered steps:

        1. care_event_fetcher
        - Interprets the user's request for a summary day (e.g. "today", "yesterday", or a date).
        - Uses tools like `get_today_date` if needed.
        - Calls `get_logs_for_day` to fetch all events for that day.
        - Produces: logs_for_day

        2. parallel_summary_team
        - Runs three specialist agents in parallel over the same logs_for_day:
            - compute_stats       → produces day_stats (JSON statistics)
            - create_visualization → produces day_visualization ({"artifact_id": "<png id>"})
            - narrative_summary   → produces day_summary (natural-language text)

        3. summary_output_agent
        - Combines logs_for_day, day_stats, day_visualization, and day_summary.
        - Produces a single final object under the key daily_summary_output:
            {
                "message": <final summary string>,
                "visualization_artifact_id": <string or null>
            }

        The final output `summary_output` is returned to the orchestrator.
    """,
)
