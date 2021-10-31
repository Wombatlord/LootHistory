#! /usr/bin/env python
import json
import sys
from operator import add
from pathlib import Path
from typing import List

import functools

import plots
from config import Config
from ledger import Ledger, DataSet
from logger.file_logger import FilesystemLogger
from styles import Style

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


def style_choice_prompt():
    chosen_style = input("Please choose a style:\n")

    if chosen_style not in Style.styles:
        chosen_style = "default"

    Config.style_choice = chosen_style
    print(f"Chosen style: {Config.style_choice.capitalize()}")


def write_chart_log(guild, teams):
    for team in teams:
        FilesystemLogger.log_main_spec(guild, team_names[team])


def print_loot_over_time(guild, teams):
    for team in teams:
        guild.loot_over_time(team_names[team])


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
        "combined": plots.CombinedPieBar(dataset, color_sequence)
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


def prep_logs_dir() -> None:
    """
    Sets up logs dir if it doesn't exist yet (if you change the default config)
    """
    Path(Config.logs_dir).mkdir(parents=True, exist_ok=True)


def get_history() -> List[dict]:
    with open(f"{Config.history_dir}/character-json.json") as fusion_history:
        history = json.load(fusion_history)
    return history


def main(teams: List[str]) -> None:
    prep_charts_dir()
    prep_logs_dir()

    history = get_history()
    guild = Ledger(history)

    # charts = construct_chart_list(guild, teams)
    # write_chart_log(guild, teams)
    print_loot_over_time(guild, teams)

    # for chart in charts:
    #     # chart.render()
    #     chart.save_chart()


chosen_team = parse_args()
date_filter_prompt()
style_choice_prompt()
main(chosen_team)
