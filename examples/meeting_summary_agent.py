"""Meeting Summary Agent — extracts action items, decisions and owners from meeting notes.

Reads meeting transcripts or notes. Writes a structured summary.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are a meeting summary specialist.

From meeting notes or transcripts, extract:
- Date and attendees
- Key decisions made
- Action items with owners and deadlines
- Open questions or unresolved topics
- Follow-up meeting requirements

Format the output as a structured summary with clear sections.
Use bullet points for action items.
Each action item must have an owner and a deadline (or "TBD" if not stated).

Write the summary to a file named meeting_summary.md."""


async def summarise_meeting(notes_path: str):
    """Extract a structured summary from meeting notes."""
    print(f"Summarising meeting notes: {notes_path}\n")

    async for message in query(
        prompt=f"Read the meeting notes at {notes_path}. "
               "Extract all decisions, action items with owners and deadlines, "
               "and open questions. Write a structured summary to meeting_summary.md.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Write"],  # Read input, write summary
            permission_mode="acceptEdits",
            max_turns=10,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nSummary complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python meeting_summary_agent.py <meeting_notes_file>")
        sys.exit(1)
    asyncio.run(summarise_meeting(sys.argv[1]))
