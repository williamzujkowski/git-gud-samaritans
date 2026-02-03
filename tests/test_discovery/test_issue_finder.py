"""
Tests for the issue finder module.
"""

from unittest.mock import MagicMock

import pytest

from git_gud_samaritans.discovery.github_scanner import ScanResult
from git_gud_samaritans.discovery.issue_finder import IssueFinder, IssueOpportunity


class TestIssueOpportunity:
    """Tests for the IssueOpportunity dataclass."""

    def test_create_opportunity(self) -> None:
        """IssueOpportunity should be creatable."""
        opp = IssueOpportunity(
            repo="owner/repo",
            issue_number=123,
            title="Test issue",
            url="https://github.com/owner/repo/issues/123",
            labels=["bug"],
            stars=100,
            language="python",
        )
        assert opp.repo == "owner/repo"
        assert opp.issue_number == 123

    def test_to_dict(self) -> None:
        """IssueOpportunity should convert to dict."""
        opp = IssueOpportunity(
            repo="owner/repo",
            issue_number=123,
            title="Test issue",
            url="https://example.com",
            labels=["bug"],
            stars=100,
            language="python",
        )
        result = opp.to_dict()
        assert result["repo"] == "owner/repo"
        assert result["issue_number"] == 123
        assert "labels" in result


class TestIssueFinder:
    """Tests for the IssueFinder class."""

    @pytest.fixture
    def mock_scanner(self) -> MagicMock:
        """Provide a mocked scanner."""
        scanner = MagicMock()
        return scanner

    def test_finder_init(self, mock_scanner: MagicMock) -> None:
        """IssueFinder should initialize with scanner."""
        finder = IssueFinder(scanner=mock_scanner)
        assert finder.scanner == mock_scanner

    def test_find_issues(self, mock_scanner: MagicMock) -> None:
        """IssueFinder should find issues."""
        scan_result = ScanResult(
            repo="owner/repo",
            issue_number=123,
            title="Good first issue",
            url="https://github.com/owner/repo/issues/123",
            labels=["good first issue"],
            stars=100,
            language="python",
        )
        mock_scanner.search_issues.return_value = [scan_result]

        finder = IssueFinder(scanner=mock_scanner)
        results = finder.find(labels=["good first issue"], max_results=10)

        assert len(results) == 1
        assert results[0]["repo"] == "owner/repo"
        mock_scanner.search_issues.assert_called_once()

    def test_excludes_wontfix(self, mock_scanner: MagicMock) -> None:
        """IssueFinder should exclude wontfix issues."""
        scan_result = ScanResult(
            repo="owner/repo",
            issue_number=123,
            title="Test",
            url="https://example.com",
            labels=["wontfix"],
            stars=100,
            language="python",
        )
        mock_scanner.search_issues.return_value = [scan_result]

        finder = IssueFinder(scanner=mock_scanner)
        results = finder.find(max_results=10)

        assert len(results) == 0

    def test_build_query(self, mock_scanner: MagicMock) -> None:
        """IssueFinder should build proper queries."""
        finder = IssueFinder(scanner=mock_scanner)
        query = finder._build_query(
            languages=["python"],
            labels=["good first issue"],
            min_stars=50,
            max_age_days=365,
        )

        assert "is:issue" in query
        assert "is:open" in query
        assert "stars:>=50" in query
        assert "language:python" in query
