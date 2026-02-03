"""
Issue scorer for evaluating contribution fitness.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import structlog
import yaml

logger = structlog.get_logger()


@dataclass
class ScoreBreakdown:
    """Breakdown of individual scoring components."""

    clarity: float = 0.0
    scope: float = 0.0
    testability: float = 0.0
    maintainer_activity: float = 0.0
    codebase_health: float = 0.0
    ai_fit: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "clarity": self.clarity,
            "scope": self.scope,
            "testability": self.testability,
            "maintainer_activity": self.maintainer_activity,
            "codebase_health": self.codebase_health,
            "ai_fit": self.ai_fit,
        }


@dataclass
class TriageResult:
    """Result of triaging an issue."""

    issue_url: str
    score: float
    breakdown: ScoreBreakdown
    recommendation: str
    estimated_effort: str
    risk_level: str
    risks: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_url": self.issue_url,
            "score": self.score,
            "breakdown": self.breakdown.to_dict(),
            "recommendation": self.recommendation,
            "estimated_effort": self.estimated_effort,
            "risk_level": self.risk_level,
            "risks": self.risks,
            "notes": self.notes,
        }

    @property
    def is_good_candidate(self) -> bool:
        """Check if this is a good contribution candidate."""
        return self.score >= 60


class IssueScorer:
    """
    Scores issues for contribution fitness.

    Uses configurable weights and rules to evaluate:
    - Clarity: How well-defined is the issue?
    - Scope: Is it appropriately sized?
    - Testability: Can we verify our fix?
    - Maintainer Activity: Will our PR get reviewed?
    - Codebase Health: Is the codebase in good shape?
    - AI Fit: Is this suitable for AI contribution?
    """

    DEFAULT_WEIGHTS: ClassVar[dict[str, float]] = {
        "clarity": 0.25,
        "scope": 0.20,
        "testability": 0.15,
        "maintainer_activity": 0.15,
        "codebase_health": 0.15,
        "ai_fit": 0.10,
    }

    def __init__(self, config_path: str | None = None):
        """
        Initialize the scorer.

        Args:
            config_path: Path to scoring configuration YAML
        """
        self.config = self._load_config(config_path)
        self.weights = self.config.get("weights", self.DEFAULT_WEIGHTS)

    def _load_config(self, config_path: str | None) -> dict[str, Any]:
        """Load scoring configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                result = yaml.safe_load(f)
                return result if isinstance(result, dict) else {}
        return {}

    def score(self, issue_url: str) -> TriageResult:
        """
        Score an issue for contribution fitness.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            TriageResult with score and breakdown
        """
        logger.info("scoring_issue", issue_url=issue_url)

        # TODO: Implement actual scoring logic
        # This is a placeholder implementation

        breakdown = ScoreBreakdown(
            clarity=self._score_clarity(issue_url),
            scope=self._score_scope(issue_url),
            testability=self._score_testability(issue_url),
            maintainer_activity=self._score_maintainer_activity(issue_url),
            codebase_health=self._score_codebase_health(issue_url),
            ai_fit=self._score_ai_fit(issue_url),
        )

        # Calculate weighted score
        total_score = (
            breakdown.clarity * self.weights["clarity"]
            + breakdown.scope * self.weights["scope"]
            + breakdown.testability * self.weights["testability"]
            + breakdown.maintainer_activity * self.weights["maintainer_activity"]
            + breakdown.codebase_health * self.weights["codebase_health"]
            + breakdown.ai_fit * self.weights["ai_fit"]
        )

        # Determine recommendation
        if total_score >= 80:
            recommendation = "Excellent candidate - proceed with contribution"
            risk_level = "low"
        elif total_score >= 60:
            recommendation = "Good candidate - proceed with caution"
            risk_level = "medium"
        elif total_score >= 40:
            recommendation = "Marginal candidate - consider alternatives"
            risk_level = "medium"
        else:
            recommendation = "Poor candidate - skip"
            risk_level = "high"

        # Estimate effort
        if breakdown.scope >= 80:
            effort = "Low (1-2 hours)"
        elif breakdown.scope >= 60:
            effort = "Medium (2-4 hours)"
        else:
            effort = "High (4+ hours)"

        result = TriageResult(
            issue_url=issue_url,
            score=total_score,
            breakdown=breakdown,
            recommendation=recommendation,
            estimated_effort=effort,
            risk_level=risk_level,
        )

        logger.info(
            "scored_issue",
            issue_url=issue_url,
            score=total_score,
            recommendation=recommendation,
        )

        return result

    def _score_clarity(self, issue_url: str) -> float:
        """Score issue clarity (0-100)."""
        # TODO: Implement clarity scoring
        return 75.0

    def _score_scope(self, issue_url: str) -> float:
        """Score issue scope (0-100)."""
        # TODO: Implement scope scoring
        return 70.0

    def _score_testability(self, issue_url: str) -> float:
        """Score testability (0-100)."""
        # TODO: Implement testability scoring
        return 80.0

    def _score_maintainer_activity(self, issue_url: str) -> float:
        """Score maintainer activity (0-100)."""
        # TODO: Implement maintainer activity scoring
        return 75.0

    def _score_codebase_health(self, issue_url: str) -> float:
        """Score codebase health (0-100)."""
        # TODO: Implement codebase health scoring
        return 70.0

    def _score_ai_fit(self, issue_url: str) -> float:
        """Score AI fitness (0-100)."""
        # TODO: Implement AI fit scoring
        return 80.0
