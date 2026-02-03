"""
Tests for the complexity estimator module.
"""

import pytest

from git_gud_samaritans.triage.complexity import ComplexityEstimator


class TestComplexityEstimator:
    """Tests for the ComplexityEstimator class."""

    @pytest.fixture
    def estimator(self) -> ComplexityEstimator:
        """Provide a ComplexityEstimator instance."""
        return ComplexityEstimator()

    def test_estimate_returns_valid_level(self, estimator: ComplexityEstimator) -> None:
        """estimate() should return a valid complexity level."""
        result = estimator.estimate("https://github.com/owner/repo/issues/123")
        assert result in ["low", "medium", "high"]

    def test_estimate_from_content_low(self, estimator: ComplexityEstimator) -> None:
        """estimate_from_content should identify low complexity."""
        result = estimator.estimate_from_content(
            title="Fix typo in README",
            body="There's a spelling mistake in the documentation.",
            labels=["good first issue", "documentation"],
        )
        assert result == "low"

    def test_estimate_from_content_high(self, estimator: ComplexityEstimator) -> None:
        """estimate_from_content should identify high complexity."""
        result = estimator.estimate_from_content(
            title="Refactor authentication system",
            body="We need to redesign the architecture for better security.",
            labels=["breaking change", "security"],
        )
        assert result == "high"

    def test_estimate_from_content_medium(self, estimator: ComplexityEstimator) -> None:
        """estimate_from_content should default to medium."""
        result = estimator.estimate_from_content(
            title="Add feature X",
            body="Implement feature X as described.",
            labels=["enhancement"],
        )
        assert result == "medium"

    def test_keywords_affect_score(self, estimator: ComplexityEstimator) -> None:
        """Keywords should affect complexity score."""
        # Low complexity keywords
        low_result = estimator.estimate_from_content(
            title="Simple typo fix",
            body="Easy fix for a minor issue.",
            labels=[],
        )

        # High complexity keywords
        high_result = estimator.estimate_from_content(
            title="Complex refactor needed",
            body="This requires redesigning the architecture.",
            labels=[],
        )

        # Low should score lower than high
        assert low_result in ["low", "medium"]
        assert high_result in ["medium", "high"]
