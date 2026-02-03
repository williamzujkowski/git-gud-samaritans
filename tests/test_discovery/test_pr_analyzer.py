"""
Tests for the PR analyzer module.
"""

from unittest.mock import MagicMock

import pytest

from git_gud_samaritans.discovery.github_scanner import ScanResult
from git_gud_samaritans.discovery.pr_analyzer import PRAnalyzer, StalePR


class TestStalePR:
    """Tests for the StalePR dataclass."""

    def test_create_stale_pr(self) -> None:
        """StalePR should be creatable."""
        pr = StalePR(
            repo="owner/repo",
            pr_number=456,
            title="Stale PR",
            url="https://github.com/owner/repo/pull/456",
            labels=["needs update"],
            stars=100,
            language="python",
            days_stale=45,
        )
        assert pr.repo == "owner/repo"
        assert pr.pr_number == 456
        assert pr.days_stale == 45

    def test_to_dict(self) -> None:
        """StalePR should convert to dict."""
        pr = StalePR(
            repo="owner/repo",
            pr_number=456,
            title="Stale PR",
            url="https://example.com",
            labels=[],
            stars=100,
            language="python",
        )
        result = pr.to_dict()
        assert result["pr_number"] == 456
        assert "days_stale" in result


class TestPRAnalyzer:
    """Tests for the PRAnalyzer class."""

    @pytest.fixture
    def mock_scanner(self) -> MagicMock:
        """Provide a mocked scanner."""
        return MagicMock()

    def test_analyzer_init(self, mock_scanner: MagicMock) -> None:
        """PRAnalyzer should initialize with scanner."""
        analyzer = PRAnalyzer(scanner=mock_scanner)
        assert analyzer.scanner == mock_scanner

    def test_find_stale_prs(self, mock_scanner: MagicMock) -> None:
        """PRAnalyzer should find stale PRs."""
        scan_result = ScanResult(
            repo="owner/repo",
            issue_number=456,
            title="Stale PR",
            url="https://github.com/owner/repo/pull/456",
            labels=["needs update"],
            stars=100,
            language="python",
        )
        mock_scanner.search_issues.return_value = [scan_result]

        analyzer = PRAnalyzer(scanner=mock_scanner)
        results = analyzer.find_stale(min_days_stale=30, max_results=10)

        assert len(results) == 1
        assert results[0]["pr_number"] == 456

    def test_excludes_wip_prs(self, mock_scanner: MagicMock) -> None:
        """PRAnalyzer should exclude WIP PRs."""
        scan_result = ScanResult(
            repo="owner/repo",
            issue_number=456,
            title="WIP: Feature",
            url="https://example.com",
            labels=["wip"],
            stars=100,
            language="python",
        )
        mock_scanner.search_issues.return_value = [scan_result]

        analyzer = PRAnalyzer(scanner=mock_scanner)
        results = analyzer.find_stale(min_days_stale=30, max_results=10)

        assert len(results) == 0

    def test_build_query(self, mock_scanner: MagicMock) -> None:
        """PRAnalyzer should build proper queries."""
        analyzer = PRAnalyzer(scanner=mock_scanner)
        query = analyzer._build_query(languages=["python"], min_days_stale=30)

        assert "is:pr" in query
        assert "is:open" in query
        assert "-is:draft" in query
        assert "language:python" in query
