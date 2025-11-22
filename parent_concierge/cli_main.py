# parent_concierge/cli_main.py

import asyncio
from pathlib import Path
from dotenv import load_dotenv


from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService

# 👇 IMPORTANT: use YOUR agent, not the built-in examples
from parent_concierge.parent_concierge_agent import parent_concierge_agent


# ---- Constants ----
# Must match the top-level package where your agent lives
APP_NAME = "parent_concierge"
USER_ID = "dev-user-1"
SESSION_ID = "local-dev-session-1"


def build_user_message(text: str) -> types.Content:
    """Helper to turn raw user text into a GenAI Content message."""
    return types.Content(
        role="user",
        parts=[types.Part(text=text)],
    )


async def chat_loop() -> None:
    # 1. Set up session service and create a session (async)
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # 2. Set up logging plugin + runner
    logging_plugin = LoggingPlugin()

    runner = Runner(
        agent=parent_concierge_agent,
        app_name=APP_NAME,
        session_service=session_service,
        plugins=[logging_plugin],
        artifact_service=artifact_service,
    )

    try:
        print("👶 New Parent Concierge (CLI dev mode)")
        print("Type 'exit' or 'quit' to end.\n")

        # 3. Simple REPL over one persistent session
        while True:
            user_text = input("You: ").strip()
            if not user_text:
                continue
            if user_text.lower() in {"exit", "quit"}:
                print("Goodbye! 👋")
                break

            user_message = build_user_message(user_text)
            final_text = None

            # Stream events asynchronously
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=user_message,
            ):
                # Let LoggingPlugin do the heavy lifting in your terminal
                if event.is_final_response() and event.content and event.content.parts:
                    final_text = event.content.parts[0].text

            if final_text:
                print(f"Concierge: {final_text}\n")
            else:
                print("Concierge: [no text response]\n")

    finally:
        await runner.close()



def main() -> None:

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    asyncio.run(chat_loop())


if __name__ == "__main__":
    main()
