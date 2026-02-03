"""
GitHub API scanner for discovering repositories and issues.
"""

import os
from collections.abc import Generator
from dataclasses import dataclass, field

import structlog
from github import Github, GithubException
from github.Issue import Issue
from github.Repository import Repository

logger = structlog.get_logger()


@dataclass
class ScanResult:
    """Result from a GitHub scan operation."""

    repo: str
    issue_number: int | None = None
    pr_number: int | None = None
    title: str = ""
    url: str = ""
    labels: list[str] = field(default_factory=list)
    stars: int = 0
    language: str | None = None


class GitHubScanner:
    """
    Scans GitHub for repositories and issues matching given criteria.

    Uses the GitHub API with rate limiting awareness.
    """

    def __init__(self, token: str | None = None):
        """
        Initialize the scanner.

        Args:
            token: GitHub personal access token. If not provided,
                   falls back to GITHUB_TOKEN environment variable.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN environment variable "
                "or pass token to constructor."
            )

        self.client = Github(self.token)
        self._check_rate_limit()

    def _check_rate_limit(self) -> None:
        """Check and log current rate limit status."""
        rate_limit = self.client.get_rate_limit()
        core = rate_limit.core

        logger.info(
            "github_rate_limit",
            remaining=core.remaining,
            limit=core.limit,
            reset=core.reset.isoformat(),
        )

        if core.remaining < 100:
            logger.warning("github_rate_limit_low", remaining=core.remaining)

    def search_issues(
        self, query: str, max_results: int = 100
    ) -> Generator[ScanResult, None, None]:
        """
        Search for issues matching the query.

        Args:
            query: GitHub search query string
            max_results: Maximum results to return

        Yields:
            ScanResult objects for each matching issue
        """
        logger.info("github_search_issues", query=query, max_results=max_results)

        try:
            issues = self.client.search_issues(query=query)

            for i, issue in enumerate(issues):
                if i >= max_results:
                    break

                yield ScanResult(
                    repo=issue.repository.full_name,
                    issue_number=issue.number,
                    title=issue.title,
                    url=issue.html_url,
                    labels=[label.name for label in issue.labels],
                    stars=issue.repository.stargazers_count,
                    language=issue.repository.language,
                )

        except GithubException as e:
            logger.error("github_search_error", error=str(e))
            raise

    def search_repositories(
        self, query: str, max_results: int = 100
    ) -> Generator[Repository, None, None]:
        """
        Search for repositories matching the query.

        Args:
            query: GitHub search query string
            max_results: Maximum results to return

        Yields:
            Repository objects
        """
        logger.info("github_search_repos", query=query, max_results=max_results)

        try:
            repos = self.client.search_repositories(query=query)

            for i, repo in enumerate(repos):
                if i >= max_results:
                    break
                yield repo

        except GithubException as e:
            logger.error("github_search_error", error=str(e))
            raise

    def get_repository(self, full_name: str) -> Repository:
        """
        Get a specific repository by full name.

        Args:
            full_name: Repository full name (owner/repo)

        Returns:
            Repository object
        """
        return self.client.get_repo(full_name)

    def get_issue(self, repo: str, number: int) -> Issue:
        """
        Get a specific issue.

        Args:
            repo: Repository full name (owner/repo)
            number: Issue number

        Returns:
            Issue object
        """
        repository = self.get_repository(repo)
        return repository.get_issue(number)
