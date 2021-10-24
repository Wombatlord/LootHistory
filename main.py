#! /usr/bin/env python3
import functools
import json
import operator
import sys
from typing import List

import plots
from ledger import Ledger

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

_teams = {"X": team_x, "Y": team_y}


def parse_args() -> List[str]:
    args = sys.argv[1:]
    team_flags = {*_teams.keys()}
    return [*({*args} & team_flags)]


def main(teams: List[str]) -> None:
    with open("history/character-json.json") as fusion_history:
        history = json.load(fusion_history)

    guild = Ledger(history)

    # order by descending values.
    datasets = [guild.get_main_spec_dataset(_teams[team]) for team in teams]
    color_sequence = guild.sequence_role_colors(datasets[0], _teams[sys.argv[1]])

    bar = plots.BarChart(datasets[0], color_sequence)
    pie = plots.PieChart(datasets[0], color_sequence)
    histogram = plots.Histogram(datasets[0])
    bar_and_pie = plots.CombinedPieBar(datasets[0], color_sequence, sys.argv[1])

    charts = [bar_and_pie]

    for chart in charts:
        chart.render()
        # chart.save_chart(sys.argv[1])


chosen_team = parse_args()
main(chosen_team)

# charts = functools.reduce(
#     operator.add,
#     [
#         [constructor(dataset) for dataset in datasets]
#         for constructor in [plots.PieChart, plots.BarChart]
#     ]
# )
