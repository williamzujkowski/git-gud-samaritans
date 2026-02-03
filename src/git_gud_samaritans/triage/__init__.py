"""
Triage module for git-gud-samaritans.

Scores issues for contribution fitness.
"""

from .complexity import ComplexityEstimator
from .fit_analyzer import AIFitAnalyzer
from .scorer import IssueScorer, TriageResult


class Triager:
    """
    Main triage interface for scoring contribution fitness.

    Example:
        triager = Triager()
        result = triager.score_issue("https://github.com/owner/repo/issues/123")

        if result.score >= 60:
            print("Good candidate for contribution!")
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize the triager.

        Args:
            config_path: Path to triage scoring configuration
        """
        self.scorer = IssueScorer(config_path=config_path)
        self.complexity_estimator = ComplexityEstimator()
        self.fit_analyzer = AIFitAnalyzer()

    def score_issue(self, issue_url: str) -> TriageResult:
        """
        Score a single issue for contribution fitness.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            TriageResult with score and breakdown
        """
        return self.scorer.score(issue_url)

    def score_all(self, opportunities: list[dict]) -> list[TriageResult]:
        """
        Score multiple opportunities and return sorted by score.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            List of TriageResults sorted by score (highest first)
        """
        results = []
        for opp in opportunities:
            result = self.score_issue(opp["url"])
            results.append(result)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def estimate_complexity(self, issue_url: str) -> str:
        """
        Estimate the complexity of fixing an issue.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            Complexity level: "low", "medium", or "high"
        """
        return self.complexity_estimator.estimate(issue_url)

    def analyze_fit(self, issue_url: str) -> dict:
        """
        Analyze how well-suited an issue is for AI contribution.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            Dictionary with fit analysis results
        """
        return self.fit_analyzer.analyze(issue_url)


__all__ = [
    "AIFitAnalyzer",
    "ComplexityEstimator",
    "IssueScorer",
    "TriageResult",
    "Triager",
]
