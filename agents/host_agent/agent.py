"""
Host Agent / Orchestrator.

A SequentialAgent that coordinates the Customer Data Agent and Support
Agent over the A2A protocol:

  Host Agent (SequentialAgent)
    -> RemoteA2aAgent("customer_data") -- calls Customer Data Agent via A2A
    -> RemoteA2aAgent("support_specialist") -- calls Support Agent via A2A

RemoteA2aAgent wraps a remote agent as a local sub-agent, discovered via
its agent card at `agent_url + AGENT_CARD_WELL_KNOWN_PATH`. SequentialAgent
runs its sub-agents in order, passing context between them.
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============================================================================
# CRITICAL: Apply A2A compatibility patch BEFORE importing RemoteA2aAgent
# This fixes an import issue between google-adk and a2a-sdk versions.
# =============================================================================
from shared import a2a_compat  # noqa: F401

from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
)

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [HOST_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_agent() -> SequentialAgent:
    """Create the Host Agent (Orchestrator).

    Returns:
        SequentialAgent wrapping remote Customer Data and Support agents
        as RemoteA2aAgent sub-agents, run in that order.
    """
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    return SequentialAgent(
        name="customer_support_host",
        sub_agents=[remote_customer_data, remote_support],
    )
