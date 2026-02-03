"""
git-gud-samaritans

AI-powered open source contribution engine using nexus-agents orchestration.

$ git gud --help-others
"""

__version__ = "0.1.0"
__author__ = "William Zujkowski"

from .contribute import Contributor
from .discovery import Discoverer
from .triage import Triager

__all__ = [
    "Contributor",
    "Discoverer",
    "Triager",
    "__version__",
]
