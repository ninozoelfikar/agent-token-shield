# Agent Token Shield 🛡️⚡

> **Cut AI Coding Agent Token Waste by 38% – 58% Automatically.**  
> A lightweight, universal agent harness that eliminates repetitive loops, monolithic context dumping, and LLM-based syntax checking.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)]()
[![Tokens Saved: 38%–58%](https://img.shields.io/badge/Token_Savings-38%25_to_58%25-orange.svg)]()
[![Cache Hit: 94%+](https://img.shields.io/badge/Cache_Hit_Ratio-94.3%25-green.svg)]()

---

## 📌 The Problem: Why Coding Agents Burn Tokens

Modern AI coding agents (Antigravity, Gemini CLI, Claude Code, Aider, Cursor) frequently suffer from three major inefficiencies:

1. **Monolithic Context Injection**: Dumping thousands of lines of documentation and state files on turn 1, forcing every subsequent interaction to re-read and bill for massive context.
2. **Infinite Error Loops (The Death Spiral)**: When a tool fails, agents often retry the exact same failing command 5–10 times with trivial whitespace changes, burning 50,000–200,000 tokens in minutes.
3. **LLM-Based Syntax Checking**: Asking the model to "verify if this code has syntax errors" instead of using free, instantaneous local compilers.
4. **Disposable Agent Scaffolding**: Rebuilding helper scripts, CLI flags, and boilerplate from scratch on every user prompt.

---

## 📊 Empirical Benchmark (Real-World 2.8 Billion Token Dataset)

In an production environment spanning 26 active working days and 21,044 model calls, **Agent Token Shield** was deployed to measure real impact:

| Metric | Before Token Shield (21 Days) | With Token Shield (Active) | Delta (% Saved) |
| :--- | :---: | :---: | :---: |
| **Average Daily Tokens** | 119,526,005 | 73,855,082 | **-38.21%** |
| **Fresh Uncached Input** | 9,396,656 | 3,961,384 | **-57.84%** |
| **Fresh Input per Call** | 10,516 tokens | 7,167 tokens | **-31.85%** |
| **Model Calls / Day** | 893.5 calls | 552.8 calls | **-38.14%** |
| **Context Cache Hit Ratio** | 91.76% | **94.27%** | **+2.51%** |

---

## 🏗️ 5 Pillars of Token Shield

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AGENT TOKEN SHIELD ARCHITECTURE                      │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Permanent Modular Workshop  │ Tools & SOPs live as permanent molds  │
│ 2. Context Lazy-Loading        │ <250-token Radar Boot; load on-demand │
│ 3. Zero-Token Local Probe      │ OS-level syntax validation (0 tokens) │
│ 4. Runtime Anti-Loop Guard     │ Hard-denies repetitive tool calls     │
│ 5. Static Context Prefix       │ Maximize Provider Context Caching     │
└────────────────────────────────┴───────────────────────────────────────┘
```

1. **Permanent Modular Workshop**: Agents treat existing tools and playbook templates as permanent modules on a workshop wall. Never rewrite scaffolding from scratch.
2. **Context Lazy-Loading**: Session start injects a dense, **<250-token Radar Index**. Full module details are only fetched when explicitly referenced.
3. **Zero-Token Local Probe**: Validates Python (`ast.parse`), Node.js/JS (`node --check`), JSON, and Bash (`bash -n`) locally in ~2ms. Costs **0 LLM tokens**.
4. **Runtime Anti-Loop Guard**: Computes a SHA-1 signature of tool names and payloads. If an identical action is executed 3 times in a 12-turn window, the runtime **hard-denies** execution and forces the agent to alter strategy.
5. **Static Context Prefix**: Aligns system prompts and invariants to maximize LLM provider context caching (Gemini, Claude, OpenAI), keeping cache hits above 94%.

---

## 🚀 Quickstart & Installation

### One-Line Install (Linux / macOS)

```bash
git clone https://github.com/your-username/agent-token-shield.git
cd agent-token-shield
./install.sh
```

The installer will:
1. Symlink `token-shield` CLI to `~/.local/bin/token-shield`.
2. Register lifecycle hooks into `~/.gemini/config/hooks.json` (if Antigravity/Gemini CLI is installed).
3. Link the `token-shield` skill into `~/.gemini/skills/`.

---

## 💻 CLI Usage

### 1. Zero-Token Local Syntax Probe
Test your files instantly before committing or reporting task completion:
```bash
token-shield probe src/app.py
token-shield probe frontend/server.js
token-shield probe config.json
```
Output:
```
✓ [PASS 0-Token] src/app.py: Python syntax OK
```

### 2. View Token Telemetry & Savings
Inspect real-time token metrics, fresh input, and cache hit ratio:
```bash
token-shield stats --days 7
```

### 3. Generate Lean Radar Manifest
Generate a high-density, <250-token workspace index:
```bash
token-shield radar --dir .
```

---

## 🔌 Platform Compatibility & Integration

Agent Token Shield is designed to be **100% platform-agnostic**:

| Environment | Integration Point | Adapter Location |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini CLI** | Native Lifecycle Hooks (`SessionStart`, `PreToolUse`, `PreInvocation`) | `adapters/antigravity/` |
| **Claude Code (Anthropic)** | Hook middleware & MCP server wrapper | `adapters/claude/` |
| **Cursor / Windsurf** | Pre-save linting & `.cursorrules` integration | `skills/token-shield/` |
| **Custom Frameworks (LangGraph, CrewAI)** | Python Middleware decorator (`TokenShieldMiddleware`) | `adapters/generic/` |

### Python Middleware Example (LangGraph / CrewAI):
```python
from adapters.generic.middleware import TokenShieldMiddleware

shield = TokenShieldMiddleware(repeat_limit=3)

# Intercept tool call
result = shield.intercept_tool(
    session_id="session_123",
    tool_name="edit_file",
    tool_args={"path": "main.py", "target": "a", "replacement": "b"},
    execute_fn=actual_tool_executor
)
```

---

## 📁 Repository Structure

```text
agent-token-shield/
├── README.md               # Architecture documentation & benchmarks
├── LICENSE                 # MIT License
├── install.sh              # One-line installer script
├── uninstall.sh            # Clean rollback script
├── cli.py                  # Main CLI entrypoint
├── bin/
│   └── token-shield        # Executable runner
├── core/
│   ├── probe.py            # Zero-token deterministic syntax validator
│   ├── loop_guard.py       # Sliding-window anti-loop guard
│   ├── lazy_loader.py      # Compact <250-token radar indexer
│   └── telemetry.py        # Token audit & cache-hit calculator
├── adapters/
│   ├── antigravity/        # Gemini / Antigravity lifecycle hooks
│   ├── claude/             # Claude Code hook integration
│   └── generic/            # Universal Python agent middleware
├── skills/
│   └── token-shield/       # Agent skill specification (SKILL.md)
└── tests/
    └── test_shield.py      # Unit test suite
```

---

## 🧪 Testing

Run the included unit test suite:
```bash
python3 tests/test_shield.py
```

---

## 📄 License
MIT License. Free to use, modify, and distribute in personal and commercial AI workflows.
