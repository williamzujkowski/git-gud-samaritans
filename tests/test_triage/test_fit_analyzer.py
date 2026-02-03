"""
Tests for the AI fit analyzer module.
"""

import pytest

from git_gud_samaritans.triage.fit_analyzer import AIFitAnalyzer, FitAnalysis


class TestFitAnalysis:
    """Tests for the FitAnalysis dataclass."""

    def test_create_analysis(self) -> None:
        """FitAnalysis should be creatable."""
        analysis = FitAnalysis(
            score=80.0,
            suitable=True,
            strengths=["Clear scope"],
            concerns=["May need review"],
            recommendations=["Check tests"],
        )
        assert analysis.score == 80.0
        assert analysis.suitable is True

    def test_to_dict(self) -> None:
        """FitAnalysis should convert to dict."""
        analysis = FitAnalysis(
            score=80.0,
            suitable=True,
            strengths=["Clear scope"],
            concerns=[],
            recommendations=[],
        )
        result = analysis.to_dict()
        assert result["score"] == 80.0
        assert result["suitable"] is True
        assert "strengths" in result


class TestAIFitAnalyzer:
    """Tests for the AIFitAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> AIFitAnalyzer:
        """Provide an AIFitAnalyzer instance."""
        return AIFitAnalyzer()

    def test_analyze_returns_dict(self, analyzer: AIFitAnalyzer) -> None:
        """analyze() should return a dictionary."""
        result = analyzer.analyze("https://github.com/owner/repo/issues/123")
        assert isinstance(result, dict)
        assert "score" in result
        assert "suitable" in result

    def test_analyze_from_content_documentation(self, analyzer: AIFitAnalyzer) -> None:
        """Documentation issues should be good fit."""
        result = analyzer.analyze_from_content(
            title="Update documentation",
            body="The docs need updating.",
            labels=["documentation"],
            repo_has_tests=True,
            repo_has_ci=True,
        )
        assert result.score >= 60
        assert result.suitable is True

    def test_analyze_from_content_security(self, analyzer: AIFitAnalyzer) -> None:
        """Security issues should have lower fit."""
        result = analyzer.analyze_from_content(
            title="Security vulnerability",
            body="There's a security issue.",
            labels=["security"],
            repo_has_tests=True,
            repo_has_ci=True,
        )
        # Security issues should have concerns
        assert len(result.concerns) > 0
        assert any("security" in c.lower() for c in result.concerns)

    def test_repo_with_tests_bonus(self, analyzer: AIFitAnalyzer) -> None:
        """Repos with tests should score higher."""
        with_tests = analyzer.analyze_from_content(
            title="Fix bug",
            body="Bug fix needed",
            labels=[],
            repo_has_tests=True,
            repo_has_ci=True,
        )

        without_tests = analyzer.analyze_from_content(
            title="Fix bug",
            body="Bug fix needed",
            labels=[],
            repo_has_tests=False,
            repo_has_ci=False,
        )

        assert with_tests.score > without_tests.score

    def test_subjective_requirements_concern(self, analyzer: AIFitAnalyzer) -> None:
        """Subjective requirements should add concerns."""
        result = analyzer.analyze_from_content(
            title="Improve UX",
            body="This is subjective and based on opinion.",
            labels=[],
            repo_has_tests=True,
            repo_has_ci=True,
        )
        assert len(result.concerns) > 0
