#! /usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import List

import plots
from config import Config
from ledger import Ledger

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

_teams = {"X": team_x, "Y": team_y}


def parse_args() -> List[str]:
    args = sys.argv[1:]
    team_flags = {*_teams.keys()}
    return [*({*args} & team_flags)]


def date_filter_prompt():
    supplied_date = input("Please enter a date: MMDD\n")
    Config.date_filter = f"2021{supplied_date}"


def main(teams: List[str]) -> None:
    history = get_history()

    guild = Ledger(history)

    # order by descending values.
    datasets = [guild.get_main_spec_dataset(_teams[team]) for team in teams]
    color_sequence = guild.sequence_role_colors(datasets[0], _teams[sys.argv[1]])

    bar = plots.BarChart(datasets[0], color_sequence)
    pie = plots.PieChart(datasets[0], color_sequence)
    histogram = plots.Histogram(datasets[0])
    bar_and_pie = plots.CombinedPieBar(datasets[0], color_sequence, sys.argv[1])

    charts = [bar_and_pie]

    prep_charts_dir()

    for chart in charts:
        # chart.render()
        chart.save_chart(sys.argv[1])


def prep_charts_dir():
    Path(Config.charts_dir).mkdir(parents=True, exist_ok=True)


def get_history():
    with open("history/character-json.json") as fusion_history:
        history = json.load(fusion_history)
    return history


chosen_team = parse_args()
date_filter_prompt()
main(chosen_team)

# charts = functools.reduce(
#     operator.add,
#     [
#         [constructor(dataset) for dataset in datasets]
#         for constructor in [plots.PieChart, plots.BarChart]
#     ]
# )
