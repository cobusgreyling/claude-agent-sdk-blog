"""Email Automation Agent — drafts, classifies and routes email responses.

Reads email content. Writes draft responses. Can fetch external context via web.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are an email automation specialist.

For each email you process:
1. Classify priority (Urgent / Normal / Low)
2. Identify the category (Support / Sales / Legal / Internal / Spam)
3. Extract key requests or questions
4. Draft an appropriate response

Response guidelines:
- Professional and concise
- Address all points raised in the original email
- Include a clear call to action
- Match the formality level of the incoming email

Write draft responses to email_drafts.md with clear separation between each draft.
Include the original subject line, priority and category above each draft."""


async def process_emails(inbox_path: str):
    """Process emails and generate draft responses."""
    print(f"Processing emails from: {inbox_path}\n")

    async for message in query(
        prompt=f"Read the emails at {inbox_path}. "
               "For each email, classify priority and category, "
               "extract key requests, and draft a response. "
               "Write all drafts to email_drafts.md.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Write", "WebFetch"],  # Read emails, write drafts, fetch context
            permission_mode="acceptEdits",
            max_turns=15,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nEmail processing complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python email_automation_agent.py <emails_file>")
        sys.exit(1)
    asyncio.run(process_emails(sys.argv[1]))
