"""
Utility module providing common functionality across the application.
"""
from .logging import (
    print_lg,
    error_log,
    critical_error_log,
    debug_log,
    warning_log,
    get_screenshot_path,
    format_json_output
)
from .element_helpers import (
    try_linkText,
    try_xp,
    find_by_class,
    try_find_by_classes,
    text_input_by_ID,
    text_input,
    wait_span_click,
    multi_sel_noWait,
    boolean_button_click,
    scroll_to_view,
    buffer
)

__all__ = [
    # Logging utilities
    'print_lg',
    'error_log',
    'critical_error_log',
    'debug_log',
    'warning_log',
    'get_screenshot_path',
    'format_json_output',
    
    # Element interaction helpers
    'try_linkText',
    'try_xp',
    'find_by_class',
    'try_find_by_classes',
    'text_input_by_ID',
    'text_input',
    'wait_span_click',
    'multi_sel_noWait',
    'boolean_button_click',
    'scroll_to_view',
    'buffer'
]
