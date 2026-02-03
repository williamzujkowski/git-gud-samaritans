"""
Issue finder for discovering contribution opportunities.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar

import structlog

from .github_scanner import GitHubScanner, ScanResult

logger = structlog.get_logger()


@dataclass
class IssueOpportunity:
    """Represents a potential contribution opportunity."""

    repo: str
    issue_number: int
    title: str
    url: str
    labels: list[str]
    stars: int
    language: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    comments_count: int = 0
    has_assignee: bool = False
    body_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "repo": self.repo,
            "issue_number": self.issue_number,
            "title": self.title,
            "url": self.url,
            "labels": self.labels,
            "stars": self.stars,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "comments_count": self.comments_count,
            "has_assignee": self.has_assignee,
            "body_preview": self.body_preview,
        }


class IssueFinder:
    """
    Finds issues suitable for AI-assisted contribution.

    Applies filtering rules to identify good contribution opportunities.
    """

    # Default labels to search for
    DEFAULT_LABELS: ClassVar[list[str]] = [
        "good first issue",
        "good-first-issue",
        "help wanted",
        "help-wanted",
        "beginner",
        "beginner-friendly",
        "hacktoberfest",
        "up-for-grabs",
    ]

    # Labels that indicate we should skip
    EXCLUDE_LABELS: ClassVar[list[str]] = [
        "wontfix",
        "invalid",
        "duplicate",
        "blocked",
        "on hold",
        "wip",
        "work in progress",
        "claimed",
        "assigned",
    ]

    def __init__(self, scanner: GitHubScanner):
        """
        Initialize the issue finder.

        Args:
            scanner: GitHubScanner instance to use for API calls
        """
        self.scanner = scanner

    def find(
        self,
        languages: list[str] | None = None,
        labels: list[str] | None = None,
        min_stars: int = 10,
        max_results: int = 20,
        max_age_days: int = 365,
    ) -> list[dict]:
        """
        Find issues matching the given criteria.

        Args:
            languages: Programming languages to filter by
            labels: Issue labels to search for
            min_stars: Minimum repository stars
            max_results: Maximum number of results
            max_age_days: Maximum age of issues in days

        Returns:
            List of issue dictionaries
        """
        labels = labels or self.DEFAULT_LABELS
        opportunities: list[IssueOpportunity] = []

        # Build search query
        query = self._build_query(
            languages=languages,
            labels=labels,
            min_stars=min_stars,
            max_age_days=max_age_days,
        )

        logger.info("finding_issues", query=query, max_results=max_results)

        # Search and filter
        for result in self.scanner.search_issues(query, max_results=max_results * 2):
            if self._should_include(result):
                opportunity = self._to_opportunity(result)
                opportunities.append(opportunity)

                if len(opportunities) >= max_results:
                    break

        logger.info("found_issues", count=len(opportunities))

        return [opp.to_dict() for opp in opportunities]

    def _build_query(
        self,
        languages: list[str] | None,
        labels: list[str],
        min_stars: int,
        max_age_days: int,
    ) -> str:
        """Build a GitHub search query."""
        parts = [
            "is:issue",
            "is:open",
            "no:assignee",
            "-label:claimed",
            "-label:wip",
            f"stars:>={min_stars}",
        ]

        # Add language filters
        if languages:
            lang_filter = " ".join(f"language:{lang}" for lang in languages)
            parts.append(f"({lang_filter})")

        # Add label filters (OR)
        if labels:
            label_parts = [f'label:"{label}"' for label in labels]
            parts.append(f"({' OR '.join(label_parts)})")

        # Add date filter
        cutoff = datetime.now() - timedelta(days=max_age_days)
        parts.append(f"created:>{cutoff.strftime('%Y-%m-%d')}")

        # Sort by recently updated
        parts.append("sort:updated-desc")

        return " ".join(parts)

    def _should_include(self, result: ScanResult) -> bool:
        """Check if an issue should be included in results."""
        # Check for exclude labels
        exclude_lower = [excl.lower() for excl in self.EXCLUDE_LABELS]
        return all(label.lower() not in exclude_lower for label in result.labels)

    def _to_opportunity(self, result: ScanResult) -> IssueOpportunity:
        """Convert a ScanResult to an IssueOpportunity."""
        return IssueOpportunity(
            repo=result.repo,
            issue_number=result.issue_number or 0,
            title=result.title,
            url=result.url,
            labels=result.labels,
            stars=result.stars,
            language=result.language,
        )
