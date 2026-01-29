"""
Code Display Components
=======================
Monaco editor integration for syntax-highlighted code display
with copy functionality and language detection.
"""

import re
from dataclasses import dataclass
from typing import Literal, Optional
import streamlit as st

# --- OPTIONAL DEPENDENCY IMPORTS ---
try:
    from streamlit_monaco import st_monaco
    MONACO_AVAILABLE = True
except ImportError:
    MONACO_AVAILABLE = False

# Try alternative code editor
try:
    from streamlit_code_editor import code_editor
    CODE_EDITOR_AVAILABLE = True
except ImportError:
    CODE_EDITOR_AVAILABLE = False


# --- THEME COLORS (matching app theme) ---
THEME = {
    "gold_primary": "#D4A84B",
    "gold_light": "#E8C872",
    "gold_dark": "#B8860B",
    "bg_dark": "#0E0E0E",
    "bg_card": "#1A1A1A",
    "bg_input": "#2A2A2A",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0B0",
}

# Monaco editor theme configuration
MONACO_THEME = {
    "base": "vs-dark",
    "inherit": True,
    "rules": [
        {"token": "comment", "foreground": "6A9955"},
        {"token": "keyword", "foreground": "569CD6"},
        {"token": "string", "foreground": "CE9178"},
        {"token": "number", "foreground": "B5CEA8"},
        {"token": "type", "foreground": "4EC9B0"},
        {"token": "function", "foreground": "DCDCAA"},
        {"token": "variable", "foreground": "9CDCFE"},
    ],
    "colors": {
        "editor.background": THEME["bg_input"],
        "editor.foreground": THEME["text_primary"],
        "editor.lineHighlightBackground": "#2F2F2F",
        "editorCursor.foreground": THEME["gold_primary"],
        "editor.selectionBackground": "#264F78",
        "editorLineNumber.foreground": THEME["text_secondary"],
    },
}


SupportedLanguage = Literal["python", "sql", "json", "text"]


def detect_language(code: str) -> SupportedLanguage:
    """
    Detect the programming language of a code snippet.

    Uses pattern matching to identify Python, SQL, or JSON.

    Args:
        code: The code string to analyze.

    Returns:
        Detected language ('python', 'sql', 'json', or 'text').
    """
    if not code or not code.strip():
        return "text"

    code_lower = code.lower().strip()

    # SQL detection patterns
    sql_patterns = [
        r'\bselect\b.*\bfrom\b',
        r'\binsert\b.*\binto\b',
        r'\bupdate\b.*\bset\b',
        r'\bdelete\b.*\bfrom\b',
        r'\bcreate\b.*\btable\b',
        r'\bdrop\b.*\btable\b',
        r'\balter\b.*\btable\b',
        r'\bjoin\b',
        r'\bwhere\b.*\band\b',
        r'\bgroup\s+by\b',
        r'\border\s+by\b',
        r'\bhaving\b',
    ]

    for pattern in sql_patterns:
        if re.search(pattern, code_lower, re.IGNORECASE | re.DOTALL):
            return "sql"

    # JSON detection
    stripped = code.strip()
    if (stripped.startswith('{') and stripped.endswith('}')) or \
       (stripped.startswith('[') and stripped.endswith(']')):
        try:
            import json
            json.loads(code)
            return "json"
        except (json.JSONDecodeError, ValueError):
            pass

    # Python detection patterns
    python_patterns = [
        r'^import\s+\w+',
        r'^from\s+\w+\s+import',
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+[:\(]',
        r'\bif\s+.*:\s*$',
        r'\bfor\s+\w+\s+in\s+',
        r'\bwhile\s+.*:\s*$',
        r'\btry:\s*$',
        r'\bexcept\b',
        r'\bwith\s+.*\s+as\s+',
        r'\blambda\s+',
        r'\breturn\s+',
        r'print\s*\(',
        r'pd\.',  # Pandas
        r'df\.',  # DataFrame
        r'np\.',  # NumPy
        r'plt\.',  # Matplotlib
        r'\.groupby\(',
        r'\.merge\(',
        r'\.filter\(',
        r'\.apply\(',
    ]

    for pattern in python_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return "python"

    # Default to Python for PandasAI context
    return "python"


@dataclass
class CodeDisplay:
    """
    Code display configuration and rendering.

    Attributes:
        code: The code string to display.
        language: Programming language for syntax highlighting.
        height: Editor height in pixels.
        readonly: Whether the editor is read-only.
        show_copy_button: Whether to show copy button.
        show_line_numbers: Whether to show line numbers.
    """
    code: str
    language: Optional[SupportedLanguage] = None
    height: int = 300
    readonly: bool = True
    show_copy_button: bool = True
    show_line_numbers: bool = True

    def __post_init__(self):
        """Auto-detect language if not provided."""
        if self.language is None:
            self.language = detect_language(self.code)

    def render(self, key: Optional[str] = None) -> Optional[str]:
        """
        Render the code display component.

        Args:
            key: Unique key for the component.

        Returns:
            The code content (may be modified if not readonly).
        """
        return render_code(
            code=self.code,
            language=self.language,
            height=self.height,
            readonly=self.readonly,
            show_copy_button=self.show_copy_button,
            show_line_numbers=self.show_line_numbers,
            key=key,
        )


def copy_code_button(code: str, key: Optional[str] = None) -> None:
    """
    Render a copy-to-clipboard button for code.

    Args:
        code: The code to copy.
        key: Unique key for the button.
    """
    button_key = key or f"copy_btn_{hash(code)}"

    # Escape special characters for JavaScript template literal
    escaped_code = code.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

    # Build style strings
    gold_dark = THEME['gold_dark']
    gold_primary = THEME['gold_primary']
    bg_dark = THEME['bg_dark']

    # Use JavaScript to copy to clipboard
    copy_script = f"""
    <button onclick="navigator.clipboard.writeText(`{escaped_code}`).then(() => {{{{
        this.innerHTML = 'Copied!';
        setTimeout(() => {{{{ this.innerHTML = 'Copy Code'; }}}}, 2000);
    }}}})" style="
        background: linear-gradient(135deg, {gold_dark} 0%, {gold_primary} 100%);
        color: {bg_dark};
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(212,168,75,0.3)'"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
        Copy Code
    </button>
    """

    st.markdown(copy_script, unsafe_allow_html=True)


def render_code(
    code: str,
    language: Optional[SupportedLanguage] = None,
    height: int = 300,
    readonly: bool = True,
    show_copy_button: bool = True,
    show_line_numbers: bool = True,
    key: Optional[str] = None,
) -> Optional[str]:
    """
    Render code with syntax highlighting using Monaco editor or fallback.

    Attempts to use streamlit-monaco for rich editing experience,
    falls back to streamlit-code-editor or native st.code.

    Args:
        code: The code string to display.
        language: Programming language ('python', 'sql', 'json', 'text').
        height: Editor height in pixels.
        readonly: Whether the editor is read-only.
        show_copy_button: Whether to show copy button.
        show_line_numbers: Whether to show line numbers.
        key: Unique key for the component.

    Returns:
        The code content (may be modified if not readonly).
    """
    if not code:
        st.info("No code to display.")
        return None

    # Auto-detect language if not provided
    if language is None:
        language = detect_language(code)

    # Generate key if not provided
    if key is None:
        key = f"code_display_{hash(code) % 10000}"

    result_code = code

    # Header with language badge and copy button
    col1, col2 = st.columns([3, 1])
    with col1:
        lang_badge_color = {
            "python": "#3776AB",
            "sql": "#F29111",
            "json": "#6DB33F",
            "text": THEME["text_secondary"],
        }.get(language, THEME["text_secondary"])

        st.markdown(
            f"""
            <span style="
                background: {lang_badge_color};
                color: white;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            ">{language}</span>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if show_copy_button:
            copy_code_button(code, key=f"{key}_copy")

    # Try Monaco editor first
    if MONACO_AVAILABLE:
        try:
            result_code = st_monaco(
                value=code,
                language=language if language != "text" else "plaintext",
                height=height,
                theme="vs-dark",
                key=f"{key}_monaco",
                options={
                    "readOnly": readonly,
                    "minimap": {"enabled": False},
                    "lineNumbers": "on" if show_line_numbers else "off",
                    "scrollBeyondLastLine": False,
                    "fontSize": 14,
                    "fontFamily": "'Fira Code', 'Consolas', monospace",
                    "automaticLayout": True,
                    "wordWrap": "on",
                    "folding": True,
                    "renderLineHighlight": "line",
                    "scrollbar": {
                        "vertical": "auto",
                        "horizontal": "auto",
                    },
                },
            )
            return result_code if result_code else code
        except Exception:
            pass  # Fall through to next option

    # Try streamlit-code-editor as second option
    if CODE_EDITOR_AVAILABLE:
        try:
            response = code_editor(
                code,
                lang=language if language != "text" else "text",
                height=height,
                theme="dark",
                key=f"{key}_editor",
                options={
                    "readOnly": readonly,
                    "showLineNumbers": show_line_numbers,
                },
            )
            if response and "text" in response:
                return response["text"]
            return code
        except Exception:
            pass  # Fall through to fallback

    # Fallback to native Streamlit code display
    _render_fallback_code(
        code=code,
        language=language,
        height=height,
        show_line_numbers=show_line_numbers,
    )

    return code


def _render_fallback_code(
    code: str,
    language: SupportedLanguage,
    height: int,
    show_line_numbers: bool,
) -> None:
    """
    Render code using native Streamlit components.

    Args:
        code: The code string to display.
        language: Programming language.
        height: Target height (approximate).
        show_line_numbers: Whether to show line numbers.
    """
    # Calculate approximate line count for height
    line_count = code.count('\n') + 1

    # Custom styling for fallback
    st.markdown(
        f"""
        <style>
            .stCode {{
                max-height: {height}px !important;
                overflow-y: auto !important;
            }}
            .stCode pre {{
                background: {THEME['bg_input']} !important;
                border: 1px solid rgba(212, 168, 75, 0.3) !important;
                border-radius: 8px !important;
                padding: 16px !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add line numbers manually if requested
    if show_line_numbers:
        lines = code.split('\n')
        max_line_num_width = len(str(len(lines)))
        numbered_code = '\n'.join(
            f"{str(i+1).rjust(max_line_num_width)} | {line}"
            for i, line in enumerate(lines)
        )
        # Display without language for numbered version
        st.code(numbered_code, language=None)
    else:
        st.code(code, language=language)


def render_code_with_explanation(
    code: str,
    explanation: Optional[str] = None,
    language: Optional[SupportedLanguage] = None,
    key: Optional[str] = None,
) -> None:
    """
    Render code with an optional explanation panel.

    Args:
        code: The code string to display.
        explanation: Optional explanation text.
        language: Programming language.
        key: Unique key for the component.
    """
    if explanation:
        col1, col2 = st.columns([2, 1])
        with col1:
            render_code(code, language=language, key=key)
        with col2:
            st.markdown(
                f"""
                <div style="
                    background: {THEME['bg_card']};
                    border: 1px solid rgba(212, 168, 75, 0.2);
                    border-radius: 8px;
                    padding: 16px;
                    height: 100%;
                ">
                    <h4 style="color: {THEME['gold_light']}; margin-bottom: 12px;">
                        Explanation
                    </h4>
                    <p style="color: {THEME['text_secondary']}; font-size: 14px; line-height: 1.6;">
                        {explanation}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        render_code(code, language=language, key=key)


def render_code_tabs(
    code_snippets: dict[str, str],
    key: Optional[str] = None,
) -> None:
    """
    Render multiple code snippets in tabs.

    Args:
        code_snippets: Dictionary mapping tab names to code strings.
        key: Base key for the components.
    """
    if not code_snippets:
        st.info("No code snippets to display.")
        return

    tabs = st.tabs(list(code_snippets.keys()))

    for idx, (tab_name, code) in enumerate(code_snippets.items()):
        with tabs[idx]:
            tab_key = f"{key}_{tab_name}" if key else f"tab_{idx}"
            render_code(code, key=tab_key)
