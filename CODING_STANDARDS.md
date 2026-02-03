# Coding Standards

> Detailed coding standards and best practices for git-gud-samaritans development.

## Table of Contents

- [Python Style Guide](#python-style-guide)
- [Type Hints](#type-hints)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Testing](#testing)
- [Documentation](#documentation)
- [Git Workflow](#git-workflow)
- [Security](#security)

---

## Python Style Guide

### Formatting

We use **Black** for code formatting and **isort** for import sorting.

```bash
# Format all code
black src/ tests/
isort src/ tests/

# Check formatting without modifying
black --check src/ tests/
isort --check src/ tests/
```

Configuration is in `pyproject.toml`. Do not override these settings.

### Imports

Order imports as follows (isort handles this automatically):

1. Standard library
2. Third-party packages
3. Local imports

```python
# Good
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
import yaml
from github import Github, GithubException

from git_gud_samaritans.discovery import GitHubScanner
from git_gud_samaritans.triage import TriageResult
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase_underscore | `issue_finder.py` |
| Classes | PascalCase | `IssueScorer` |
| Functions | lowercase_underscore | `score_issue()` |
| Constants | UPPERCASE_UNDERSCORE | `MAX_RESULTS` |
| Private | leading underscore | `_parse_url()` |

### Line Length

- Maximum 88 characters (Black default)
- Exceptions: URLs, long strings that shouldn't be broken

### String Formatting

Use f-strings for string interpolation:

```python
# Good
message = f"Found {count} issues in {repo}"

# Avoid
message = "Found {} issues in {}".format(count, repo)
message = "Found %d issues in %s" % (count, repo)
```

---

## Type Hints

### Required Everywhere

All functions must have complete type hints:

```python
# Good
def find_issues(
    self,
    labels: list[str] | None = None,
    min_stars: int = 10,
    max_results: int = 20
) -> list[dict[str, Any]]:
    ...

# Bad - missing types
def find_issues(self, labels=None, min_stars=10, max_results=20):
    ...
```

### Modern Syntax (Python 3.10+)

Use modern type hint syntax:

```python
# Good (Python 3.10+)
def process(items: list[str] | None = None) -> dict[str, Any]:
    ...

# Avoid (legacy)
from typing import List, Dict, Optional, Union
def process(items: Optional[List[str]] = None) -> Dict[str, Any]:
    ...
```

### Type Aliases

Define type aliases for complex types:

```python
from typing import TypeAlias

IssueDict: TypeAlias = dict[str, Any]
ScoreBreakdownDict: TypeAlias = dict[str, float]

def score_all(self, issues: list[IssueDict]) -> list[ScoreBreakdownDict]:
    ...
```

### Dataclasses for Structured Data

Use dataclasses for structured return types:

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class TriageResult:
    """Result of triaging an issue."""
    issue_url: str
    score: float
    recommendation: str
    risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "issue_url": self.issue_url,
            "score": self.score,
            "recommendation": self.recommendation,
            "risks": self.risks
        }

    @property
    def is_good_candidate(self) -> bool:
        """Check if this is a good contribution candidate."""
        return self.score >= 60
```

---

## Error Handling

### Specific Exceptions

Catch specific exceptions, not bare `except`:

```python
# Good
try:
    result = self.client.search_issues(query)
except GithubException as e:
    logger.error("github_api_error", error=str(e))
    raise
except RateLimitExceededException as e:
    logger.warning("rate_limit_exceeded", reset_at=e.reset_at)
    raise

# Bad
try:
    result = self.client.search_issues(query)
except:  # Never do this
    pass
```

### Custom Exceptions

Define custom exceptions for domain-specific errors:

```python
class GitGudError(Exception):
    """Base exception for git-gud-samaritans."""
    pass

class DiscoveryError(GitGudError):
    """Error during issue discovery."""
    pass

class TriageError(GitGudError):
    """Error during issue triage."""
    pass

class ContributionError(GitGudError):
    """Error during contribution workflow."""
    pass
```

### Result Objects for Expected Failures

For operations that can fail in expected ways, return result objects:

```python
@dataclass
class ContributionResult:
    success: bool
    error: str | None = None
    pr_url: str | None = None

# Usage
def contribute(self, issue_url: str) -> ContributionResult:
    try:
        pr_url = self._submit_pr(...)
        return ContributionResult(success=True, pr_url=pr_url)
    except ContributionError as e:
        return ContributionResult(success=False, error=str(e))
```

---

## Logging

### Use structlog

All logging should use structlog for structured, contextual logging:

```python
import structlog

logger = structlog.get_logger()

# Good - structured with context
logger.info(
    "issue_scored",
    issue_url=issue_url,
    score=result.score,
    recommendation=result.recommendation
)

# Bad - unstructured string formatting
logger.info(f"Scored issue {issue_url}: {result.score}")
```

### Log Levels

| Level | Use For |
|-------|---------|
| `DEBUG` | Detailed diagnostic info |
| `INFO` | Normal operation events |
| `WARNING` | Unexpected but handled situations |
| `ERROR` | Errors that prevent operation completion |

```python
logger.debug("parsing_issue_url", url=url)
logger.info("found_issues", count=len(issues), query=query)
logger.warning("rate_limit_low", remaining=remaining, reset_at=reset_at)
logger.error("contribution_failed", issue_url=url, error=str(e))
```

### Context Binding

Bind context for a series of related operations:

```python
def contribute(self, issue_url: str) -> ContributionResult:
    log = logger.bind(issue_url=issue_url)

    log.info("starting_contribution")
    # ... operations ...
    log.info("contribution_complete", pr_url=pr_url)
```

---

## Testing

### Structure

Tests mirror the source structure:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_discovery/
│   ├── test_github_scanner.py
│   ├── test_issue_finder.py
│   └── test_pr_analyzer.py
├── test_triage/
│   ├── test_scorer.py
│   └── test_complexity.py
└── test_contribute/
    └── test_orchestrator.py
```

### Naming

```python
# Test files: test_<module>.py
# Test functions: test_<what>_<condition>_<expected>

def test_score_issue_with_valid_url_returns_result():
    ...

def test_score_issue_with_invalid_url_raises_error():
    ...
```

### Fixtures

Define fixtures in `conftest.py`:

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_github_scanner():
    """Provide a mocked GitHubScanner."""
    scanner = MagicMock()
    scanner.search_issues.return_value = [
        {"repo": "owner/repo", "issue_number": 123, "title": "Test"}
    ]
    return scanner

@pytest.fixture
def sample_issue():
    """Provide a sample issue dictionary."""
    return {
        "repo": "owner/repo",
        "issue_number": 123,
        "title": "Fix bug",
        "url": "https://github.com/owner/repo/issues/123",
        "labels": ["bug", "good first issue"]
    }
```

### Mocking External Services

Always mock external services:

```python
def test_discovery_returns_issues(mock_github_scanner):
    finder = IssueFinder(scanner=mock_github_scanner)

    results = finder.find(labels=["good first issue"])

    assert len(results) > 0
    mock_github_scanner.search_issues.assert_called_once()

# Never hit real APIs in tests
# ❌ Don't do this:
def test_real_api():
    scanner = GitHubScanner(token=os.getenv("GITHUB_TOKEN"))
    results = scanner.search_issues("is:open")  # Hits real API!
```

### Async Tests

Use `pytest-asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Coverage

Maintain >80% test coverage:

```bash
pytest --cov=src/git_gud_samaritans --cov-report=html
```

---

## Documentation

### Docstrings

Use Google style docstrings:

```python
def score_issue(
    self,
    issue_url: str,
    include_breakdown: bool = True
) -> TriageResult:
    """Score an issue for contribution fitness.

    Analyzes the issue and repository to determine suitability
    for AI-assisted contribution.

    Args:
        issue_url: Full URL to the GitHub issue
            (e.g., https://github.com/owner/repo/issues/123)
        include_breakdown: Whether to include detailed score breakdown

    Returns:
        TriageResult containing the score and analysis

    Raises:
        TriageError: If the issue cannot be analyzed
        ValueError: If the URL format is invalid

    Example:
        >>> scorer = IssueScorer()
        >>> result = scorer.score_issue("https://github.com/owner/repo/issues/123")
        >>> print(f"Score: {result.score}")
        Score: 75.0
    """
```

### Module Docstrings

Every module should have a docstring:

```python
"""
Issue scorer for evaluating contribution fitness.

This module provides the scoring engine that evaluates GitHub issues
for suitability as AI-assisted contribution targets.

Classes:
    IssueScorer: Main scoring interface
    ScoreBreakdown: Detailed score components
    TriageResult: Complete triage results
"""
```

### README Updates

Update README.md when:
- Adding new features
- Changing CLI commands
- Modifying configuration options
- Adding dependencies

---

## Git Workflow

### Branching

```
main                    # Production-ready code
├── feature/<name>      # New features
├── fix/<name>          # Bug fixes
├── docs/<name>         # Documentation changes
└── refactor/<name>     # Code refactoring
```

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change without feature/fix
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(discovery): add support for GitLab repositories

Extends the scanner to handle GitLab's API alongside GitHub.

Closes #45
```

```
fix(triage): handle rate limiting gracefully

- Add exponential backoff
- Log warnings when approaching limits
- Respect X-RateLimit-Reset header
```

### Pull Requests

- Keep PRs focused (one feature/fix per PR)
- Write clear descriptions
- Link related issues
- Ensure CI passes
- Request review from maintainers

---

## Security

### Secrets Management

```python
# Good - use environment variables
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("GITHUB_TOKEN required")

# Bad - hardcoded secrets
token = "ghp_xxxxxxxxxxxx"  # NEVER do this
```

### Input Validation

Validate all external input:

```python
def _parse_issue_url(self, issue_url: str) -> tuple[str, int]:
    """Parse and validate a GitHub issue URL."""
    if not issue_url.startswith("https://github.com/"):
        raise ValueError(f"Invalid GitHub URL: {issue_url}")

    parts = issue_url.rstrip("/").split("/")
    if "issues" not in parts:
        raise ValueError(f"Not an issue URL: {issue_url}")

    # ... continue parsing
```

### Protected Operations

Use safeguards for dangerous operations:

```python
# Rate limiting
if remaining_requests < self.RATE_LIMIT_BUFFER:
    raise RateLimitError("Rate limit buffer reached")

# PR limits
if daily_pr_count >= self.MAX_DAILY_PRS:
    raise ContributionError("Daily PR limit reached")

# Protected files
PROTECTED_FILES = [".github/workflows/*", "*.lock", ".env*"]
if any(fnmatch(file, pattern) for pattern in PROTECTED_FILES):
    raise ContributionError(f"Cannot modify protected file: {file}")
```

### Dry Run Support

Always support dry-run mode for destructive operations:

```python
def submit_pr(self, dry_run: bool = False) -> str | None:
    if dry_run:
        logger.info("dry_run_pr", would_create=pr_details)
        return None

    # Actually create PR
    return self._create_pr(pr_details)
```

---

## Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
```

---

*"Write code that future you (and future AI agents) will thank you for."*
