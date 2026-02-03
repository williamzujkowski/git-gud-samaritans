# Git-Gud-Samaritans: Claude CLI Bootstrap Prompt

Copy and paste this prompt into Claude CLI to initialize the project, verify configuration, and fix any issues.

---

## Prompt

```
You are bootstrapping the git-gud-samaritans project. Follow this systematic verification workflow:

## Phase 1: Project Understanding
1. Read CLAUDE.md to understand project context, structure, and conventions
2. Read CODING_STANDARDS.md for detailed coding standards
3. Review the project structure and verify all expected directories/files exist

## Phase 2: Environment Verification
1. Check Python version (requires 3.10+)
2. Verify .env file exists (copy from .env.example if missing)
3. Check if GITHUB_TOKEN is set (warn if missing, don't block)
4. Verify virtual environment setup

## Phase 3: Dependency Installation
1. Create virtual environment if not exists: `python -m venv venv`
2. Activate and install dependencies: `pip install -e ".[dev]"`
3. Install pre-commit hooks: `pre-commit install`
4. Verify all dependencies installed correctly

## Phase 4: Code Quality Verification
1. Run formatter check: `black --check src/ tests/`
2. Run import sort check: `isort --check src/ tests/`
3. Run linter: `flake8 src/ tests/`
4. Run type checker: `mypy src/`
5. Fix any issues found automatically where possible

## Phase 5: Test Verification
1. Create missing test files if needed (tests/ should mirror src/ structure)
2. Run test suite: `pytest -v`
3. Check coverage: `pytest --cov=src/git_gud_samaritans`
4. Report any failing tests

## Phase 6: Configuration Verification
1. Validate config/mcp-config.json is valid JSON
2. Validate config/nexus-config.yaml is valid YAML
3. Validate config/discovery-rules.yaml is valid YAML
4. Validate config/triage-scoring.yaml is valid YAML
5. Check pyproject.toml for completeness

## Phase 7: CLI Verification
1. Verify CLI entry point works: `python -m git_gud_samaritans.cli --help`
2. Test each subcommand's help: discover, triage, contribute, auto, metrics
3. Report any import errors or missing dependencies

## Phase 8: Summary Report
Generate a status report with:
- ✅ What's working correctly
- ⚠️ Warnings (non-blocking issues)
- ❌ Errors that need attention
- 📝 Recommended next steps

## Execution Rules
- Fix formatting/linting issues automatically
- Create missing __init__.py files if needed
- Create placeholder test files if missing
- Do NOT modify .env or add real credentials
- Do NOT make changes that would break existing functionality
- Commit fixes with message: "chore: bootstrap project setup and fixes"

Start by reading CLAUDE.md, then proceed through each phase systematically. Report progress as you go.
```

---

## Alternative: Shorter Quick-Start Prompt

```
Bootstrap git-gud-samaritans:

1. Read CLAUDE.md and CODING_STANDARDS.md
2. Install deps: `pip install -e ".[dev]" && pre-commit install`
3. Run checks: `black --check src/` `isort --check src/` `flake8 src/` `mypy src/`
4. Fix any issues found
5. Run tests: `pytest -v`
6. Verify CLI: `python -m git_gud_samaritans.cli --help`
7. Report status with ✅/⚠️/❌ for each component

Fix issues automatically. Commit fixes as "chore: bootstrap fixes".
```

---

## Interactive Session Prompt

For an interactive session where you want Claude to guide you through setup:

```
I'm setting up the git-gud-samaritans project for the first time. Please:

1. Walk me through the project structure (read CLAUDE.md first)
2. Help me set up my development environment step by step
3. Verify everything is configured correctly
4. Fix any issues you find
5. Show me how to run the CLI commands

Ask me questions if you need any input (like environment preferences). Let's start!
```

---

## CI/CD Verification Prompt

For verifying the project is CI-ready:

```
Verify git-gud-samaritans is CI/CD ready:

1. All code passes: black, isort, flake8, mypy
2. All tests pass with >80% coverage
3. All config files are valid
4. CLI entry points work
5. No hardcoded secrets or credentials
6. .gitignore covers all generated files
7. pyproject.toml has correct metadata

Create a GitHub Actions workflow file at .github/workflows/ci.yml if missing.
Fix any issues. Report final status.
```

---

## Post-Bootstrap Development Prompt

After initial setup, use this to start working on features:

```
I'm working on git-gud-samaritans. Before we start:

1. Verify the project is in a clean state (no uncommitted changes to track)
2. Check that tests pass
3. Review any TODOs in the codebase

Then let's work on: [YOUR TASK HERE]

Follow the patterns in CLAUDE.md and CODING_STANDARDS.md for any new code.
```
