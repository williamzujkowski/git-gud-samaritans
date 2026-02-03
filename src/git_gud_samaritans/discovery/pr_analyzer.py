"""
Pull request analyzer for finding stale PRs that need help.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar

import structlog

from .github_scanner import GitHubScanner

logger = structlog.get_logger()


@dataclass
class StalePR:
    """Represents a stale pull request that might need help."""

    repo: str
    pr_number: int
    title: str
    url: str
    labels: list[str]
    stars: int
    language: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    days_stale: int = 0
    review_state: str | None = None
    needs_rebase: bool = False
    has_conflicts: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "repo": self.repo,
            "pr_number": self.pr_number,
            "title": self.title,
            "url": self.url,
            "labels": self.labels,
            "stars": self.stars,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "days_stale": self.days_stale,
            "review_state": self.review_state,
            "needs_rebase": self.needs_rebase,
            "has_conflicts": self.has_conflicts,
        }


class PRAnalyzer:
    """
    Analyzes pull requests to find ones that need help.

    Looks for:
    - Stale PRs with no recent activity
    - PRs with requested changes that haven't been addressed
    - PRs that need rebasing
    """

    # Labels indicating PR needs help
    HELP_LABELS: ClassVar[list[str]] = [
        "needs update",
        "needs rebase",
        "needs tests",
        "needs documentation",
        "stale",
    ]

    def __init__(self, scanner: GitHubScanner):
        """
        Initialize the PR analyzer.

        Args:
            scanner: GitHubScanner instance to use for API calls
        """
        self.scanner = scanner

    def find_stale(
        self,
        languages: list[str] | None = None,
        min_days_stale: int = 30,
        max_results: int = 20,
    ) -> list[dict]:
        """
        Find stale PRs that might need help.

        Args:
            languages: Programming languages to filter by
            min_days_stale: Minimum days since last update
            max_results: Maximum number of results

        Returns:
            List of stale PR dictionaries
        """
        stale_prs: list[StalePR] = []

        # Build search query
        query = self._build_query(languages=languages, min_days_stale=min_days_stale)

        logger.info(
            "finding_stale_prs",
            query=query,
            min_days_stale=min_days_stale,
            max_results=max_results,
        )

        # Search for stale PRs
        for result in self.scanner.search_issues(query, max_results=max_results * 2):
            if self._is_suitable_pr(result):
                stale_pr = self._to_stale_pr(result, min_days_stale)
                stale_prs.append(stale_pr)

                if len(stale_prs) >= max_results:
                    break

        logger.info("found_stale_prs", count=len(stale_prs))

        return [pr.to_dict() for pr in stale_prs]

    def _build_query(self, languages: list[str] | None, min_days_stale: int) -> str:
        """Build a GitHub search query for stale PRs."""
        cutoff = datetime.now() - timedelta(days=min_days_stale)

        parts = [
            "is:pr",
            "is:open",
            "-is:draft",
            f"updated:<{cutoff.strftime('%Y-%m-%d')}",
            "sort:updated-asc",
        ]

        # Add language filters
        if languages:
            lang_filter = " ".join(f"language:{lang}" for lang in languages)
            parts.append(f"({lang_filter})")

        return " ".join(parts)

    def _is_suitable_pr(self, result: Any) -> bool:
        """Check if a PR is suitable for our help."""
        # Skip PRs with certain labels
        skip_labels = ["wip", "work in progress", "do not merge"]
        return all(label.lower() not in skip_labels for label in result.labels)

    def _to_stale_pr(self, result: Any, min_days: int) -> StalePR:
        """Convert a search result to a StalePR."""
        return StalePR(
            repo=result.repo,
            pr_number=result.issue_number or 0,
            title=result.title,
            url=result.url,
            labels=result.labels,
            stars=result.stars,
            language=result.language,
            days_stale=min_days,  # Approximate
        )
