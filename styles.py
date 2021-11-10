from typing import List, Dict


def choose_style(style) -> List[str]:
    return [element for (key, element) in Style.styles[style].items()]


def choose_bar_style(style) -> Dict[str, str]:
    return {key: value for (key, value) in Style.bar_styles[style].items()}


def choose_over_time_style(style) -> Dict[str, str]:
    return {key: value for (key, value) in Style.over_time_styles[style].items()}


class Style:
    """
    Colors & Visual Styling element configuration.
    """

    fonts = {
        "inconsolata": "Inconsolata NF"
    }

    colors = {
        "goldenrod": "xkcd:goldenrod",
        "ocean": "xkcd:ocean",
        "almost_black": "xkcd:almost black"
    }

    """
    To create a new style, copy and paste each "default" dict and assign a new key.
    The key in role_colors, styles, bar_styles must match.
    eg: "default", "default", "default".
    """
    role_colors = {
        "default": {
            "Warrior": "xkcd:chocolate",
            "Rogue": "xkcd:goldenrod",
            "Hunter": "xkcd:hunter green",
            "Mage": "xkcd:cyan",
            "Warlock": "xkcd:indigo",
            "Priest": "white",
            "Druid": "xkcd:dusty orange",
            "Paladin": "pink",
            "Shaman": "xkcd:royal blue"
        }
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

    over_time_styles = {
        "default": {
            "title": "Loot Over Time",
            "xlabel": "Raid Date",
            "tick_colors": colors["goldenrod"],
            "face_color": colors["almost_black"]
        }
    }
