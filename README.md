# Parent Concierge

Parent Concierge is an AI-driven assistant for new parents. It provides tooling for capturing baby care events, maintaining a baby profile, and producing daily summaries through orchestrated ADK agents.

## Features
- CLI entrypoint (`parent_concierge/cli_main.py`) wired to the top-level `parent_concierge_agent` for interactive conversations.
- Persistent baby profile storage in `data/profiles.json` managed by tool functions.
- Care event logging and retrieval stored under `data/care_logs.json`.
- Daily summary pipeline that fetches logs, computes statistics, generates visualizations, and assembles final narrative output.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in a `.env` file at the project root as needed (for example, API keys used by the Google ADK runtime).

## Usage
Run the local CLI assistant:
```bash
python -m parent_concierge.cli_main
```
You can type natural language queries like "log a 90ml feed at 7:10" or "summarize today". Type `exit` or `quit` to end the session.

## Testing
Execute the test suite:
```bash
pytest
```
