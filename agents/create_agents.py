"""
Agent factory and AgentCard definitions.

AgentCards are the A2A protocol's way of advertising agent capabilities
(name, URL, description, skills, examples) for discovery. This module
defines one AgentCard per agent plus create_all_agents(), which builds
every agent and card and pairs each with its server port.
"""

from typing import Any

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    HOST_AGENT_URL,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# Customer Data Agent Card
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """Create the AgentCard for the Customer Data Agent.

    Returns:
        AgentCard advertising broad customer/ticket data-management
        capabilities, served over JSON-RPC at CUSTOMER_DATA_AGENT_URL.
    """
    return AgentCard(
        name="Customer Data Agent",
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            "Manages customer and ticket data: lookup, creation, updates, "
            "account status, and statistics via the customer support database."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="manage_customer_data",
                name="Manage Customer Data",
                description="Access and manage customer information and tickets",
                tags=["customers", "tickets", "data", "database", "mcp"],
                examples=[
                    "Get customer information for ID 5",
                    "List all active customers",
                    "Show me all open tickets with high priority",
                ],
            ),
        ],
    )


# =============================================================================
# Support Agent Card
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """Create the AgentCard for the Support Agent.

    Returns:
        AgentCard advertising troubleshooting/support capabilities, served
        over JSON-RPC at SUPPORT_AGENT_URL.
    """
    return AgentCard(
        name="Support Agent",
        url=SUPPORT_AGENT_URL,
        description=(
            "Troubleshoots customer issues (login, payment, performance, "
            "feature requests, data export) and manages support tickets."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="provide_support",
                name="Provide Customer Support",
                description="Troubleshoot issues and provide solutions",
                tags=["support", "troubleshooting", "solutions", "help"],
                examples=[
                    "I can't login to my account",
                    "How do I reset my password?",
                    "My payment failed, what should I do?",
                ],
            ),
        ],
    )


# =============================================================================
# Host Agent Card
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """Create the AgentCard for the Host Agent (Orchestrator).

    Returns:
        AgentCard advertising comprehensive, orchestrated support that
        combines data access and troubleshooting, served over JSON-RPC
        at HOST_AGENT_URL.
    """
    return AgentCard(
        name="Customer Support Host Agent",
        url=HOST_AGENT_URL,
        description=(
            "Orchestrates the Customer Data Agent and Support Agent to "
            "provide complete, data-informed customer support end to end."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="comprehensive_support",
                name="Comprehensive Customer Support",
                description="Provides complete support by combining data access and solutions",
                tags=["orchestration", "support", "data", "coordination"],
                examples=[
                    "I'm having login issues, can you check my account?",
                    "Show me my open tickets and help resolve them",
                ],
            ),
        ],
    )


# =============================================================================
# Factory Function
# =============================================================================

def create_all_agents() -> dict[str, dict[str, Any]]:
    """Create all agents for the customer support system.

    Returns:
        Dict keyed by 'customer_data', 'support', and 'host', each mapping
        to {'agent': Agent | SequentialAgent, 'card': AgentCard, 'port': int}.
    """
    return {
        "customer_data": {
            "agent": create_customer_data_agent(),
            "card": create_customer_data_agent_card(),
            "port": 10020,
        },
        "support": {
            "agent": create_support_agent(),
            "card": create_support_agent_card(),
            "port": 10021,
        },
        "host": {
            "agent": create_host_agent(),
            "card": create_host_agent_card(),
            "port": 10022,
        },
    }
