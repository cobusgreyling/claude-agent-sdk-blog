"""Contract Review Agent — analyses legal documents for risk clauses and obligations.

Reads documents. Cannot modify them. Produces structured risk assessment.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are a contract review specialist.

Analyse legal documents and identify:
- Payment terms and conditions
- Termination clauses and notice periods
- Liability limitations and indemnification
- Non-compete and exclusivity provisions
- Data protection and confidentiality obligations
- Automatic renewal clauses
- Governing law and dispute resolution

For each clause found, provide:
1. Clause type
2. Location in the document
3. Key terms and conditions
4. Risk level (High / Medium / Low)
5. Plain-language summary

Flag any unusual or one-sided terms that may require negotiation.
Do not modify any files."""


async def review_contract(file_path: str):
    """Analyse a contract document for risk and obligations."""
    print(f"Reviewing contract: {file_path}\n")

    async for message in query(
        prompt=f"Read and analyse the contract at {file_path}. "
               "Identify all key clauses, obligations and risks. "
               "Produce a structured risk assessment with plain-language summaries.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read"],  # Read-only, single file
            permission_mode="acceptEdits",
            max_turns=10,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nReview complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python contract_review_agent.py <contract_file>")
        sys.exit(1)
    asyncio.run(review_contract(sys.argv[1]))
