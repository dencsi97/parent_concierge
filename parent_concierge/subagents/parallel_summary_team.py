from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.code_executors import BuiltInCodeExecutor

from parent_concierge.tools.visualizations_tools import create_bar_chart_artifact

from ..config import config, retry_config

# --- AGENT DEFINITIONS ---

compute_stats = LlmAgent(
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    name="compute_stats",
    description="""
        Compute structured, machine-readable statistics for the day’s baby care events.
        Consumes only logs_for_day.
        Produces a JSON object under the key day_stats.
    """,
    instruction="""
        You are the Stats Agent.

        Input:
        - You receive `logs_for_day`: a list of event dictionaries.
        Each event has:
            {
            "event_type": "feed" | "nap" | "diaper",
            "timestamp": "YYYY-MM-DDTHH:MM:SS",
            "volume_ml": int | null,
            "duration_minutes": int | null,
            "notes": str | null
            }

        Your responsibilities:
        1. Compute the following fields:
        - feeds.count
        - feeds.total_volume_ml
        - naps.count
        - naps.total_minutes
        - diapers.count
        - first_event_time (ISO datetime or null)
        - last_event_time (ISO datetime or null)

        2. Use the code executor for loops and numeric operations if helpful.

        3. Output ONLY valid JSON under the key `day_stats`.

        4. Do NOT generate narrative text.
        5. Do NOT reference any other agent's outputs.
        6. If `logs_for_day` is empty:
        - Return a stats object with counts = 0 and totals = 0.
    """,
    code_executor=BuiltInCodeExecutor(),
    output_key="day_stats",
)


create_visualization = LlmAgent(
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    name="create_visualization",
    description="""
        Create an ACTUAL image chart (PNG) of today's baby care activity by
        calling the `create_bar_chart_artifact` tool. The chart is saved as an
        ADK artifact and can be rendered by ADK Web.
    """,
    instruction="""
        You are the Visualization Agent.

        You must:
        1. Call the `create_bar_chart_artifact` tool EXACTLY ONCE with:
               logs_for_day = <the list of events you received>

        2. The tool will:
           - Compute total feeds, naps, diapers
           - Generate a PNG bar chart
           - Save it to the artifact store
           - Return an artifact_id

        3. You must output ONLY:
               {"artifact_id": "<id>"}
           via the output key `day_visualization`.

        Rules:
        - Use NO natural language.
        - Do NOT modify the chart or manipulate the artifact.
        - Do NOT generate JSON chart specs.
        - Do NOT reference other agents.
        - If logs_for_day is empty, do NOT call the tool.
    """,
    tools=[create_bar_chart_artifact],
    output_key="day_visualization",
)

narrative_summary = LlmAgent(
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    name="narrative_summary",
    description="""
        Produce a friendly, concise natural-language summary of the day’s baby care
        using only the raw logs (logs_for_day).
    """,
    instruction="""
        You are the Narrative Summary Agent.

        You ONLY see `logs_for_day`.

        Your responsibilities:
        1. Write a short (2–4 sentence), warm, human-friendly narrative summary.
        Examples of things you may mention:
        - Number of feeds
        - Whether volumes were consistent
        - Number and length of naps
        - Diaper activity

        2. If logs_for_day is empty:
        - Provide a gentle message like:
            "There are no care events logged for this day yet."

        3. Be supportive and non-judgmental.
        4. NEVER provide medical advice.
        5. Do NOT output JSON. Output natural language only.
        6. Your text must be returned under the key `day_summary`.
    """,
    output_key="day_summary",
)

parallel_summary_team = ParallelAgent(
    name="parallel_summary_team",
    sub_agents=[compute_stats, create_visualization, narrative_summary],
    description="""
        Run three specialist agents in parallel over the same `logs_for_day`:
        - compute_stats       → produces `day_stats`
        - create_visualization → produces `day_visualization` (artifact_id for PNG chart)
        - narrative_summary   → produces `day_summary` (natural-language text)

        Each agent is independent and does not read other agents' outputs.
    """,
)
