from typing import List, Tuple, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np

from config import Config
from styles import choose_style, choose_bar_style, Style

DataPoints = List[Tuple[str, int]]
DataSeries = Tuple[List[str], List[int]]


# noinspection PyTypeChecker
class Chart:
    _team_id: str
    data: DataPoints

    fonts: Dict[str, str] = {
        "monospace": "monospace",
        "roboto": "Roboto Mono Medium for Powerline",
        "inconsolata": "Inconsolata NF"
    }

    def normalise_dataset(self) -> DataSeries:
        series: DataSeries = tuple([point[i] for point in self.data] for i in (0, 1))
        return series

    def populate_chart(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def render(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def save_chart(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def apply_style(self, text_color, label_color, edge_color, title_color, font) -> None:
        plt.rcdefaults()
        plt.rcParams.update(
            {
                'text.color': text_color,
                'axes.labelcolor': label_color,
                'axes.edgecolor': edge_color,
                'axes.titlecolor': title_color,
                'font.family': font,
                'font.size': 12
            }
        )

    def apply_bar_style(self, figure, axes, title, xlabel, tick_colors, face_color) -> None:
        axes.set_title(title)
        axes.set_xlabel(xlabel)
        axes.tick_params(axis='y', colors=tick_colors)
        axes.tick_params(axis='x', colors=tick_colors)
        axes.invert_yaxis()  # labels read top-to-bottom
        axes.set_facecolor(face_color)
        figure.patch.set_facecolor(face_color)

    @property
    def team_id(self) -> str:
        return self._team_id

    @team_id.setter
    def team_id(self, val: str) -> None:
        self._team_id = val


class PieChart(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str]):
        self.data = data
        self.role_colors = role_colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        self.apply_style(*choose_style(Config.style_choice))

        fig, ax = plt.subplots(tight_layout=True)
        fig.suptitle("Mainspec Loot Share", color=Style.colors["goldenrod"])

        ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            pctdistance=0.8,
            colors=self.role_colors
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        fig.patch.set_facecolor(Style.colors["almost_black"])

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self):
        self.populate_chart()
        plt.savefig(f"{Config.charts_dir}/{self.team_id}-loot-pie.png")


class BarChart(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str]):
        self.data = data
        self.role_colors = role_colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        self.apply_style(
            *choose_style(Config.style_choice)
        )

        fig, ax = plt.subplots(tight_layout=True)
        y_pos = np.arange(len(labels))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.barh(y_pos, values, align='center', color=self.role_colors)

        self.apply_bar_style(
            **choose_bar_style(Config.style_choice)
        )

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self) -> None:
        self.populate_chart()
        plt.savefig(f"{Config.charts_dir}/{self.team_id}-loot-bars")


class CombinedPieBar(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str]):
        self.data = data
        self.role_colors = role_colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        y_pos = np.arange(len(labels))
        px = 1 / plt.rcParams['figure.dpi']

        self.apply_style(
            *choose_style(Config.style_choice)
        )

        fig, (bar, pie) = plt.subplots(1, 2, tight_layout=True, figsize=(1600 * px, 800 * px))
        fig.suptitle(f"Fusion: Team {self.team_id} Mainspec Loot Share", color=Style.colors["goldenrod"])

        bar.barh(y_pos, values, align='center', color=self.role_colors)
        bar.set_yticks(y_pos)
        bar.set_yticklabels(labels)

        self.apply_bar_style(
            figure=fig,
            axes=bar,
            **choose_bar_style(Config.style_choice)
        )

        pie.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            pctdistance=0.8,
            colors=self.role_colors
        )
        pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self) -> None:
        self.populate_chart()
        plt.savefig(f"{Config.charts_dir}/{self.team_id}-bar-and-pie")


class Histogram(Chart):
    def __init__(self, data: DataPoints):
        self.data = data

    def populate_chart(self) -> None:
        values = self.normalise_dataset()[1]
        n_bins = max(values) + 1

        self.apply_style(
            *choose_style(Config.style_choice)
        )

        fig, ax = plt.subplots()

        ax.set_xlabel("Total Loot Awarded")
        ax.set_ylabel("Raiders")
        ax.tick_params(axis='y', colors=Style.colors["goldenrod"])
        ax.tick_params(axis='x', colors=Style.colors["goldenrod"])
        ax.set_facecolor(Style.colors["almost_black"])
        fig.patch.set_facecolor(Style.colors["almost_black"])
        ax.set_title("Loot Histogram")
        ax.hist(values, bins=n_bins, align="mid")

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self) -> None:
        self.populate_chart()
        plt.savefig(f"{Config.charts_dir}/{self.team_id}-histogram")
