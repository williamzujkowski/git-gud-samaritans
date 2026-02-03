"""
Discovery module for git-gud-samaritans.

Finds repositories and issues that welcome contributions.
"""

from .github_scanner import GitHubScanner
from .issue_finder import IssueFinder
from .pr_analyzer import PRAnalyzer


class Discoverer:
    """
    Main discovery interface for finding contribution opportunities.

    Example:
        discoverer = Discoverer(languages=["python", "rust"])
        opportunities = discoverer.find_issues(
            labels=["good first issue"],
            min_stars=50
        )
    """

    def __init__(
        self, languages: list[str] | None = None, github_token: str | None = None
    ):
        self.languages = languages or []
        self.scanner = GitHubScanner(token=github_token)
        self.issue_finder = IssueFinder(scanner=self.scanner)
        self.pr_analyzer = PRAnalyzer(scanner=self.scanner)

    def find_issues(
        self,
        labels: list[str] | None = None,
        min_stars: int = 10,
        max_results: int = 20,
    ) -> list[dict]:
        """
        Find issues that match the given criteria.

        Args:
            labels: Issue labels to search for
            min_stars: Minimum repository stars
            max_results: Maximum number of results to return

        Returns:
            List of issue dictionaries with metadata
        """
        return self.issue_finder.find(
            languages=self.languages,
            labels=labels or ["good first issue"],
            min_stars=min_stars,
            max_results=max_results,
        )

    def find_stale_prs(
        self, min_days_stale: int = 30, max_results: int = 20
    ) -> list[dict]:
        """
        Find stale PRs that might need help.

        Args:
            min_days_stale: Minimum days since last update
            max_results: Maximum number of results to return

        Returns:
            List of PR dictionaries with metadata
        """
        return self.pr_analyzer.find_stale(
            languages=self.languages,
            min_days_stale=min_days_stale,
            max_results=max_results,
        )


__all__ = [
    "Discoverer",
    "GitHubScanner",
    "IssueFinder",
    "PRAnalyzer",
]
