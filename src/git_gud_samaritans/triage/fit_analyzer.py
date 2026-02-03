"""
AI fit analyzer for evaluating issue suitability for AI contribution.
"""

from dataclasses import dataclass
from typing import Any, ClassVar

import structlog

logger = structlog.get_logger()


@dataclass
class FitAnalysis:
    """Result of AI fit analysis."""

    score: float
    suitable: bool
    strengths: list[str]
    concerns: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "suitable": self.suitable,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
        }


class AIFitAnalyzer:
    """
    Analyzes how well-suited an issue is for AI contribution.

    Considers:
    - Issue type (documentation, tests, bugs, features)
    - Required domain knowledge
    - Subjectivity level
    - Security sensitivity
    - Need for human judgment
    """

    # Issue types well-suited for AI
    GOOD_FIT_TYPES: ClassVar[list[str]] = [
        "documentation",
        "test",
        "typo",
        "example",
        "type hints",
        "formatting",
        "linting",
    ]

    # Issue types less suited for AI
    POOR_FIT_TYPES: ClassVar[list[str]] = [
        "design",
        "rfc",
        "discussion",
        "opinion",
        "security",
        "performance optimization",
        "user experience",
    ]

    def analyze(self, issue_url: str) -> dict:
        """
        Analyze AI fit for an issue.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            Dictionary with fit analysis results
        """
        logger.info("analyzing_ai_fit", issue_url=issue_url)

        # TODO: Implement actual analysis
        # This would fetch the issue and analyze content

        analysis = FitAnalysis(
            score=75.0,
            suitable=True,
            strengths=[
                "Clear acceptance criteria",
                "Well-defined scope",
                "Good test coverage in repo",
            ],
            concerns=["May require some domain knowledge"],
            recommendations=[
                "Review existing tests before implementing",
                "Follow code style conventions",
            ],
        )

        return analysis.to_dict()

    def analyze_from_content(
        self,
        title: str,
        body: str,
        labels: list[str],
        repo_has_tests: bool = True,
        repo_has_ci: bool = True,
    ) -> FitAnalysis:
        """
        Analyze AI fit from issue content.

        Args:
            title: Issue title
            body: Issue body/description
            labels: Issue labels
            repo_has_tests: Whether the repo has tests
            repo_has_ci: Whether the repo has CI

        Returns:
            FitAnalysis result
        """
        score = 50.0  # Start at neutral
        strengths = []
        concerns = []
        recommendations = []

        content = f"{title} {body}".lower()
        label_set = {lbl.lower() for lbl in labels}

        # Check for good fit indicators
        for fit_type in self.GOOD_FIT_TYPES:
            if fit_type in content or fit_type in label_set:
                score += 10
                strengths.append(f"Issue type '{fit_type}' is well-suited for AI")

        # Check for poor fit indicators
        for fit_type in self.POOR_FIT_TYPES:
            if fit_type in content or fit_type in label_set:
                score -= 15
                concerns.append(f"Issue type '{fit_type}' may require human judgment")

        # Repository factors
        if repo_has_tests:
            score += 10
            strengths.append("Repository has test infrastructure")
        else:
            score -= 10
            concerns.append("No test infrastructure - harder to verify fix")
            recommendations.append("Consider adding tests with the fix")

        if repo_has_ci:
            score += 5
            strengths.append("CI will automatically verify changes")
        else:
            recommendations.append("Run tests locally before submitting")

        # Check for clear requirements
        if any(word in content for word in ["expected", "should", "must"]):
            score += 5
            strengths.append("Clear expected behavior defined")

        # Check for concerning patterns
        if any(word in content for word in ["subjective", "opinion", "preference"]):
            score -= 10
            concerns.append("Subjective requirements may need human input")

        if "security" in content or "security" in label_set:
            score -= 20
            concerns.append("Security-sensitive changes need careful review")
            recommendations.append("Flag for human review before submitting")

        # Normalize score
        score = max(0, min(100, score))
        suitable = score >= 60

        return FitAnalysis(
            score=score,
            suitable=suitable,
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations,
        )
