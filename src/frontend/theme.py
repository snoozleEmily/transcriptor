from tkinter import ttk


from .constants import THEMES, FONTS



def configure_theme(root, theme_name="default"):
    """Configures ttk styles for a given theme"""
    style = ttk.Style(root)
    style.theme_use('clam')
    colors = THEMES[theme_name]

    # Base styles
    base_config = {
        "TFrame": {"background": colors["bg"]},
        "TLabel": {
            "background": colors["bg"],
            "foreground": colors["fg"],
            "font": FONTS["default"]
        },
        "TButton": {
            "background": colors["button_bg"],
            "foreground": colors["fg"],
            "font": FONTS["default"],
            "borderwidth": 0,
            "focuscolor": colors["bg"]
        },
        "TCheckbutton": {
            "background": colors["button_bg"],
            "foreground": colors["fg"],
            "font": FONTS["default"],
            "indicatorcolor": colors["bg"],
            "indicatordepth": 1
        }
    }

    # Apply base configurations
    for element, config in base_config.items():
        style.configure(element, **config)

    # Interactive states
    style.map(
        "TButton",
        background=[("active", colors["active_bg"]), ("disabled", colors["bg"])],
        foreground=[("active", colors["active_fg"])]
    )

    style.map(
        "TCheckbutton",
        indicatorbackground=[
            ("selected", colors["fg"]),
            ("!selected", colors["bg"])
        ]
    )

    # Custom widget styles
    custom_styles = {
        "HeaderTitle.TLabel": {"font": FONTS["title"]},
        "EmojiDisplay.TLabel": {"font": FONTS["emoji_large"]}
    }

    for style_name, config in custom_styles.items():
        style.configure(style_name, **config)