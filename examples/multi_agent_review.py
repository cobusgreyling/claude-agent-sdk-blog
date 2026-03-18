"""Multi-Agent Code Review — parent agent delegates to specialised subagents.

Demonstrates the subagent pattern: a parent agent spawns a security reviewer
and a code quality reviewer in parallel. Each runs in isolated context with
restricted tools. The parent synthesises the results.
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

PARENT_PROMPT = """You are a lead engineer coordinating a code review.

You have two specialised reviewers available:
1. security-reviewer — finds security vulnerabilities
2. quality-reviewer — finds code quality issues

For the given codebase:
1. Delegate security analysis to the security-reviewer
2. Delegate quality analysis to the quality-reviewer
3. Synthesise both reports into a single prioritised review

Present the final review with sections:
- Critical Issues (must fix before merge)
- Improvements (should fix)
- Suggestions (nice to have)"""


async def run_multi_agent_review(target_dir: str):
    """Run parallel security and quality reviews via subagents."""
    print(f"Starting multi-agent review of {target_dir}\n")

    async for message in query(
        prompt=f"Review all Python files in {target_dir}. "
               "Run security and quality reviews in parallel using your subagents. "
               "Synthesise the results into a single prioritised report.",
        options=ClaudeAgentOptions(
            system_prompt=PARENT_PROMPT,
            allowed_tools=["Read", "Glob", "Agent"],  # Agent tool enables subagents
            permission_mode="acceptEdits",
            cwd=target_dir,
            max_turns=25,
            agents={
                "security-reviewer": AgentDefinition(
                    description="Expert at finding security vulnerabilities in code",
                    prompt=(
                        "You are a security auditor. Scan all Python files for:\n"
                        "- SQL injection, command injection, path traversal\n"
                        "- Hardcoded secrets and credentials\n"
                        "- Insecure deserialization\n"
                        "- Missing input validation\n"
                        "Report each finding with file, line, severity and fix."
                    ),
                    tools=["Read", "Grep", "Glob"],  # Read-only
                ),
                "quality-reviewer": AgentDefinition(
                    description="Expert at code quality, readability and best practices",
                    prompt=(
                        "You are a code quality reviewer. Check all Python files for:\n"
                        "- Naming conventions and readability\n"
                        "- Error handling gaps\n"
                        "- Code duplication\n"
                        "- Missing type hints on public APIs\n"
                        "- Unused imports or dead code\n"
                        "Report each finding with file, line, category and suggestion."
                    ),
                    tools=["Read", "Grep", "Glob"],  # Read-only
                ),
            },
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    if block.name == "Agent":
                        print(f"\n>> Delegating to: {block.input.get('description', block.name)}")
        elif isinstance(message, ResultMessage):
            print(f"\nReview complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    asyncio.run(run_multi_agent_review(target))
