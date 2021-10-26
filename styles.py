from typing import List, Dict


def choose_style(style) -> List[str]:
    return [element for (key, element) in Style.styles[style].items()]


def choose_bar_style(style) -> Dict[str, str]:
    return {key: value for (key, value) in Style.bar_styles[style].items()}


class Style:
    fonts = {
        "inconsolata": "Inconsolata NF"
    }

    colors = {
        "goldenrod": "xkcd:goldenrod",
        "ocean": "xkcd:ocean",
        "almost_black": "xkcd:almost black"
    }

    styles = {
        "default": {
            "text.color": colors["ocean"],
            "axes.labelcolor": colors["goldenrod"],
            "axes.edgecolor": colors["ocean"],
            "axes.titlecolor": colors["goldenrod"],
            "font.family": fonts["inconsolata"],
        }
    }

    bar_styles = {
        "default": {
            "title": "Loot Assignment Totals",
            "xlabel": "Mainspec BIS / Upgrade pieces awarded",
            "tick_colors": colors["goldenrod"],
            "face_color": colors["almost_black"]
        }
    }
