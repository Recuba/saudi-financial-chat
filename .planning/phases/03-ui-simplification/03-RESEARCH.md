# Phase 3: UI Simplification - Research

**Researched:** 2026-02-01
**Domain:** Streamlit UI/UX, Sidebar Removal, Chat-First Interface
**Confidence:** HIGH

## Summary

This phase involves removing the sidebar from the Ra'd AI interface, defaulting the LLM to Gemini 2.0 Flash, and making comparison mode accessible without sidebar navigation. The current codebase uses Streamlit's sidebar extensively for model selection, database info, column reference, view info, and advanced filters.

The standard approach for hiding Streamlit sidebars is CSS injection via `st.markdown()` with `display: none` targeting `[data-testid="stSidebar"]`. Comparison mode can be made accessible through chat commands (parsing user input for `/compare` prefix) or an inline toggle using Streamlit's native `st.popover()` component.

**Primary recommendation:** Remove sidebar completely via CSS, set DEFAULT_MODEL in llm_config.py, move comparison mode trigger to a popover or chat command pattern.

## Standard Stack

The existing codebase is already using the standard stack. No new libraries needed.

### Core (Already in Use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Streamlit | 1.x | Web UI framework | Standard for Python data apps |
| PandasAI | - | Natural language data querying | Core app functionality |
| LiteLLM | - | LLM abstraction layer | OpenRouter integration |

### Supporting (Already in Use)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Plotly | - | Interactive charts | Comparison visualizations |
| Pandas | - | Data manipulation | All data operations |

### No New Dependencies Required
This phase is purely refactoring existing UI code - no new libraries needed.

## Architecture Patterns

### Current Structure (To Be Modified)
```
app.py
├── render_sidebar()         # REMOVE - model selector, filters, column ref
├── mode radio (Chat/Compare) # MODIFY - integrate into main UI differently
└── Main content area        # KEEP - becomes primary interface
```

### Target Structure
```
app.py
├── CSS injection (hide sidebar)
├── Main chat interface
│   ├── Logo/branding
│   ├── Data preview (collapsible)
│   ├── Example questions
│   ├── Chat history
│   ├── Compare toggle (popover or chat command)
│   └── Chat input (pinned bottom)
└── Comparison mode (triggered by toggle/command)
```

### Pattern 1: CSS Sidebar Hiding
**What:** Inject CSS to completely hide the sidebar element
**When to use:** When sidebar should never be visible
**Example:**
```python
# Source: Streamlit community best practice
def hide_sidebar_css() -> str:
    return """
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """

# In app.py, add after st.set_page_config():
st.markdown(hide_sidebar_css(), unsafe_allow_html=True)
```

### Pattern 2: Chat Command Detection
**What:** Parse user input for special commands like `/compare`
**When to use:** Triggering modes/actions via natural text commands
**Example:**
```python
# Source: Standard pattern (Streamlit docs confirm manual parsing)
def parse_chat_command(prompt: str) -> tuple[str, str]:
    """Parse chat input for commands.

    Returns:
        (command, remaining_text) or (None, prompt)
    """
    if prompt.startswith("/"):
        parts = prompt.split(maxsplit=1)
        command = parts[0].lower()
        remaining = parts[1] if len(parts) > 1 else ""
        return command, remaining
    return None, prompt

# Usage in app.py
prompt = st.chat_input("Ask about Saudi financials or type /compare")
if prompt:
    command, text = parse_chat_command(prompt)
    if command == "/compare":
        st.session_state.active_tab = "Compare"
        st.rerun()
    else:
        # Normal chat processing
        process_query(text, data)
```

### Pattern 3: Popover Toggle for Compare Mode
**What:** Use st.popover() for inline mode toggle without sidebar
**When to use:** Quick access to secondary features without page navigation
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/layout/st.popover
with st.popover("Compare Companies", icon=":material/compare_arrows:"):
    st.markdown("**Quick Compare**")
    if st.button("Open Compare Mode", use_container_width=True):
        st.session_state.active_tab = "Compare"
        st.rerun()
```

### Anti-Patterns to Avoid
- **Hiding sidebar via Python conditionals:** Don't use `if False: render_sidebar()` - use CSS for complete removal
- **Leaving dead code:** Remove all sidebar-related imports and function calls, not just hide them
- **Complex state for simple toggle:** Don't over-engineer compare mode access - popover or command is sufficient

## Don't Hand-Roll

Problems that have existing solutions in the codebase or Streamlit:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sidebar hiding | JavaScript injection | CSS `display: none` | Simpler, reliable, no JS needed |
| Compare mode toggle | Custom modal component | `st.popover()` or chat command | Native Streamlit, no dependencies |
| Model defaulting | Runtime selection logic | Set `DEFAULT_MODEL` constant | One-time config change |
| Mode switching | Tab component | Session state + rerun | Already implemented this way |

**Key insight:** Streamlit CSS injection is the most reliable way to hide UI elements. Native `st.popover()` handles toggles without third-party packages.

## Common Pitfalls

### Pitfall 1: Sidebar Flash on Page Load
**What goes wrong:** Sidebar briefly appears before CSS hides it
**Why it happens:** CSS loads after initial render
**How to avoid:**
1. Add `initial_sidebar_state="collapsed"` to `st.set_page_config()`
2. CSS hides it immediately after collapse
**Warning signs:** Visible sidebar flicker on page refresh

### Pitfall 2: Breaking Advanced Filters
**What goes wrong:** Advanced filters (currently in sidebar) stop working
**Why it happens:** `render_advanced_filters()` currently renders inside `st.sidebar` context
**How to avoid:**
1. REMOVE advanced filters entirely (per phase goals - no visible configuration)
2. OR move to main content area in a collapsed expander
**Warning signs:** Filter-related errors after sidebar removal

### Pitfall 3: Test Failures After Sidebar Removal
**What goes wrong:** Tests import from `components.sidebar` and fail
**Why it happens:** `test_sidebar.py` tests sidebar functionality that no longer exists
**How to avoid:**
1. Update/remove `test_sidebar.py` tests
2. Update imports in any files that import sidebar functions
**Warning signs:** Import errors in test suite

### Pitfall 4: Model Selection State Loss
**What goes wrong:** Users can't select models, stuck on default
**Why it happens:** `render_model_selector()` removed with sidebar but session state still expects it
**How to avoid:**
1. Ensure `DEFAULT_MODEL` is set correctly in `llm_config.py`
2. Verify `get_selected_model()` returns default when no selection made
**Warning signs:** LLM errors about missing model

### Pitfall 5: Compare Mode Unreachable
**What goes wrong:** Users can't access comparison feature
**Why it happens:** Mode radio button removed but no alternative provided
**How to avoid:**
1. Implement chat command `/compare` pattern
2. OR add popover toggle near chat input
3. OR keep radio button (it's already in main content area, not sidebar)
**Warning signs:** No way to enter Compare mode in UI

## Code Examples

### Example 1: Complete Sidebar Hiding CSS
```python
# Source: Streamlit community patterns, verified approach
def get_no_sidebar_css() -> str:
    """CSS to completely hide the sidebar."""
    return """
    <style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Remove sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
    """
```

### Example 2: Modified app.py Page Config
```python
# Source: Streamlit docs
st.set_page_config(
    page_title="Ra'd | Saudi Financial AI",
    page_icon="lightning_cloud",
    layout="wide",
    initial_sidebar_state="collapsed",  # ADD THIS
)
```

### Example 3: Chat Command Handler
```python
# Source: Standard pattern for chat interfaces
CHAT_COMMANDS = {
    "/compare": "compare_mode",
    "/help": "show_help",
    "/clear": "clear_history",
}

def handle_chat_command(prompt: str) -> tuple[bool, str | None]:
    """Handle special chat commands.

    Returns:
        (is_command, action_name) or (False, None) for regular queries
    """
    prompt_lower = prompt.strip().lower()

    for command, action in CHAT_COMMANDS.items():
        if prompt_lower.startswith(command):
            return True, action

    return False, None
```

### Example 4: LLM Default Configuration
```python
# In utils/llm_config.py - this is ALREADY correctly set:
DEFAULT_MODEL = "openrouter/google/gemini-2.0-flash-001"
MODEL_DISPLAY_NAME = "Gemini 2.0 Flash"

# Verify get_selected_model() returns default properly:
def get_selected_model() -> str:
    """Get the currently selected model from session state."""
    return st.session_state.get("selected_model", DEFAULT_MODEL)  # Already correct
```

### Example 5: Compare Mode with Popover
```python
# Source: https://docs.streamlit.io/develop/api-reference/layout/st.popover
# Place near chat input area
col1, col2 = st.columns([6, 1])
with col1:
    prompt = st.chat_input("Ask about Saudi financials...")
with col2:
    with st.popover("Compare", icon=":material/compare:"):
        st.markdown("**Compare Companies**")
        st.caption("Side-by-side financial analysis")
        if st.button("Enter Compare Mode", use_container_width=True, type="primary"):
            st.session_state.active_tab = "Compare"
            st.rerun()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| st.beta_columns | st.columns | Streamlit 1.0 | Already using current |
| st.experimental_rerun | st.rerun | Streamlit 1.27+ | Already using current |
| Third-party modals | st.popover / st.dialog | Streamlit 1.33+ | Native solution available |

**Deprecated/outdated:**
- `use_container_width` on st.popover: Deprecated, use `width` parameter instead
- `st.experimental_*` functions: Most graduated to stable API

## Open Questions

Things that couldn't be fully resolved:

1. **Advanced Filters Fate**
   - What we know: Currently in sidebar, used for filtering data before query
   - What's unclear: Should they be completely removed or moved to main area?
   - Recommendation: Per requirements ("no visible configuration complexity"), REMOVE entirely - let LLM handle filtering via natural language

2. **Compare Mode Trigger Preference**
   - What we know: Can use chat command OR popover toggle OR keep existing radio
   - What's unclear: Which provides best UX for target users
   - Recommendation: Keep existing radio button (it's NOT in sidebar, it's in main content) - simplest solution

3. **Database Info Display**
   - What we know: Currently in sidebar expander
   - What's unclear: Is this "visible configuration complexity"?
   - Recommendation: Remove - users don't need to see database stats

## Sources

### Primary (HIGH confidence)
- Codebase analysis: `app.py`, `components/sidebar.py`, `components/comparison_mode.py`, `utils/llm_config.py`
- Streamlit official docs: https://docs.streamlit.io/develop/api-reference/layout/st.popover
- Streamlit official docs: https://docs.streamlit.io/develop/api-reference/chat/st.chat_input

### Secondary (MEDIUM confidence)
- Streamlit community patterns for hiding sidebar: https://discuss.streamlit.io/t/completely-disable-sidebar/35463

### Tertiary (LOW confidence)
- None - all patterns verified against official docs

## Metadata

**Confidence breakdown:**
- Sidebar hiding: HIGH - Well-documented Streamlit pattern, verified in official community
- LLM defaulting: HIGH - Already implemented in codebase, just need to verify
- Compare mode access: HIGH - Multiple working patterns available (popover, command, radio)
- Test updates: MEDIUM - Standard refactoring, but specific test changes need verification

**Research date:** 2026-02-01
**Valid until:** 2026-03-01 (Streamlit stable, no breaking changes expected)

## Implementation Checklist

Based on this research, the planner should address:

1. **CSS injection** - Add sidebar hiding CSS to `styles/css.py` or directly in `app.py`
2. **Page config update** - Add `initial_sidebar_state="collapsed"`
3. **Remove sidebar render** - Delete `render_sidebar()` call from `app.py`
4. **Remove advanced filters** - Delete filter rendering from main content (line 91-92 in app.py)
5. **Verify LLM default** - Confirm DEFAULT_MODEL is Gemini 2.0 Flash (already is)
6. **Keep mode radio** - Existing Chat/Compare radio is NOT in sidebar, already in main content
7. **Update/remove tests** - Modify `test_sidebar.py` for new reality
8. **Clean up imports** - Remove unused sidebar imports from `app.py`
