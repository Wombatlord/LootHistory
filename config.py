from typing import Optional


class Config:
    """
    Filter configuration
    """

    date_filter: Optional[str] = None
    """
    date_filter is a user supplied month and date used to filter data based on item received dates.
    format: 0915 (MMDD)
    """

    charts_dir: str = "./charts"
    """
    Destination dir for generation of charts
    """
