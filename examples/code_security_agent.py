"""Code Security Agent — scans source files for OWASP top 10 vulnerabilities.

Read-only. Cannot modify files. Reports findings only.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are a code security auditor.

Your job is to find security vulnerabilities in source code. Focus on:
- SQL injection
- Cross-site scripting (XSS)
- Insecure authentication and session management
- Hardcoded secrets, API keys, passwords
- Path traversal
- Command injection
- Insecure deserialization

Report each finding with:
1. File and line number
2. Vulnerability type
3. Severity (Critical / High / Medium / Low)
4. Recommended fix

Do not modify any files. Report only."""


async def run_security_scan(target_dir: str):
    """Scan a directory for security vulnerabilities."""
    print(f"Running security scan on {target_dir}\n")

    async for message in query(
        prompt=f"Scan all source files in {target_dir} for security vulnerabilities. "
               "Check for OWASP top 10 issues. Report each finding with file, line, type, severity and fix.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Grep", "Glob"],  # Read-only access
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
            print(f"\nScan complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    asyncio.run(run_security_scan(target))
