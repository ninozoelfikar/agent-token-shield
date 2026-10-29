---
name: token-shield
description: Universal token efficiency harness. Enforces 0-token local syntax validation, modular execution without reinventing the wheel, and loop avoidance.
---

# Token Shield - Agent Operating Doctrine

When `token-shield` is active, adhere strictly to these token-conservation principles:

### 1. Zero-Token Local Syntax Validation
Before reporting code changes as complete, ALWAYS run the local syntax probe:
```bash
token-shield probe <path-to-modified-file>
```
* **Cost**: 0 LLM tokens (runs natively via OS bytecode/AST parser).
* If the probe reports a syntax error, fix it directly before declaring the task done.

### 2. Modular Workshop Doctrine (Anti-Reinventing)
* Treat tools, templates, and scripts as permanent modules.
* Never rebuild or write new scaffolding scripts from scratch if an existing tool or template can fulfill the requirement.
* Reuse existing functions, modules, and configurations.

### 3. Loop Breaker Awareness
* If an execution fails, DO NOT re-run the exact same command or payload.
* The system runtime automatically terminates identical failed attempts on the 3rd repetition.
* Analyze the failure output, change the hypothesis/approach, or report the obstacle to the user.

### 4. Telemetry Audit
To verify token consumption and cache hit ratio:
```bash
token-shield stats --days 7
```
