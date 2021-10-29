from typing import Optional, Set


class Config:
    """
    Filter configuration
    """

    date_filter: Optional[str] = None
    """
    date_filter is a user supplied month and date used to filter data based on item received dates.
    format: 0915 (MMDD)
    """

    style_choice: Optional[str] = None
    """
    style_choice is a user supplied string used to select a visual style for charts.
    Configures titles and colors of a figure and chart elements within that figure.
    New styles can be added by copying and tweaking the default style in Styles.py
    """

    charts_dir: str = "./charts"
    """
    Destination dir for generation of charts
    """

    logs_dir: str = "./logs"
    """
    Destination for log data to accompany charts.
    """

    history_dir: str = "./history"
    """
    Source dir for raw data to be visualised
    """

    output_charts = ("bar", "pie", "hist", "combined")
    """
    Available chart types
    """

    excluded_charts = ("bar", "pie", "hist")
    """
    Add charts to this tuple to exclude them from being generated
    """

    excluded_officer_note = ("Banking", "PvP", "OS", "OSPvP", "Pass", "Other")
    """
    Add any term in the "officer_note" field of received items that is not associated to a mainspec upgrade.
    ie. terms associated to any gear you do not wish to include in a chart.
    """

    @classmethod
    def get_charts_to_render(cls) -> Set[str]:
        return {*cls.output_charts} - {*cls.excluded_charts}