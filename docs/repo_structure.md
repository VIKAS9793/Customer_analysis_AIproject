# FinConnectAI Clean Folder Structure

```
/FinConnectAI/
│
├── app/ # All MCP agents, FastAPI routes, core logic
├── ui/ # Gradio UI files (no dummy UIs)
├── connectors/ # Mock API connectors (e.g. core banking)
├── auth/ # RBAC configs, consent-related logic
├── scripts/ # Shell scripts for local or demo runs
├── logs/ # JSON logs for eval, integration, consent
├── docs/ # OpenAPI, repo_structure, architecture files
└── tests/ # Pytest files only, no legacy test folders
```

**Rules:**
- No placeholder folders.
- No nested agent folders unless required.
- Only documented agents and modules allowed.
- All code tied to a task from this JSON plan.
