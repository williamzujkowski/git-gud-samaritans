"""
Tests for the GitHub scanner module.
"""

from unittest.mock import MagicMock, patch

import pytest

from git_gud_samaritans.discovery.github_scanner import GitHubScanner, ScanResult


class TestScanResult:
    """Tests for the ScanResult dataclass."""

    def test_create_scan_result(self) -> None:
        """ScanResult should be creatable with required fields."""
        result = ScanResult(
            repo="owner/repo",
            issue_number=123,
            title="Test issue",
            url="https://github.com/owner/repo/issues/123",
        )
        assert result.repo == "owner/repo"
        assert result.issue_number == 123
        assert result.labels == []

    def test_scan_result_with_labels(self) -> None:
        """ScanResult should accept labels."""
        result = ScanResult(
            repo="owner/repo",
            issue_number=123,
            title="Test",
            url="https://example.com",
            labels=["bug", "help wanted"],
        )
        assert result.labels == ["bug", "help wanted"]


class TestGitHubScanner:
    """Tests for the GitHubScanner class."""

    @patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"})
    @patch("git_gud_samaritans.discovery.github_scanner.Github")
    def test_scanner_init_with_env_token(self, mock_github: MagicMock) -> None:
        """Scanner should initialize with environment token."""
        mock_client = MagicMock()
        mock_rate_limit = MagicMock()
        mock_rate_limit.core.remaining = 5000
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.reset.isoformat.return_value = "2024-01-01T00:00:00"
        mock_client.get_rate_limit.return_value = mock_rate_limit
        mock_github.return_value = mock_client

        scanner = GitHubScanner()
        assert scanner.token == "test_token"
        mock_github.assert_called_once_with("test_token")

    @patch("git_gud_samaritans.discovery.github_scanner.Github")
    def test_scanner_init_with_explicit_token(self, mock_github: MagicMock) -> None:
        """Scanner should initialize with explicit token."""
        mock_client = MagicMock()
        mock_rate_limit = MagicMock()
        mock_rate_limit.core.remaining = 5000
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.reset.isoformat.return_value = "2024-01-01T00:00:00"
        mock_client.get_rate_limit.return_value = mock_rate_limit
        mock_github.return_value = mock_client

        scanner = GitHubScanner(token="explicit_token")
        assert scanner.token == "explicit_token"

    @patch.dict("os.environ", {}, clear=True)
    def test_scanner_raises_without_token(self) -> None:
        """Scanner should raise ValueError without token."""
        with pytest.raises(ValueError, match="GitHub token required"):
            GitHubScanner()

    @patch("git_gud_samaritans.discovery.github_scanner.Github")
    def test_search_issues(self, mock_github: MagicMock) -> None:
        """Scanner should search for issues."""
        mock_client = MagicMock()
        mock_rate_limit = MagicMock()
        mock_rate_limit.core.remaining = 5000
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.reset.isoformat.return_value = "2024-01-01T00:00:00"
        mock_client.get_rate_limit.return_value = mock_rate_limit

        # Mock issue search results
        mock_issue = MagicMock()
        mock_issue.repository.full_name = "owner/repo"
        mock_issue.number = 123
        mock_issue.title = "Test issue"
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_issue.labels = []
        mock_issue.repository.stargazers_count = 100
        mock_issue.repository.language = "Python"
        mock_client.search_issues.return_value = [mock_issue]

        mock_github.return_value = mock_client

        scanner = GitHubScanner(token="test")
        results = list(scanner.search_issues("is:open", max_results=10))

        assert len(results) == 1
        assert results[0].repo == "owner/repo"
        assert results[0].issue_number == 123
