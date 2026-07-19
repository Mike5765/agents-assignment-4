"""
McpToolset factory functions for the customer support agents.

Configures Google ADK's McpToolset against the MCP server via SSE. Each
factory scopes its agent to a `tool_filter` subset of the 15 tools exposed
by the MCP server (see mcp_server/app.py):
  Customer: get_customer, list_customers, add_customer, update_customer,
            disable_customer, activate_customer
  Ticket:   get_ticket, list_tickets, create_ticket, update_ticket_status,
            update_ticket_priority, delete_ticket
  Stats:    get_ticket_stats, get_customer_stats, search_tickets
"""

import logging

from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from shared.agents_config import MCP_SERVER_URL

# Setup logging
logger = logging.getLogger(__name__)

# SSE endpoint URL for the MCP server
MCP_SSE_URL = f"{MCP_SERVER_URL}/sse"
logger.info(f"[MCP_TOOLSET] MCP SSE URL: {MCP_SSE_URL}")


# =============================================================================
# EXAMPLE: Full toolset with no filter (all 15 tools) - for reference only
# =============================================================================
def create_full_toolset() -> McpToolset:
    """Create an McpToolset with ALL MCP server tools (no filter).

    This is provided as a reference. In practice, agents should use
    filtered toolsets so each agent only has access to the tools it needs.

    Returns:
        McpToolset: Toolset connected to MCP server with all tools
    """
    logger.info("[MCP_TOOLSET] Creating full toolset (no filter)")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
    )


# =============================================================================
# Customer Data Toolset — broad data access (lookup, create, update, admin,
# ticket management, statistics)
# =============================================================================

def create_customer_data_toolset() -> McpToolset:
    """Create an McpToolset for the Customer Data Agent.

    Includes tools for customer lookup, ticket management, statistics,
    and admin operations. This agent has broad data access.

    Returns:
        McpToolset: Toolset with customer data tools
    """
    logger.info("[MCP_TOOLSET] Creating customer data toolset")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=[
            "get_customer", "list_customers", "add_customer", "update_customer",
            "disable_customer", "activate_customer",
            "get_ticket", "list_tickets", "create_ticket",
            "update_ticket_status", "update_ticket_priority",
            "get_ticket_stats", "get_customer_stats", "search_tickets",
        ],
    )


# =============================================================================
# Support Toolset — support-safe subset; excludes admin/destructive ops
# (disable_customer, activate_customer, add_customer, update_customer,
# delete_ticket)
# =============================================================================

def create_support_toolset() -> McpToolset:
    """Create an McpToolset for the Support Agent.

    Includes only support-safe tools: lookups, ticket management, and stats.
    Excludes admin operations (disable/activate customer, delete ticket,
    add/update customer).

    Returns:
        McpToolset: Toolset with support-safe tools only
    """
    logger.info("[MCP_TOOLSET] Creating support toolset")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=[
            "get_customer", "list_customers",
            "get_ticket", "list_tickets", "search_tickets",
            "create_ticket", "update_ticket_status", "update_ticket_priority",
            "get_ticket_stats", "get_customer_stats",
        ],
    )
