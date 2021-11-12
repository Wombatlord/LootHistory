#! /usr/bin/env python
import functools
import json
import os
import sys
from operator import add
from pathlib import Path
from subprocess import call
from typing import List
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import track

import plots
from config import Config
from ledger import Ledger, DataSet
from logger.file_logger import FilesystemLogger, TerminalLogger
from styles import Style

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

team_names = {"X": team_x, "Y": team_y}


def parse_args() -> List[str]:
    args = sys.argv[1:]
    team_flags = {*team_names.keys()}
    return [*({*args} & team_flags)]


def date_filter_prompt():
    date_prompt = "[bold pale_green3]Please enter a date:[/bold pale_green3]"
    month_pair = "[bold gold3]MM[/bold gold3]"
    day_pair = "[bold cyan]DD[/bold cyan]"

    rprint(f"{date_prompt} {month_pair}{day_pair}")

    supplied_date = input()
    rprint()
    Config.date_filter = f"2021{supplied_date}"


def style_choice_prompt():
    style_prompt = "[bold pale_green3]Please choose a style:[/bold pale_green3]"
    chosen_style = Prompt.ask(f"{style_prompt}", choices=["default"], default="default")

    if chosen_style not in Style.styles:
        chosen_style = "default"

    Config.style_choice = chosen_style
    rprint(f"[bold pale_green3]Chosen style:[/bold pale_green3] [bold gold3]{Config.style_choice.capitalize()}[/bold gold3]\n")


def log_prompt():
    display_and_save = Confirm.ask("[bold pale_green3]Would you like to display and save a log?[/bold pale_green3]")
    rprint()
    return display_and_save


def write_chart_log(guild, teams):
    for team in teams:
        FilesystemLogger.log_main_spec(guild, team_names[team])


def terminal_log_main_spec(guild, teams):
    for team in teams:
        TerminalLogger.log_main_spec(guild, team_names[team])


def loot_received_dates(guild, teams):
    for team in teams:
        # rprint(guild.unique_dates_to_dict(team_names[team]))
        # rprint(guild.loot_per_raid(team_names[team]))
        rprint([guild.loot_over_time(team_names[team]) for team in teams])


def clear_terminal():
    _ = call('clear' if os.name == 'posix' else 'cls')


def construct_chart_list(guild, teams) -> List[plots.Chart]:
    """
    For the list of teams supplied, a list of charts to be saved is returned
    """
    datasets = [guild.get_main_spec_dataset(team_names[team]) for team in teams]
    color_sequences = [guild.sequence_role_colors(datasets[i], team_names[team]) for i, team in enumerate(teams)]

    accumulated_loot_data = [guild.loot_over_time(team_names[team]) for team in teams]

    args_list = [(color_sequences[i], datasets[i], accumulated_loot_data[i], team) for i, team in enumerate(teams)]

    charts = functools.reduce(add, [select_charts(*args) for args in args_list])
    return charts


def select_charts(color_sequence: List[str], dataset: DataSet, accumulated_loot_data, team_id: str) -> List[plots.Chart]:
    charts = {
        "bar": plots.BarChart(dataset, color_sequence),
        "pie": plots.PieChart(dataset, color_sequence),
        "hist": plots.Histogram(dataset),
        "over-time": plots.LootOverTime(accumulated_loot_data),
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

    clear_terminal()
    date_filter_prompt()
    style_choice_prompt()

    history = get_history()
    guild = Ledger(history)

    charts = construct_chart_list(guild, teams)

    if log_prompt():
        clear_terminal()
        terminal_log_main_spec(guild, teams)
        write_chart_log(guild, teams)

    for chart in charts:  # track(charts, description="[bold gold3]Processing...[/bold gold3]"):
        # chart.render()
        chart.save_chart()

    # loot_received_dates(guild, teams)


# console = Console()

chosen_team = parse_args()
main(chosen_team)
