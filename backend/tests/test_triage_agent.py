"""Unit tests for Triage Agent.
"""

from bugdiag.agents.triage_agent import TriageAgent

def test_triage_agent_null_pointer_classification():
    agent = TriageAgent()
    result = agent.analyze(
        title="NullPointerException in UserProfileService",
        description="The application threw a NullPointerException when accessing user.profile.getSettings().",
        stack_trace="java.lang.NullPointerException at com.example.service.UserProfileService.get(UserProfileService.java:42)",
        language_hint="Java"
    )

    assert result.category == "NullPointer"
    assert result.programming_language == "Java"
    assert result.severity in ["high", "critical"]
    assert result.completeness_score > 0.0

def test_triage_agent_memory_classification():
    agent = TriageAgent()
    result = agent.analyze(
        title="Spark driver OutOfMemoryError heap space crash",
        description="Shuffle spill failed with java.lang.OutOfMemoryError: Java heap space during SortMergeJoin operation.",
        stack_trace="java.lang.OutOfMemoryError: Java heap space",
        language_hint="Scala"
    )

    assert result.category == "Memory"
    assert result.severity == "critical"
    assert result.priority == "p1"
