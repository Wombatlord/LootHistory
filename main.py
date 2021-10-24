#! /usr/bin/env python3
import json
import sys
from operator import add
from pathlib import Path
from typing import List

import functools

import plots
from config import Config
from ledger import Ledger, DataSet

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

team_names = {"X": team_x, "Y": team_y}


def parse_args() -> List[str]:
    args = sys.argv[1:]
    team_flags = {*team_names.keys()}
    return [*({*args} & team_flags)]


def date_filter_prompt():
    supplied_date = input("Please enter a date: MMDD\n")
    Config.date_filter = f"2021{supplied_date}"


def main(teams: List[str]) -> None:
    history = get_history()

    guild = Ledger(history)

    charts = construct_chart_list(guild, teams)

    prep_charts_dir()

    for chart in charts:
        chart.render()
        # chart.save_chart()


def construct_chart_list(guild, teams) -> List[plots.Chart]:
    """
    For the list of teams supplied, a list of charts to be saved is returned
    """
    datasets = [guild.get_main_spec_dataset(team_names[team]) for team in teams]
    color_sequences = [guild.sequence_role_colors(datasets[i], team_names[team]) for i, team in enumerate(teams)]

    args_list = [(color_sequences[i], datasets[i], team) for i, team in enumerate(teams)]

    charts = functools.reduce(add, [select_charts(*args) for args in args_list])
    return charts


def select_charts(color_sequence: List[str], dataset: DataSet, team_id: str) -> List[plots.Chart]:
    charts = {
        "bar": plots.BarChart(dataset, color_sequence),
        "pie": plots.PieChart(dataset, color_sequence),
        "hist": plots.Histogram(dataset),
        "combined": plots.CombinedPieBar(dataset, color_sequence, sys.argv[1])
    }
    charts = [charts[chart_name] for chart_name in Config.get_charts_to_render()]
    for chart in charts:
        chart.team_id = team_id
    return charts


def prep_charts_dir() -> None:
    """
    Sets up charts dir if it doesn't exist yet (if you change the default config)
    """
    Path(Config.charts_dir).mkdir(parents=True, exist_ok=True)


def get_history() -> List[dict]:
    with open(f"{Config.history_dir}/character-json.json") as fusion_history:
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
