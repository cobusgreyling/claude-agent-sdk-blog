"""Financial Reporting Agent — analyses financial data and generates reports.

Reads data files, runs calculations via Bash, writes report output.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

SYSTEM_PROMPT = """You are a financial reporting analyst.

Analyse financial data and produce clear reports covering:
- Revenue and expense summaries
- Profit margins and trends
- Year-over-year or period-over-period comparisons
- Anomalies or outliers that require attention
- Key financial ratios (if data permits)

Use Bash to run Python calculations when needed for aggregations or statistics.
Present numbers with proper formatting (currency symbols, percentages, thousands separators).
Write the final report to financial_report.md.

Be precise with numbers. Never estimate when you can calculate."""


async def generate_report(data_path: str):
    """Analyse financial data and generate a report."""
    print(f"Analysing financial data: {data_path}\n")

    async for message in query(
        prompt=f"Read the financial data at {data_path}. "
               "Analyse revenue, expenses, margins and trends. "
               "Flag anomalies. Write a structured report to financial_report.md.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Bash", "Write"],  # Read data, calculate, write report
            permission_mode="acceptEdits",
            max_turns=15,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nReport complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python financial_reporting_agent.py <data_file>")
        sys.exit(1)
    asyncio.run(generate_report(sys.argv[1]))
