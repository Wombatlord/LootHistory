class Style(dict):
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


def choose_style(style):
    return [element for (key, element) in Style.styles[style].items()]


choose_style("default")
