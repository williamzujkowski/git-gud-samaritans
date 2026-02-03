"""
Tests for the issue scorer module.
"""

import pytest

from git_gud_samaritans.triage.scorer import IssueScorer, ScoreBreakdown, TriageResult


class TestScoreBreakdown:
    """Tests for the ScoreBreakdown dataclass."""

    def test_create_breakdown(self) -> None:
        """ScoreBreakdown should be creatable with defaults."""
        breakdown = ScoreBreakdown()
        assert breakdown.clarity == 0.0
        assert breakdown.scope == 0.0

    def test_create_with_values(self) -> None:
        """ScoreBreakdown should accept values."""
        breakdown = ScoreBreakdown(
            clarity=80.0,
            scope=70.0,
            testability=90.0,
            maintainer_activity=75.0,
            codebase_health=85.0,
            ai_fit=80.0,
        )
        assert breakdown.clarity == 80.0
        assert breakdown.scope == 70.0

    def test_to_dict(self) -> None:
        """ScoreBreakdown should convert to dict."""
        breakdown = ScoreBreakdown(clarity=80.0)
        result = breakdown.to_dict()
        assert result["clarity"] == 80.0
        assert "scope" in result


class TestTriageResult:
    """Tests for the TriageResult dataclass."""

    def test_create_result(self) -> None:
        """TriageResult should be creatable."""
        result = TriageResult(
            issue_url="https://github.com/owner/repo/issues/123",
            score=75.0,
            breakdown=ScoreBreakdown(),
            recommendation="Good candidate",
            estimated_effort="Medium",
            risk_level="low",
        )
        assert result.score == 75.0
        assert result.recommendation == "Good candidate"

    def test_is_good_candidate_true(self) -> None:
        """TriageResult should identify good candidates."""
        result = TriageResult(
            issue_url="https://example.com",
            score=75.0,
            breakdown=ScoreBreakdown(),
            recommendation="Good",
            estimated_effort="Medium",
            risk_level="low",
        )
        assert result.is_good_candidate is True

    def test_is_good_candidate_false(self) -> None:
        """TriageResult should identify poor candidates."""
        result = TriageResult(
            issue_url="https://example.com",
            score=40.0,
            breakdown=ScoreBreakdown(),
            recommendation="Poor",
            estimated_effort="High",
            risk_level="high",
        )
        assert result.is_good_candidate is False

    def test_to_dict(self) -> None:
        """TriageResult should convert to dict."""
        result = TriageResult(
            issue_url="https://example.com",
            score=75.0,
            breakdown=ScoreBreakdown(clarity=80.0),
            recommendation="Good",
            estimated_effort="Medium",
            risk_level="low",
            risks=["Some risk"],
        )
        data = result.to_dict()
        assert data["score"] == 75.0
        assert data["breakdown"]["clarity"] == 80.0
        assert "risks" in data


class TestIssueScorer:
    """Tests for the IssueScorer class."""

    def test_scorer_init(self) -> None:
        """IssueScorer should initialize with defaults."""
        scorer = IssueScorer()
        assert scorer.weights == IssueScorer.DEFAULT_WEIGHTS

    def test_scorer_init_with_config(self, tmp_path: pytest.TempPathFactory) -> None:
        """IssueScorer should load config from file."""
        # Create a temp config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("weights:\n  clarity: 0.30\n")

        scorer = IssueScorer(config_path=str(config_file))
        assert scorer.config.get("weights", {}).get("clarity") == 0.30

    def test_score_issue(self) -> None:
        """IssueScorer should score an issue."""
        scorer = IssueScorer()
        result = scorer.score("https://github.com/owner/repo/issues/123")

        assert isinstance(result, TriageResult)
        assert 0 <= result.score <= 100
        assert result.issue_url == "https://github.com/owner/repo/issues/123"

    def test_score_breakdown_included(self) -> None:
        """IssueScorer should include score breakdown."""
        scorer = IssueScorer()
        result = scorer.score("https://github.com/owner/repo/issues/123")

        assert isinstance(result.breakdown, ScoreBreakdown)
        assert result.breakdown.clarity > 0
        assert result.breakdown.scope > 0

    def test_recommendation_based_on_score(self) -> None:
        """IssueScorer should provide recommendation based on score."""
        scorer = IssueScorer()
        result = scorer.score("https://github.com/owner/repo/issues/123")

        # Placeholder implementation returns ~74.5 score
        assert result.recommendation is not None
        assert len(result.recommendation) > 0
