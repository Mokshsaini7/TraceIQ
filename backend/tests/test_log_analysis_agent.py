"""Unit tests for Log Analysis Agent.
"""

from bugdiag.agents.log_analysis_agent import LogAnalysisAgent

def test_log_analysis_python_traceback():
    agent = LogAnalysisAgent()
    trace = """Traceback (most recent call last):
  File "/app/services/auth.py", line 88, in verify_token
    payload = jwt.decode(token, secret)
  File "/app/utils/jwt.py", line 14, in decode
    raise InvalidTokenError("Signature verification failed")
InvalidTokenError: Signature verification failed"""

    result = agent.analyze(stack_trace=trace, error_logs=None)
    assert result.has_stack_trace is True
    assert result.exception_type == "InvalidTokenError"
    assert "Signature verification failed" in result.error_message
    assert len(result.stack_frames) >= 2
    assert "/app/services/auth.py" in result.suspect_files

def test_log_analysis_java_stack_trace():
    agent = LogAnalysisAgent()
    trace = """java.lang.NullPointerException: Name cannot be null
 at org.eclipse.jdt.internal.compiler.lookup.MethodBinding.isVarargs(MethodBinding.java:490)
 at org.eclipse.jdt.internal.compiler.ast.LambdaExpression.resolveType(LambdaExpression.java:231)"""

    result = agent.analyze(stack_trace=trace, error_logs=None)
    assert result.has_stack_trace is True
    assert result.exception_type == "java.lang.NullPointerException"
    assert len(result.stack_frames) == 2
    assert result.stack_frames[0].line == 490
