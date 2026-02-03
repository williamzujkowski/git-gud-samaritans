"""
Shared pytest fixtures for git-gud-samaritans tests.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_github_client() -> MagicMock:
    """Provide a mocked GitHub client."""
    client = MagicMock()

    # Mock rate limit
    rate_limit = MagicMock()
    rate_limit.core.remaining = 5000
    rate_limit.core.limit = 5000
    rate_limit.core.reset.isoformat.return_value = "2024-01-01T00:00:00"
    client.get_rate_limit.return_value = rate_limit

    return client


@pytest.fixture
def mock_github_scanner(mock_github_client: MagicMock) -> MagicMock:
    """Provide a mocked GitHubScanner."""
    scanner = MagicMock()
    scanner.client = mock_github_client
    return scanner


@pytest.fixture
def sample_issue_url() -> str:
    """Provide a sample GitHub issue URL."""
    return "https://github.com/owner/repo/issues/123"


@pytest.fixture
def sample_issue_dict() -> dict:
    """Provide a sample issue dictionary."""
    return {
        "repo": "owner/repo",
        "issue_number": 123,
        "title": "Fix bug in authentication",
        "url": "https://github.com/owner/repo/issues/123",
        "labels": ["bug", "good first issue"],
        "stars": 1000,
        "language": "python",
    }


@pytest.fixture
def sample_scan_result() -> dict:
    """Provide a sample scan result dictionary."""
    return {
        "repo": "owner/repo",
        "issue_number": 123,
        "title": "Fix bug in authentication",
        "url": "https://github.com/owner/repo/issues/123",
        "labels": ["bug", "good first issue"],
        "stars": 1000,
        "language": "python",
    }
