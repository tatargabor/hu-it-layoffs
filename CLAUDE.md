## Persistent Memory

This project uses persistent memory (shodh-memory) across sessions. Memory context is automatically injected into `<system-reminder>` tags in your conversation — **you MUST read and use this context**.

**IMPORTANT: On EVERY prompt, check for injected memory context (system-reminder tags labeled "PROJECT MEMORY", "PROJECT CONTEXT", or "MEMORY: Context for this command"). When present, acknowledge and use it BEFORE doing independent research. If a memory directly answers the user's question or provides a known fix, cite it explicitly (e.g., "From memory: ...") instead of re-investigating from scratch. This applies to every turn, not just the first one.**

**How it works:**
- Session start → relevant memories loaded as system-reminder
- Every prompt → topic-based recall injected as system-reminder
- Every tool use → relevant past experience injected as system-reminder
- Tool errors → past fixes surfaced automatically
- Session end → insights extracted and saved

**Active (MCP tools):** You also have MCP memory tools available (`remember`, `recall`, `proactive_context`, etc.) for deeper memory interactions when automatic context isn't enough.

**Emphasis (use sparingly):**
- `echo "<insight>" | wt-memory remember --type <Decision|Learning|Context> --tags source:user,<topic>` — mark something as HIGH IMPORTANCE
- `wt-memory forget <id>` — suppress or correct a wrong memory
- Most things are remembered automatically. Only use `remember` for emphasis.
