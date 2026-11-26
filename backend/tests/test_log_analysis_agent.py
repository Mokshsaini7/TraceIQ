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


def test_log_analysis_node_stack_trace():
    trace = "TypeError: Cannot read properties of undefined (reading 'id')\n    at loadUser (/srv/app/users.js:42:9)\n    at processRequest (/srv/app/router.js:18:3)"
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "TypeError"
    assert "Cannot read properties" in result.error_message
    assert result.failure_point.file == "/srv/app/users.js"
    assert result.failure_point.line == 42
    assert result.code_path[1].file == "/srv/app/router.js"
    assert 0 <= result.confidence_score <= 1


def test_log_analysis_python_failure_is_innermost_frame():
    trace = '''Traceback (most recent call last):
  File "/app/api.py", line 10, in handler
    service.run()
  File "/app/service.py", line 25, in run
    raise ValueError("invalid state")
ValueError: invalid state'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.failure_point.file == "/app/service.py"
    assert result.failure_point.line == 25
    assert result.failure_point.method == "run"


def test_log_analysis_go_panic_format():
    trace = '''panic: runtime error: index out of range
\ngoroutine 1 [running]:
main.process()
\t/app/main.go:44 +0x20'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "panic"
    assert result.has_stack_trace
    assert result.failure_point.file == "/app/main.go"
    assert result.failure_point.line == 44


def test_log_analysis_cpp_gdb_format():
    trace = '''#0  0x00007f in AuthService::verify() at /src/auth.cpp:91
#1  0x00008f in main() at /src/main.cpp:20'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.failure_point.file == "/src/auth.cpp"
    assert result.failure_point.line == 91
    assert "AuthService::verify" in result.failure_point.method


def test_log_analysis_without_frames_has_conservative_confidence():
    result = LogAnalysisAgent().analyze(None, "2026-11-23 ERROR request failed; retry later")
    assert result.has_stack_trace is False
    assert result.failure_point is None
    assert result.code_path == []
    assert result.confidence_score < 0.5


def test_log_analysis_empty_input_schema_is_stable():
    result = LogAnalysisAgent().analyze(None, None)
    payload = result.model_dump()
    assert set(("exception_type", "error_message", "failure_point", "code_path", "confidence_score")).issubset(payload)


def test_log_analysis_dotnet_stack_trace():
    trace = '''System.InvalidOperationException: Object is not ready
   at Billing.PaymentService.Charge() in C:\\src\\Billing\\PaymentService.cs:line 73
   at Billing.ApiController.Post() in C:\\src\\Billing\\ApiController.cs:line 21'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "System.InvalidOperationException"
    assert result.failure_point.line == 73
    assert result.failure_point.class_name == "Billing.PaymentService"


def test_log_analysis_ruby_stack_trace():
    trace = '''NoMethodError: undefined method `name' for nil
from /app/models/user.rb:31:in `display_name'
from /app/controllers/users_controller.rb:12:in `show`'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "NoMethodError"
    assert result.failure_point.file == "/app/models/user.rb"
    assert result.failure_point.line == 31


def test_log_analysis_php_fatal_stack_trace():
    trace = '''PHP Fatal error: Uncaught Error: Call to undefined method User::label()
#0 /srv/app/controllers/UserController.php(58): UserService->format()
#1 /srv/app/public/index.php(12): UserController->show()'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "Error"
    assert result.detected_format == "php"
    assert result.failure_point.file == "/srv/app/controllers/UserController.php"
    assert result.failure_point.line == 58
    assert result.frame_count == 2


def test_log_analysis_structured_json_logger():
    logs = '{"timestamp":"2026-11-25T10:00:00Z","level":"ERROR","exception":{"type":"DatabaseTimeout","message":"pool acquisition timed out"}}'
    result = LogAnalysisAgent().analyze(None, logs)
    assert result.exception_type == "DatabaseTimeout"
    assert result.error_message == "pool acquisition timed out"
    assert result.detected_format == "unknown"
    assert result.failure_point is None
    assert "Detected DatabaseTimeout" in result.analysis_summary


def test_log_analysis_timestamp_prefixed_java_trace():
    trace = '''2026-11-25 10:22:11,002 ERROR [payment-api] java.lang.IllegalStateException: transaction closed
 at com.acme.PaymentService.commit(PaymentService.java:144)
 at com.acme.PaymentController.pay(PaymentController.java:51)'''
    result = LogAnalysisAgent().analyze(trace, None)
    assert result.exception_type == "java.lang.IllegalStateException"
    assert result.failure_point.file == "PaymentService.java"
    assert result.failure_point.line == 144
    assert result.detected_format == "java"


def test_log_analysis_output_contract_is_complete_and_bounded():
    result = LogAnalysisAgent().analyze("TypeError: bad value\n at run (/app/a.js:8:2)", None)
    payload = result.model_dump()
    assert {"exception_type", "error_message", "failure_point", "code_path", "confidence_score",
            "detected_format", "frame_count", "analysis_summary"}.issubset(payload)
    assert payload["frame_count"] == len(payload["code_path"])
    assert 0 <= payload["confidence_score"] <= 1
