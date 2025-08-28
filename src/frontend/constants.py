# External Resources
BUG_REPORTS_GT = "https://github.com/snoozleEmily/transcriptor/issues" 

# Color Constants
LOGO_COLOR = "#EBAC36"  # Primary brand color used for the app logo (golden yellow)
PLACEHOLDER_TEXT = "#334345"  # Color for placeholder text in input fields (dark teal blue)

# UI Theme Configuration
THEMES = {
    # Light theme configuration - suitable for daytime/well-lit environments
    "default": {
        "bg": "#F5F5F5",          # Main background color (light gray)
        "fg": "#333333",          # Primary text color (dark gray)
        "button_bg": "#A5D9F1",   # Default button background (light blue)
        "active_bg": "#6CA0B8",   # Active/selected button background (medium blue)
        "console_fg":"#333333",   # Text color in console (black)
        "console_bg":"#F5F5F5",   # Main background color in console (light gray always)
        "active_fg": "#000000",   # Text color for active elements (black)
        "message": "#00707D",     # Notification/copy confirmation color (teal blue)
    },
    # Dark theme configuration - reduces eye strain in low-light conditions
    "dark": {
        "bg": "#2E3B4E",          # Main background color (dark navy blue)
        "fg": "#FFFFFF",          # Primary text color (white)
        "button_bg": "#3C8DBC",   # Default button background (medium blue)
        "active_bg": "#367FA6",   # Active/selected button background (darker blue)
        "console_fg":"#333333",   # Text color in console (black)
        "console_bg":"#F5F5F5",   # Main background color in console (light gray always)
        "active_fg": "#FFFFFF",   # Text color for active elements (white)
        "message": "#FFFF00",     # Notification/copy confirmation color (yellow)
    }
}

# Font Configuration
FONTS = {
    "title": ("Courier New", 16),       # Main title font (monospace, medium size)
    "default": ("Courier New", 10),     # Primary text font (monospace, standard size)
    "console": ("Consolas", 10),        # Terminal/console output font (clean monospace)
    "emoji_large": ("Segoe UI Emoji", 64),  # Large emoji display (presentation size)
    "emoji_medium": ("Segoe UI Emoji", 36), # Medium emoji (button/header size)
    "emoji_small": ("Segoe UI Emoji", 12)   # Small emoji (inline text size)
}

# For PDF Styling
PDF_COLORS = {
    "title": "#00468B",        # Dark blue for main titles
    "heading": "#00468B",      # Dark blue for headings
    "text": "#282828",         # Dark gray for regular text
    "bullet": "#000000",       # Black for bullet points
    "header_line": "#2E3B4E",  # Navy blue for header/footer lines
    "footer_text": "#282828",  # Dark gray for footer text
}
