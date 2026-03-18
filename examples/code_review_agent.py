"""Code Review Agent — reviews code for quality, readability and best practices.

Read-only analysis with the ability to run linters via Bash.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are a senior code reviewer.

Review code for:
- Readability and naming conventions
- Error handling gaps
- Code duplication
- Missing type hints or documentation
- Anti-patterns and code smells
- Unused imports or variables

For each issue, provide:
1. File and line number
2. Category (readability / error-handling / duplication / style)
3. Current code snippet
4. Suggested improvement

Be constructive. Prioritise issues that affect maintainability.
Do not modify any files."""


async def review_code(target_dir: str, file_pattern: str = "**/*.py"):
    """Review source files for quality issues."""
    print(f"Reviewing {file_pattern} in {target_dir}\n")

    async for message in query(
        prompt=f"Review all {file_pattern} files for code quality. "
               "Check readability, error handling, duplication and style. "
               "Prioritise the most impactful issues.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Grep", "Glob", "Bash"],
            permission_mode="acceptEdits",
            cwd=target_dir,
            max_turns=20,
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
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    asyncio.run(review_code(target))
