"""
Complexity estimator for issues.
"""

from typing import ClassVar, Literal

import structlog

logger = structlog.get_logger()

ComplexityLevel = Literal["low", "medium", "high"]


class ComplexityEstimator:
    """
    Estimates the complexity of fixing an issue.

    Uses heuristics based on:
    - Issue description keywords
    - Labels
    - Codebase characteristics
    - Historical data
    """

    # Keywords indicating low complexity
    LOW_COMPLEXITY_KEYWORDS: ClassVar[list[str]] = [
        "typo",
        "spelling",
        "documentation",
        "docs",
        "readme",
        "comment",
        "example",
        "simple",
        "minor",
        "trivial",
        "easy",
        "quick",
    ]

    # Keywords indicating high complexity
    HIGH_COMPLEXITY_KEYWORDS: ClassVar[list[str]] = [
        "refactor",
        "redesign",
        "architecture",
        "performance",
        "security",
        "breaking",
        "major",
        "complex",
        "difficult",
        "api",
    ]

    # Labels indicating low complexity
    LOW_COMPLEXITY_LABELS: ClassVar[list[str]] = [
        "good first issue",
        "beginner",
        "easy",
        "documentation",
        "typo",
        "trivial",
    ]

    # Labels indicating high complexity
    HIGH_COMPLEXITY_LABELS: ClassVar[list[str]] = [
        "breaking change",
        "security",
        "performance",
        "architecture",
        "major",
        "complex",
    ]

    def estimate(self, issue_url: str) -> ComplexityLevel:
        """
        Estimate the complexity of an issue.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            Complexity level: "low", "medium", or "high"
        """
        logger.info("estimating_complexity", issue_url=issue_url)

        # TODO: Implement actual complexity estimation
        # This would fetch the issue and analyze it

        # Placeholder implementation
        return "medium"

    def estimate_from_content(
        self, title: str, body: str, labels: list[str]
    ) -> ComplexityLevel:
        """
        Estimate complexity from issue content.

        Args:
            title: Issue title
            body: Issue body/description
            labels: Issue labels

        Returns:
            Complexity level
        """
        score = 0
        content = f"{title} {body}".lower()

        # Check for low complexity indicators
        for keyword in self.LOW_COMPLEXITY_KEYWORDS:
            if keyword in content:
                score -= 1

        low_labels = [lbl.lower() for lbl in self.LOW_COMPLEXITY_LABELS]
        for label in labels:
            if label.lower() in low_labels:
                score -= 2

        # Check for high complexity indicators
        for keyword in self.HIGH_COMPLEXITY_KEYWORDS:
            if keyword in content:
                score += 1

        high_labels = [lbl.lower() for lbl in self.HIGH_COMPLEXITY_LABELS]
        for label in labels:
            if label.lower() in high_labels:
                score += 2

        # Convert score to level
        if score <= -2:
            return "low"
        elif score >= 2:
            return "high"
        else:
            return "medium"
