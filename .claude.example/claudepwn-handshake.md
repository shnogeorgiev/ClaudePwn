# ClaudePwn Handshake

- Active session: sessions/.current
- Session workspace (host): sessions/<session>/workspace
- Session workspace (container): /workspace
- Claude Code project root: same folder as claudepwn.py

Flows:
- CLI:
  - sessions_create / sessions_use
  - launch_claude
- Claude Code:
  - agent_run / agent_enumerate / agent_exploit
  - Uses MCP tools: run_command, read_file, write_file, list_dir, tail_log
- Shared state: /workspace contents
