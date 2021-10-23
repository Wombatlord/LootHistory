from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import numpy as np

DataPoints = List[Tuple[str, int]]
DataSeries = Tuple[List[str], List[int]]


# noinspection PyTypeChecker
class Chart:
    data: DataPoints
    chart_colors: Dict[str, str] = {"goldenrod": "xkcd:goldenrod",
                                    "ocean": "xkcd:ocean",
                                    "almost_black": "xkcd:almost black"}

    fonts: Dict[str, str] = {"monospace": "monospace",
                             "roboto": "Roboto Mono Medium for Powerline",
                             "inconsolata": "Inconsolata NF"}

    def normalise_dataset(self) -> DataSeries:
        series: DataSeries = tuple([point[i] for point in self.data] for i in (0, 1))
        return series

    def populate_chart(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def render(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def save_chart(self, team_name: str) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def apply_style(self, text_color, label_color, edge_color, title_color, font) -> None:
        plt.rcdefaults()
        plt.rcParams.update({'text.color': text_color,
                             'axes.labelcolor': label_color,
                             'axes.edgecolor': edge_color,
                             'axes.titlecolor': title_color,
                             'font.family': font,
                             'font.size': 12})

    def apply_bar_style(self, figure, axes, title, xlabel, tick_colors, face_color) -> None:
        axes.set_title(title)
        axes.set_xlabel(xlabel)
        axes.tick_params(axis='y', colors=tick_colors)
        axes.tick_params(axis='x', colors=tick_colors)
        axes.invert_yaxis()  # labels read top-to-bottom
        axes.set_facecolor(face_color)
        figure.patch.set_facecolor(face_color)
        pass


class PieChart(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str]):
        self.data = data
        self.role_colors = role_colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        self.apply_style(self.chart_colors["ocean"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.fonts["inconsolata"])

        fig, ax = plt.subplots(tight_layout=True)
        fig.suptitle("Mainspec Loot Share", color=self.chart_colors["goldenrod"])
        ax.pie(values, labels=labels, autopct='%1.1f%%', pctdistance=0.8, colors=self.role_colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        fig.patch.set_facecolor(self.chart_colors["almost_black"])

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str):
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-loot-pie.png")


class BarChart(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str]):
        self.data = data
        self.role_colors = role_colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        self.apply_style(self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["ocean"],
                         self.chart_colors["goldenrod"],
                         self.fonts["inconsolata"])

        fig, ax = plt.subplots(tight_layout=True)
        y_pos = np.arange(len(labels))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.barh(y_pos, values, align='center', color=self.role_colors)

        self.apply_bar_style(figure=fig,
                             axes=ax,
                             title="Fusion: Team Y Loot Assignment Totals",
                             xlabel="Mainspec BIS / Upgrade pieces awarded",
                             tick_colors=self.chart_colors["goldenrod"],
                             face_color=self.chart_colors["almost_black"])

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str) -> None:
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-loot-bars")


class CombinedPieBar(Chart):
    def __init__(self, data: DataPoints, role_colors: List[str], main_title: str):
        self.data = data
        self.role_colors = role_colors
        self.main_title = main_title

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        y_pos = np.arange(len(labels))
        px = 1 / plt.rcParams['figure.dpi']

        self.apply_style(self.chart_colors["ocean"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["ocean"],
                         self.chart_colors["goldenrod"],
                         self.fonts["inconsolata"])

        fig, (bar, pie) = plt.subplots(1, 2, tight_layout=True, figsize=(1600 * px, 800 * px))
        fig.suptitle(f"Fusion: Team {self.main_title} Mainspec Loot Share", color=self.chart_colors["goldenrod"])

        bar.barh(y_pos, values, align='center', color=self.role_colors)
        bar.set_yticks(y_pos)
        bar.set_yticklabels(labels)

        self.apply_bar_style(figure=fig,
                             axes=bar,
                             title="Loot Assignment Totals",
                             xlabel="Mainspec BIS / Upgrade pieces awarded",
                             tick_colors=self.chart_colors["goldenrod"],
                             face_color=self.chart_colors["almost_black"])

        pie.pie(values, labels=labels, autopct='%1.1f%%', pctdistance=0.8, colors=self.role_colors)
        pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str) -> None:
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-bar-and-pie")


class Histogram(Chart):
    def __init__(self, data: DataPoints):
        self.data = data

    def populate_chart(self) -> None:
        values = self.normalise_dataset()[1]
        n_bins = max(values) + 1

        self.apply_style(self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.chart_colors["goldenrod"],
                         self.fonts["inconsolata"])

        fig, ax = plt.subplots()

        ax.set_xlabel("Total Loot Awarded")
        ax.set_ylabel("Raiders")
        ax.tick_params(axis='y', colors=self.chart_colors["goldenrod"])
        ax.tick_params(axis='x', colors=self.chart_colors["goldenrod"])
        ax.set_facecolor(self.chart_colors["almost_black"])
        fig.patch.set_facecolor(self.chart_colors["almost_black"])
        ax.set_title("Loot Histogram")
        ax.hist(values, bins=n_bins, align="mid")

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str) -> None:
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-histogram")
