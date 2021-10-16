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
    with open("fusion-history.json") as fusion_history:
        history = json.load(fusion_history)

    guild = Ledger(history)

    # sanity checking color assignment to players
    for player in guild.teams[team_y]:
        print(f"{player.name} : {player.role} : {player.role_color}")

    datasets = [guild.get_main_spec_dataset(_teams[team]) for team in teams]
    charts = functools.reduce(
        operator.add,
        [
            [constructor(dataset) for dataset in datasets]
            for constructor in [plots.PieChart, plots.BarChart]
        ]
    )

    for chart in charts:
        # chart.render()
        chart.save_chart(sys.argv[1])


teams = parse_args()
main(teams)
