"""Security utilities for Ra'd AI.

This module provides input sanitization, validation, and security-related
functions to protect against malicious input and ensure data integrity.

Usage:
    from utils.security import sanitize_query, validate_input

    safe_query = sanitize_query(user_input)
    is_valid, error = validate_input(user_input, max_length=2000)
"""

import re
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

# Maximum allowed query length
MAX_QUERY_LENGTH = 2000

# Minimum meaningful query length
MIN_QUERY_LENGTH = 3

# Patterns that might indicate malicious input
SUSPICIOUS_PATTERNS = [
    r'<script\b',           # Script tags
    r'javascript:',         # JavaScript protocol
    r'on\w+\s*=',          # Event handlers (onclick, onerror, etc.)
    r'eval\s*\(',          # eval() calls
    r'exec\s*\(',          # exec() calls
    r'__import__',         # Python imports
    r'subprocess',         # Subprocess calls
    r'os\s*\.\s*system',   # OS system calls
    r'import\s+os',        # OS module import
    r'from\s+os\s+import', # OS import
]

# Characters to strip from queries
CONTROL_CHARS_PATTERN = r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]'


def sanitize_query(query: str) -> str:
    """Sanitize user query by removing potentially harmful content.

    This function removes control characters, excessive whitespace, and
    normalizes the query for safe processing.

    Args:
        query: Raw user query string

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query is None, empty, or exceeds maximum length
    """
    if query is None:
        logger.warning("Attempted to sanitize None query")
        raise ValueError("Query cannot be None")

    if not isinstance(query, str):
        logger.warning(f"Invalid query type: {type(query)}")
        raise ValueError(f"Query must be a string, got {type(query).__name__}")

    # Strip leading/trailing whitespace
    query = query.strip()

    if not query:
        logger.warning("Empty query after stripping whitespace")
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        logger.warning(f"Query exceeds max length: {len(query)} > {MAX_QUERY_LENGTH}")
        raise ValueError(f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters")

    if len(query) < MIN_QUERY_LENGTH:
        logger.warning(f"Query too short: {len(query)} < {MIN_QUERY_LENGTH}")
        raise ValueError(f"Query must be at least {MIN_QUERY_LENGTH} characters")

    # Remove control characters
    query = re.sub(CONTROL_CHARS_PATTERN, '', query)

    # Normalize whitespace (collapse multiple spaces to single)
    query = ' '.join(query.split())

    logger.debug(f"Sanitized query: {query[:50]}...")
    return query


def validate_input(
    text: str,
    max_length: int = MAX_QUERY_LENGTH,
    min_length: int = MIN_QUERY_LENGTH,
    allow_empty: bool = False
) -> Tuple[bool, Optional[str]]:
    """Validate input text against security constraints.

    Args:
        text: Input text to validate
        max_length: Maximum allowed length
        min_length: Minimum required length
        allow_empty: Whether empty strings are allowed

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None
    """
    if text is None:
        return False, "Input cannot be None"

    if not isinstance(text, str):
        return False, f"Input must be a string, got {type(text).__name__}"

    text = text.strip()

    if not text and not allow_empty:
        return False, "Input cannot be empty"

    if len(text) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters"

    if len(text) < min_length and not allow_empty:
        return False, f"Input must be at least {min_length} characters"

    return True, None


def check_suspicious_patterns(query: str) -> Tuple[bool, List[str]]:
    """Check if query contains suspicious patterns.

    This function scans for patterns that might indicate injection attacks
    or other malicious input.

    Args:
        query: Query string to check

    Returns:
        Tuple of (has_suspicious, list_of_matches)
        If no suspicious patterns found, list is empty
    """
    if not query:
        return False, []

    found_patterns = []
    query_lower = query.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            found_patterns.append(pattern)
            logger.warning(f"Suspicious pattern found in query: {pattern}")

    return len(found_patterns) > 0, found_patterns


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file system operations.

    Args:
        filename: Raw filename string

    Returns:
        Sanitized filename safe for file system use

    Raises:
        ValueError: If filename is invalid
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Remove path separators and null bytes
    filename = re.sub(r'[/\\:\x00]', '_', filename)

    # Remove other potentially dangerous characters
    filename = re.sub(r'[<>"|?*]', '_', filename)

    # Collapse multiple underscores
    filename = re.sub(r'_+', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    if not filename:
        raise ValueError("Filename is empty after sanitization")

    # Limit length (most filesystems support 255 chars)
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 200 - len(ext) - 1 if ext else 200
        filename = f"{name[:max_name_len]}.{ext}" if ext else name[:200]

    return filename


def mask_sensitive_data(text: str, patterns: Optional[List[str]] = None) -> str:
    """Mask sensitive data in text for logging purposes.

    Args:
        text: Text that may contain sensitive data
        patterns: Optional list of regex patterns to mask

    Returns:
        Text with sensitive data masked
    """
    if not text:
        return text

    # Default patterns for sensitive data
    default_patterns = [
        (r'(api[_-]?key["\s:=]+)["\']?[\w-]{10,}', r'\1***MASKED***'),
        (r'(password["\s:=]+)["\']?[\w@#$%^&*!]+', r'\1***MASKED***'),
        (r'(secret["\s:=]+)["\']?[\w-]+', r'\1***MASKED***'),
        (r'(token["\s:=]+)["\']?[\w.-]+', r'\1***MASKED***'),
        (r'sk-or-v1-[\w-]+', '***API_KEY_MASKED***'),
    ]

    result = text
    for pattern, replacement in default_patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def is_safe_path(path: str, base_dir: str) -> bool:
    """Check if a path is safely within a base directory.

    Prevents directory traversal attacks.

    Args:
        path: Path to validate
        base_dir: Base directory that path must be within

    Returns:
        True if path is safe, False otherwise
    """
    import os

    # Resolve to absolute paths
    abs_base = os.path.abspath(base_dir)
    abs_path = os.path.abspath(os.path.join(base_dir, path))

    # Check if the resolved path starts with base directory
    return abs_path.startswith(abs_base)


def rate_limit_key(identifier: str, action: str = "query") -> str:
    """Generate a rate limiting key for an identifier.

    Args:
        identifier: User or session identifier
        action: Type of action being rate limited

    Returns:
        Rate limit key string
    """
    import hashlib

    # Create a hash to anonymize the identifier
    id_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    return f"rate_limit:{action}:{id_hash}"
