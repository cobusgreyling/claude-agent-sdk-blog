"""Invoice Processing Agent — extracts structured data from invoices.

Reads invoice files. Writes structured output (JSON). Uses custom tools for validation.
"""

import asyncio
import json
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    tool,
    create_sdk_mcp_server,
)

SYSTEM_PROMPT = """You are an invoice processing specialist.

From each invoice, extract:
- Invoice number
- Invoice date
- Due date
- Vendor name and address
- Line items (description, quantity, unit price, total)
- Subtotal, tax, total amount
- Payment terms
- Currency

Validate all extracted data:
- Line item totals must equal quantity * unit price
- Subtotal must equal sum of line item totals
- Total must equal subtotal + tax

Use the validate_invoice tool to check your extraction.
Write the structured data as JSON to invoices_output.json.
Flag any discrepancies or missing fields."""


@tool(
    "validate_invoice",
    "Validate extracted invoice data for mathematical consistency",
    {
        "line_items": list,
        "subtotal": float,
        "tax": float,
        "total": float,
    },
)
async def validate_invoice(args):
    """Check that invoice numbers add up correctly."""
    errors = []

    # Validate line item totals
    calculated_subtotal = 0
    for i, item in enumerate(args["line_items"]):
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0)
        line_total = item.get("total", 0)
        expected = round(qty * price, 2)
        if abs(line_total - expected) > 0.01:
            errors.append(
                f"Line {i+1}: total {line_total} != qty {qty} * price {price} = {expected}"
            )
        calculated_subtotal += expected

    # Validate subtotal
    if abs(args["subtotal"] - calculated_subtotal) > 0.01:
        errors.append(
            f"Subtotal {args['subtotal']} != sum of lines {calculated_subtotal}"
        )

    # Validate total
    expected_total = round(args["subtotal"] + args["tax"], 2)
    if abs(args["total"] - expected_total) > 0.01:
        errors.append(
            f"Total {args['total']} != subtotal {args['subtotal']} + tax {args['tax']} = {expected_total}"
        )

    if errors:
        return {"content": [{"type": "text", "text": f"VALIDATION FAILED:\n" + "\n".join(errors)}]}
    return {"content": [{"type": "text", "text": "VALIDATION PASSED: All totals are consistent."}]}


async def process_invoices(invoice_path: str):
    """Extract structured data from invoices."""
    print(f"Processing invoice: {invoice_path}\n")

    invoice_tools = create_sdk_mcp_server(
        name="invoice-tools",
        version="1.0.0",
        tools=[validate_invoice],
    )

    async for message in query(
        prompt=f"Read the invoice at {invoice_path}. "
               "Extract all fields (number, date, vendor, line items, totals). "
               "Validate the math using the validate_invoice tool. "
               "Write structured JSON output to invoices_output.json.",
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Write", "mcp__invoice-tools__validate_invoice"],
            mcp_servers={"invoice-tools": invoice_tools},
            permission_mode="acceptEdits",
            max_turns=10,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nInvoice processing complete. Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python invoice_processing_agent.py <invoice_file>")
        sys.exit(1)
    asyncio.run(process_invoices(sys.argv[1]))
