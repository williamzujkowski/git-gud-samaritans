# CLAUDE.md

> This file provides context and guidelines for AI agents working on this codebase.

## Project Overview

**git-gud-samaritans** is an AI-powered open source contribution engine that identifies struggling repositories and helps fix them using [nexus-agents](https://github.com/williamzujkowski/nexus-agents) orchestration.

**Mission**: Find repos that need help → Triage issues → Contribute quality PRs → Make pipelines green.

**Name Origin**: A mashup of the "git gud" gaming meme + Good Samaritans, inspired by `sudo make it green` and `sed 's/red/green/g'`.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/williamzujkowski/git-gud-samaritans.git
cd git-gud-samaritans

# Install with uv (recommended)
uv sync --all-extras

# Or with pip
pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install

# Copy and configure environment
cp .env.example .env
# Edit .env to add your GITHUB_TOKEN

# Verify setup
make check  # or: uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest

# Run the CLI
uv run ggs --help
uv run ggs discover --language python --min-stars 100
```

## MCP Integration with nexus-agents

This project integrates with [nexus-agents](https://github.com/williamzujkowski/nexus-agents) v2.4.0 via the Model Context Protocol (MCP) for multi-agent orchestration.

### Prerequisites

1. **nexus-agents installed globally**:
   ```bash
   # nexus-agents should be in your PATH
   which nexus-agents  # Should return a path
   nexus-agents --version  # Should show v2.4.0+
   ```

2. **Claude Code with MCP support**: The `.claude/settings.local.json` configures the MCP server automatically.

### MCP Configuration

The project uses Claude Code's `.mcp.json` file for MCP server configuration:

1. **`.mcp.json`** (project root) - MCP server definitions:
   ```json
   {
     "mcpServers": {
       "nexus-agents": {
         "command": "nexus-agents",
         "args": []
       }
     }
   }
   ```

2. **`.claude/settings.local.json`** - Enables project MCP servers:
   ```json
   {
     "enableAllProjectMcpServers": true
   }
   ```

3. **`config/mcp-config.json`** - Full MCP server definitions and tool schemas for external use.

**Verify MCP is loaded**: Run `/mcp` in Claude Code to see connected servers.

### Available nexus-agents Workflows

When the MCP server is running, these workflows are available:

| Workflow | Description | Agents Used |
|----------|-------------|-------------|
| `research` | Understand a codebase | researcher |
| `plan` | Create a contribution plan | researcher, planner |
| `implement` | Implement planned changes | researcher, planner, implementer |
| `full_contribution` | Complete contribution workflow | all agents |

### Using nexus-agents in Development

```bash
# Verify nexus-agents installation
nexus-agents verify
nexus-agents doctor

# Start nexus-agents MCP server manually (for debugging)
nexus-agents  # Starts MCP server with stdio transport (default)

# The MCP server provides tools like:
# - orchestrate: Task orchestration with TechLead coordination
# - create_expert: Dynamic expert agent creation
# - run_workflow: Execute workflow templates
# - delegate_to_model: Route task to optimal model

# CLI commands (standalone, outside MCP):
nexus-agents orchestrate "Implement feature X with tests"
nexus-agents workflow list
nexus-agents expert list
```

## Tech Stack

- **Language**: Python 3.10+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (fast, modern Python package manager)
- **Linting/Formatting**: [ruff](https://github.com/astral-sh/ruff) (replaces flake8, black, isort)
- **Type Checking**: mypy (strict mode)
- **CLI Framework**: Click + Rich (for terminal UI)
- **GitHub API**: PyGithub
- **Configuration**: YAML (pydantic-settings)
- **Logging**: structlog
- **Orchestration**: nexus-agents via MCP (Model Context Protocol)
- **Testing**: pytest + pytest-cov + pytest-asyncio

## Project Structure

```
git-gud-samaritans/
├── .mcp.json                   # MCP server definitions for Claude Code
├── .claude/                    # Claude Code configuration
│   ├── settings.local.json     # Project permissions and settings
│   └── rules/                  # Context rules for Claude
├── config/                     # Configuration files
│   ├── mcp-config.json         # MCP server definitions
│   ├── nexus-config.yaml       # Agent orchestration settings
│   ├── discovery-rules.yaml    # Repo/issue filtering criteria
│   └── triage-scoring.yaml     # Issue scoring weights
├── src/git_gud_samaritans/
│   ├── cli.py                  # Main CLI entry point
│   ├── discovery/              # Find repos/issues that need help
│   │   ├── github_scanner.py   # GitHub API wrapper
│   │   ├── issue_finder.py     # Issue discovery logic
│   │   └── pr_analyzer.py      # Stale PR detection
│   ├── triage/                 # Score issues for contribution fitness
│   │   ├── scorer.py           # Main scoring engine
│   │   ├── complexity.py       # Complexity estimation
│   │   └── fit_analyzer.py     # AI suitability analysis
│   ├── contribute/             # Execute contribution workflow
│   │   ├── orchestrator.py     # Main workflow coordinator
│   │   ├── pr_generator.py     # PR creation
│   │   └── verification.py     # Pre-submit checks
│   └── utils/                  # Shared utilities
├── tests/                      # Test suite (mirrors src/ structure)
├── Makefile                    # Common development commands
├── pyproject.toml              # Project configuration (ruff, mypy, pytest)
└── uv.lock                     # Lockfile for reproducible builds
```

## Development Commands

Use the Makefile for common tasks (all commands use `uv run` internally):

```bash
make install      # Install package with uv
make install-dev  # Install with development dependencies
make sync         # Sync environment from lockfile
make test         # Run tests
make coverage     # Run tests with coverage
make lint         # Run ruff linter
make format       # Format code with ruff
make typecheck    # Run mypy
make check        # Run all checks (lint + typecheck + test)
make clean        # Clean build artifacts
make help         # Show all available commands
```

Or run directly with uv:

```bash
# Sync dependencies from lockfile
uv sync --all-extras

# Run tests
uv run pytest
uv run pytest --cov=src/git_gud_samaritans  # with coverage

# Lint and format
uv run ruff check src/ tests/           # check for issues
uv run ruff check --fix src/ tests/     # auto-fix issues
uv run ruff format src/ tests/          # format code
uv run mypy src/                        # type check

# CLI usage
uv run ggs discover --language python --min-stars 50
uv run ggs triage https://github.com/owner/repo/issues/123
uv run ggs contribute https://github.com/owner/repo/issues/123 --dry-run
```

## Code Style

- **Linting/Formatting**: ruff (replaces flake8, black, isort)
  - Line length: 88
  - Rules: E, F, I, B, UP, C4, SIM, RUF
- **Types**: Full type hints required (mypy strict mode)
- **Docstrings**: Google style
- **Logging**: Use structlog, not print statements

```python
# Good
def score_issue(self, issue_url: str) -> TriageResult:
    """Score an issue for contribution fitness.

    Args:
        issue_url: Full URL to the GitHub issue

    Returns:
        TriageResult with score and breakdown
    """
    logger.info("scoring_issue", issue_url=issue_url)
    ...

# Bad
def score_issue(self, url):
    print(f"Scoring {url}")
    ...
```

## Key Patterns

### Dataclasses for Results
All result types should be dataclasses with `to_dict()` methods:

```python
@dataclass
class SomeResult:
    field: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {"field": self.field, "score": self.score}
```

### ClassVar for Mutable Class Attributes
Use `ClassVar` annotation for mutable class-level constants:

```python
from typing import ClassVar

class MyClass:
    DEFAULT_VALUES: ClassVar[list[str]] = ["a", "b", "c"]
    CONFIG: ClassVar[dict[str, int]] = {"timeout": 30}
```

### Error Handling
Catch specific exceptions, log with context, re-raise or return error results:

```python
try:
    result = self.scanner.search_issues(query)
except GithubException as e:
    logger.error("github_search_error", error=str(e), query=query)
    raise
```

### Configuration Loading
Use YAML configs with sensible defaults:

```python
def _load_config(self, config_path: str | None) -> dict[str, Any]:
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            result = yaml.safe_load(f)
            return result if isinstance(result, dict) else {}
    return {}
```

## Agent Integration Patterns

When implementing agent integration with nexus-agents:

1. **Use iterative loops with convergence checks**:
   ```python
   for iteration in range(max_iterations):
       result = await agent.execute(task)
       if result.confidence >= convergence_threshold:
           break
   ```

2. **Respect rate limits and token budgets**:
   ```python
   if remaining_requests < RATE_LIMIT_BUFFER:
       await asyncio.sleep(calculate_backoff())
   ```

3. **Always verify changes before submission**:
   ```python
   verification = verifier.verify(repo_path, run_tests=True, run_lint=True)
   if not verification["passed"]:
       raise ContributionError("Verification failed")
   ```

4. **Include proper attribution in PRs**:
   ```markdown
   *This PR was generated by git-gud-samaritans using nexus-agents*
   ```

## Safety & Rate Limits

**IMPORTANT**: This tool interacts with real GitHub repos. Be a good citizen:

1. **Rate Limits**: GitHub API has limits. The scanner maintains a buffer (`GITHUB_RATE_LIMIT_BUFFER=100`)
2. **PR Limits**: Default `MAX_DAILY_PRS=5` to avoid spamming repos
3. **Protected Files**: Never modify `.github/workflows/*`, `*.lock`, `.env*`
4. **Dry Run**: Always test with `--dry-run` first
5. **Verification**: Run tests and linting before any PR submission

## Environment Variables

**Required:**
- `GITHUB_TOKEN` — GitHub PAT with `repo` scope (create at https://github.com/settings/tokens)

**Optional** (see `.env.example` for full list):
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXUS_AGENTS_PATH` | `~/git/nexus-agents` | Path to nexus-agents installation |
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `DRY_RUN` | `false` | Prevent actual PR submissions |
| `MAX_DAILY_PRS` | `5` | Daily PR submission limit |
| `USE_FORKS` | `true` | Fork repos before contributing |

## Testing Guidelines

- Unit tests in `tests/` mirror the `src/` structure
- Mock external APIs (GitHub, etc.) — never hit real APIs in tests
- Use pytest fixtures for common setup
- Test both success and error paths
- Maintain >80% coverage

```python
def test_score_issue_returns_result(mocker):
    """Scoring an issue should return a TriageResult."""
    mocker.patch.object(GitHubScanner, 'get_issue', return_value=mock_issue)

    scorer = IssueScorer()
    result = scorer.score("https://github.com/owner/repo/issues/123")

    assert isinstance(result, TriageResult)
    assert 0 <= result.score <= 100
```

## Common Tasks

### Adding a New Discovery Filter
1. Add filter criteria to `config/discovery-rules.yaml`
2. Implement filter logic in `discovery/issue_finder.py`
3. Add tests in `tests/test_discovery/`

### Adding a New Scoring Factor
1. Add weight to `config/triage-scoring.yaml`
2. Implement scoring method in `triage/scorer.py`
3. Update `ScoreBreakdown` dataclass
4. Add tests in `tests/test_triage/`

### Extending the Contribution Workflow
1. Define agent role in `config/nexus-config.yaml`
2. Add workflow step in `contribute/orchestrator.py`
3. Create prompt template in `prompts/contribute/` (if needed)
4. Add tests in `tests/test_contribute/`

## Gotchas & Warnings

1. **GitHub Search API Quirks**: Search queries have a different rate limit than the REST API. The `IssueFinder` handles pagination but be aware of limits.

2. **Issue URL Parsing**: Always validate issue URLs before processing. The `_parse_issue_url` method expects `https://github.com/owner/repo/issues/123` format.

3. **Stale Data**: GitHub's search index can be delayed. Recently updated issues might not appear immediately.

4. **Fork vs Direct Push**: Default is to fork repos before contributing (`USE_FORKS=true`). Direct push requires write access.

5. **Test Infrastructure Detection**: The `Verifier` auto-detects test commands but may fail on non-standard setups. Check `verification.py` for supported patterns.

6. **MCP Server Startup**: The nexus-agents MCP server may take a few seconds to initialize. If tools aren't available immediately, wait and retry.

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

feat(discovery): add GitLab support
fix(triage): handle rate limiting gracefully
docs: update MCP configuration examples
test(contribute): add integration tests
chore: update dependencies
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## CI/CD

The project uses GitHub Actions for CI:
- **On push/PR**: Runs ruff (lint + format check), mypy, and pytest
- **Python versions**: 3.10, 3.11, 3.12
- **Package manager**: uv with caching enabled
- **Coverage**: Reports to Codecov

---

*"git gud && help-others"*
