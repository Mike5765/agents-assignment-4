# Assignment 4: Reflection

## Student Name: Michael Kelley

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
- Which MCP tools did you implement and why?
The MCP tools themselves were provided (15 tools in `mcp_server/app.py`); what I implemented was the *toolset scoping* via `tool_filter`. The Customer Data Agent gets a broad filter, everything except `delete_ticket`, since it's the system's data-access layer and needs to read and write customer/ticket records freely. The Support Agent gets a narrower filter excluding `add_customer`, `update_customer`, `disable_customer`, `activate_customer`, and `delete_ticket`, keeping it limited to lookup, ticket creation/update, and stats. The design principle was least privilege by role: the agent that talks directly to customers shouldn't be able to disable an account or delete a ticket, even though the underlying MCP server exposes that capability.

- How did you design the tool signatures for ADK compatibility?
This wasn't manual signature design, that's the point of `McpToolset`. It connects to the MCP server over SSE and auto-discovers each tool's schema directly from the server, so the ADK-compatible wrapper is generated automatically. My job was which subset of the 15 auto-discovered tools each agent should see, and I verified those tool name strings against the live server's actual registrations in `mcp_server/app.py` rather than trusting the docstring in `mcp_toolset.py`, since they turned out to match but a typo would have silently produced a broken filter.


### Data Agent Instruction
- What capabilities did you include in the system instruction?
The instruction covers the agent's role as a customer data specialist with database read/write access, a full tool inventory grouped by category (customer lookup/management, ticket operations, statistics/search), a step-by-step request-handling procedure (parse the request, resolve missing IDs via lookup tools first rather than guessing, chain tool calls for multi-step requests, never fabricate data), and a response style directive (precise, data-driven, structured so another agent can consume it directly).

- How does the instruction guide the agent's tool selection?
By pairing each capability category with its exact tool names, and by giving explicit sequencing logic for chained requests, a "find customer X and list their tickets" style query should chain a lookup call into a ticket-list call rather than fabricating data. The instruction also handles the rubric's error-handling requirement at the instruction level (report tool errors plainly, never invent data), since `McpToolset` itself already handles wire-level MCP errors automatically.


---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- What knowledge did you embed in the support agent's instruction?
A five-category knowledge base, login issues, payment issues, performance/timeout issues, feature requests, and data export issues, each with troubleshooting steps rather than generic advice. Paired with that is a request-handling procedure: categorize the issue, pull customer/ticket context via read tools if an ID is available, propose the matching troubleshooting steps, then decide on a ticket action. Admin operations are explicitly flagged as out of scope and to be deferred rather than worked around, reinforcing what the `tool_filter` already restricts.

- How does it handle queries without external tools?
The knowledge base is static and embedded directly in the instruction, so general troubleshooting guidance can be answered from the instruction alone with zero tool calls when no customer/ticket lookup is implied. Tools are only invoked when the query references an actual account or existing ticket.


### Host Agent Orchestration
- How does the SequentialAgent coordinate between sub-agents?
`host_agent/agent.py` wires two `RemoteA2aAgent` wrappers, `customer_data` and `support_specialist`, into one `SequentialAgent` (`customer_support_host`), run in that order. `SequentialAgent` executes its `sub_agents` list in sequence, carrying context forward between them, so ordering customer-data-first, support-second reflects the intended workflow of pulling facts before reasoning about them.

- What happens when the Customer Data Agent returns data to the Support Agent?
The Customer Data Agent's output becomes part of the shared context `SequentialAgent` passes into the next step, so the Support Agent has that retrieved customer/ticket data already available when it runs, rather than needing to fetch it itself.


### A2A Protocol Insights
- How does agent discovery work via AgentCards?
Each agent publishes an `AgentCard`, name, URL, description, capabilities, and a list of `AgentSkill` entries with ids, descriptions, tags, and example queries. A `RemoteA2aAgent` doesn't need any knowledge of the remote agent's internal implementation; it fetches the card and gets everything it needs to decide it can delegate work there.

- What role does the `.well-known/agent-card.json` endpoint play?
It's the standardized, predictable location every A2A-compliant agent serves its card from, `AGENT_CARD_WELL_KNOWN_PATH` appended to the agent's base URL. That convention is what makes discovery automatic rather than requiring hardcoded per-agent integration knowledge.

- How does RemoteA2aAgent differ from direct function calls?
A direct function call requires shared code in the same process. `RemoteA2aAgent` instead treats the other agent as an independent network service, it discovers capabilities via the card, then communicates over the A2A protocol as if the other agent were running on a different machine or built in a different framework entirely. That's the actual point of the exercise: the Support Agent and Customer Data Agent don't need to know anything about each other's internals to cooperate.


---

## Part 3: Challenges and Solutions

### Technical Challenges
- What was the most difficult part of the implementation?
A dependency version mismatch, not the agent logic itself. `requirements.txt` pinned `google-adk>=1.9.0` and `a2a-sdk>=0.3.0` with no upper bound, so a fresh install resolved to `google-adk==2.5.0` and `a2a-sdk==1.1.1`, both far newer than what the starter code was actually built against. `a2a-sdk` 1.x turned out to be a different API generation entirely, with `AgentCard` as a protobuf message instead of the pydantic model the scaffold assumed, and no `TransportProtocol` in `a2a.types`, which broke AgentCard construction (`test_a2a.py`: 7/11 passing). Pinning `a2a-sdk==0.3.0` fixed that, but pinning `google-adk` to the version named in `a2a_compat.py`'s own docstring (1.9.0) then broke Part 1: that version exports the toolset class as `MCPToolset` (all-caps), while every given file actually imports `McpToolset` (lowercase c), a name that doesn't exist at 1.9.0. That meant the documented version was simply wrong. Bisecting installed package versions directly (inspecting `mcp_tool/__init__.py` across releases) found the rename to `McpToolset` lands at `google-adk==1.13.0`, which became the actual working pin, paired with `a2a-sdk==0.3.0`.

-How did you debug agent communication issues?

By treating the test suite output and the actual installed package contents as ground truth over the documentation. When `test_a2a` failed with `TransportProtocol` missing, the fix was to check what version was actually installed versus what the docstrings claimed, then confirm the correct version by inspecting the package directly rather than guessing. I also re-ran all three test suites after each dependency change specifically to catch regressions, since fixing one version mismatch (`a2a-sdk`) broke a previously-passing part (`test_mcp_toolset`) once `google-adk` was pinned alongside it. Also confirmed the `a2a_compat.py` patch was still necessary at the final pinned version by grepping the installed package for both the old broken import path and the new correct one, the upstream bug it patches around was fixed between 1.9.0 and 1.13.0, but the patch was kept since `test_a2a.py` still explicitly checks for it.

A second debugging issue surfaced later, after the code itself was working: `test_scenarios.py` reported 10/10 scenarios passing, but every response body was actually an API error (a 404 for a deprecated Gemini model, then 429 rate-limit errors once retries piled up). The script's own verification logic only checked for response length and keyword presence, both of which an error message satisfies just as easily as a real answer. I caught this by manually reading the response content instead of trusting the pass/fail summary, which is really the same lesson as the dependency issue: verify against what's actually happening, not what a status indicator claims.


### Architecture Decisions
- Why is the SequentialAgent pattern appropriate for this use case?
The workflow has a genuine order dependency: the Support Agent's troubleshooting advice is more useful with the customer's account and ticket context already in hand rather than needing to ask for it separately. `SequentialAgent` encodes that dependency directly, data lookup first, support reasoning second, context passed forward automatically. A `ParallelAgent` wouldn't fit, since the second step depends on the first step's output rather than being an independent subtask.

- What are the trade-offs vs. direct agent calls?
Direct function calls would be simpler and faster, no network hop, no card discovery, no protocol serialization, but they'd tightly couple the host agent to the internal implementation of the other two agents. `RemoteA2aAgent` instead makes each agent independently deployable, independently testable via `adk web`, and swappable for a differently-built agent as long as it serves a compliant AgentCard. The cost is real: more moving parts and more places for version or configuration drift to break things, which is exactly what the dependency mismatch above demonstrated firsthand.


---

## Bonus: Routing Modes (if attempted)

### Advanced Router
- How does the dynamic routing decide which agents to call?
- What callback patterns did you use?

### Parallel Router
- How does parallel execution improve latency?
- What synthesis strategy did you use to combine results?

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | | | |
| Advanced (Dynamic) | | | |
| Parallel | | | |

---

## Key Learnings
1. Documentation can be wrong in ways that matter. The `a2a_compat.py` docstring stated `google-adk==1.9.0`, but the actual required version had to be reverse-engineered from what the given code's imports required. When docs and code disagree, the code is the real spec.
2. Unbounded version constraints (`>=X.Y.Z` with no ceiling) in a shared `requirements.txt` are a real liability, since a library's API can change shape entirely between what look like minor version jumps.
3. A2A's value isn't obvious until you consider removing it. `RemoteA2aAgent` and AgentCards add real overhead for a two-agent system this small, but they're what make the Support Agent and Customer Data Agent genuinely swappable and independent rather than secretly coupled through shared imports.

## Ideas for Improvement
- Pin exact dependency versions (`==`, not `>=`) in the starter `requirements.txt`, so the version-mismatch debugging isn't an unplanned part of every student's Part 2 experience.
- Add a version-check step to `run_agents.py` that fails fast with a clear message if the installed `google-adk`/`a2a-sdk` don't match what `a2a_compat.py` expects, rather than surfacing as a confusing downstream `AttributeError`.
