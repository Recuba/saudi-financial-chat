"""Tests for security utilities."""

import pytest
from utils.security import (
    sanitize_query,
    validate_input,
    check_suspicious_patterns,
    sanitize_filename,
    mask_sensitive_data,
    is_safe_path,
    MAX_QUERY_LENGTH,
    MIN_QUERY_LENGTH,
)


class TestSanitizeQuery:
    """Tests for sanitize_query function."""

    def test_sanitize_normal_query(self):
        """Test sanitization of a normal query."""
        query = "What is the revenue of ARAMCO?"
        result = sanitize_query(query)
        assert result == "What is the revenue of ARAMCO?"

    def test_sanitize_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        query = "   What is the revenue?   "
        result = sanitize_query(query)
        assert result == "What is the revenue?"

    def test_sanitize_collapses_whitespace(self):
        """Test that multiple spaces are collapsed."""
        query = "What   is   the   revenue?"
        result = sanitize_query(query)
        assert result == "What is the revenue?"

    def test_sanitize_removes_control_chars(self):
        """Test that control characters are removed."""
        query = "What is\x00 the\x0b revenue?"
        result = sanitize_query(query)
        assert "\x00" not in result
        assert "\x0b" not in result

    def test_sanitize_none_raises(self):
        """Test that None input raises ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            sanitize_query(None)

    def test_sanitize_empty_raises(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sanitize_query("")

    def test_sanitize_whitespace_only_raises(self):
        """Test that whitespace-only input raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sanitize_query("   ")

    def test_sanitize_too_long_raises(self):
        """Test that overly long input raises ValueError."""
        query = "a" * (MAX_QUERY_LENGTH + 1)
        with pytest.raises(ValueError, match="exceeds maximum length"):
            sanitize_query(query)

    def test_sanitize_too_short_raises(self):
        """Test that too short input raises ValueError."""
        query = "ab"
        with pytest.raises(ValueError, match=f"at least {MIN_QUERY_LENGTH}"):
            sanitize_query(query)

    def test_sanitize_non_string_raises(self):
        """Test that non-string input raises ValueError."""
        with pytest.raises(ValueError, match="must be a string"):
            sanitize_query(123)

    def test_sanitize_max_length_accepted(self):
        """Test that exactly max length is accepted."""
        query = "a" * MAX_QUERY_LENGTH
        result = sanitize_query(query)
        assert len(result) == MAX_QUERY_LENGTH


class TestValidateInput:
    """Tests for validate_input function."""

    def test_validate_valid_input(self):
        """Test validation of valid input."""
        is_valid, error = validate_input("Valid query text")
        assert is_valid is True
        assert error is None

    def test_validate_none_invalid(self):
        """Test that None is invalid."""
        is_valid, error = validate_input(None)
        assert is_valid is False
        assert "None" in error

    def test_validate_empty_invalid(self):
        """Test that empty string is invalid by default."""
        is_valid, error = validate_input("")
        assert is_valid is False
        assert "empty" in error

    def test_validate_empty_allowed(self):
        """Test that empty string can be allowed."""
        is_valid, error = validate_input("", allow_empty=True)
        assert is_valid is True
        assert error is None

    def test_validate_too_long(self):
        """Test validation of too long input."""
        is_valid, error = validate_input("a" * 100, max_length=50)
        assert is_valid is False
        assert "50" in error

    def test_validate_too_short(self):
        """Test validation of too short input."""
        is_valid, error = validate_input("ab", min_length=5)
        assert is_valid is False
        assert "5" in error

    def test_validate_non_string(self):
        """Test validation of non-string input."""
        is_valid, error = validate_input(123)
        assert is_valid is False
        assert "string" in error


class TestCheckSuspiciousPatterns:
    """Tests for check_suspicious_patterns function."""

    def test_clean_query(self):
        """Test that clean query has no suspicious patterns."""
        has_suspicious, matches = check_suspicious_patterns(
            "What is the revenue of ARAMCO?"
        )
        assert has_suspicious is False
        assert len(matches) == 0

    def test_script_tag_detected(self):
        """Test that script tags are detected."""
        has_suspicious, matches = check_suspicious_patterns(
            "<script>alert('xss')</script>"
        )
        assert has_suspicious is True
        assert len(matches) > 0

    def test_javascript_protocol_detected(self):
        """Test that javascript: protocol is detected."""
        has_suspicious, matches = check_suspicious_patterns(
            "javascript:alert('xss')"
        )
        assert has_suspicious is True

    def test_event_handler_detected(self):
        """Test that event handlers are detected."""
        has_suspicious, matches = check_suspicious_patterns(
            '<img onerror="alert(1)">'
        )
        assert has_suspicious is True

    def test_eval_detected(self):
        """Test that eval() is detected."""
        has_suspicious, matches = check_suspicious_patterns(
            "eval(userInput)"
        )
        assert has_suspicious is True

    def test_os_system_detected(self):
        """Test that os.system is detected."""
        has_suspicious, matches = check_suspicious_patterns(
            "os.system('rm -rf /')"
        )
        assert has_suspicious is True

    def test_empty_query(self):
        """Test empty query handling."""
        has_suspicious, matches = check_suspicious_patterns("")
        assert has_suspicious is False
        assert len(matches) == 0


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_sanitize_normal_filename(self):
        """Test sanitization of normal filename."""
        result = sanitize_filename("report_2024.csv")
        assert result == "report_2024.csv"

    def test_sanitize_removes_path_separators(self):
        """Test that path separators are removed."""
        result = sanitize_filename("../../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_removes_dangerous_chars(self):
        """Test that dangerous characters are removed."""
        result = sanitize_filename('file<>:"|?*.txt')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result

    def test_sanitize_empty_raises(self):
        """Test that empty filename raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            sanitize_filename("")

    def test_sanitize_truncates_long_filename(self):
        """Test that long filenames are truncated."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_sanitize_preserves_extension(self):
        """Test that extension is preserved on truncation."""
        long_name = "a" * 300 + ".csv"
        result = sanitize_filename(long_name)
        assert result.endswith(".csv")


class TestMaskSensitiveData:
    """Tests for mask_sensitive_data function."""

    def test_mask_api_key(self):
        """Test that API keys are masked."""
        text = 'api_key="sk-or-v1-abc123xyz"'
        result = mask_sensitive_data(text)
        assert "sk-or-v1-abc123xyz" not in result
        assert "MASKED" in result

    def test_mask_password(self):
        """Test that passwords are masked."""
        text = 'password="supersecret123"'
        result = mask_sensitive_data(text)
        assert "supersecret123" not in result
        assert "MASKED" in result

    def test_mask_openrouter_key(self):
        """Test that OpenRouter keys are masked."""
        text = "Using key sk-or-v1-abcdefghijklmnop"
        result = mask_sensitive_data(text)
        assert "sk-or-v1-abcdefghijklmnop" not in result

    def test_no_masking_needed(self):
        """Test text without sensitive data."""
        text = "Normal text without secrets"
        result = mask_sensitive_data(text)
        assert result == text

    def test_empty_text(self):
        """Test empty text handling."""
        result = mask_sensitive_data("")
        assert result == ""


class TestIsSafePath:
    """Tests for is_safe_path function."""

    def test_safe_path_in_base(self):
        """Test path within base directory is safe."""
        assert is_safe_path("subdir/file.txt", "/home/user/data") is True

    def test_unsafe_path_traversal(self):
        """Test path traversal is detected."""
        assert is_safe_path("../../../etc/passwd", "/home/user/data") is False

    def test_safe_absolute_path(self):
        """Test absolute path within base is safe."""
        # This depends on actual path resolution
        assert is_safe_path("file.txt", "/tmp") is True
