# Connect an AI assistant over MCP

MCP server: **`https://sandbox.wbx.cz/mcp`** (streamable HTTP).

## Sign in with OAuth (assistants in a browser or app)

| Client | Steps |
|---|---|
| claude.ai / Claude desktop | Customize → Connectors → *Add custom connector*. Name `WBX Sandbox`, URL `https://sandbox.wbx.cz/mcp`, leave the advanced OAuth fields empty → *Add* → sign in to WBX Sandbox → *Allow access*. In a chat: **+** → Connectors → turn on WBX Sandbox. Works on every Claude plan (Free allows one custom connector). |
| Claude Team / Enterprise | An organisation Owner adds it once: Organization settings → Connectors → Add → Custom. Members then click *Connect*. |
| ChatGPT | Settings → Apps & Connectors → Advanced settings → turn on *Developer mode* (Plus, Pro, Business, Enterprise, Edu; an admin may need to allow it). Back in Apps & Connectors → *Create*: name `WBX Sandbox`, URL `https://sandbox.wbx.cz/mcp`, Authentication OAuth → sign in → *Allow access*. |
| Claude Code | `claude mcp add --transport http wbxsandbox https://sandbox.wbx.cz/mcp`, then run `/mcp` and sign in in the browser. |

Approving access creates an API key named "… (connected app)" in your team (portal → API keys); delete it there to disconnect. Only team owners and admins can approve.

## API key (servers, CI, headless agents)

Send the key as a bearer token:

```bash
claude mcp add --transport http wbxsandbox https://sandbox.wbx.cz/mcp \
  --header "Authorization: Bearer $WBXSANDBOX_API_KEY"
```

Clients that only speak stdio can use the `wbxsandbox-mcp` helper (macOS, Windows, Linux; download in the portal → Docs → SDKs & MCP):

```json
{
  "mcpServers": {
    "wbxsandbox": {
      "command": "/path/to/wbxsandbox-mcp",
      "args": ["-url", "https://sandbox.wbx.cz", "-key", "YOUR_API_KEY"]
    }
  }
}
```

Keep keys out of chats, logs and repositories.

## Tools

Sandboxes: `create_sandbox`, `run_command`, `run_code`, `write_file`, `read_file`, `list_files`, `list_sandboxes`, `list_templates`, `set_timeout`, `get_public_url`, `kill_sandbox`.
Jobs and batches: `run_job`, `get_job_summary`, `get_job_result`, `get_job_logs`, `list_job_artifacts`, `download_job_artifact`, `cancel_job`, `retry_job`, `wait_jobs`, `run_batch`, `get_batch_summary`, `cancel_batch`.
Account: `get_budget`, `get_compute_classes`.

Your client shows the current list after connecting – check it there rather than relying on this page.

## Prompts

See [prompts.md](prompts.md) for prompts we have run end to end.
