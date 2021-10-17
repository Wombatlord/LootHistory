from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

DataPoints = List[Tuple[str, int]]
DataSeries = Tuple[List[str], List[int]]


# noinspection PyTypeChecker
class Chart:
    data: DataPoints

    def normalise_dataset(self) -> DataSeries:
        series: DataSeries = tuple([point[i] for point in self.data] for i in (0, 1))
        return series

    def populate_chart(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def render(self) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")

    def save_chart(self, team_name: str) -> None:
        raise NotImplementedError("Do not invoke the interface directly!")


class PieChart(Chart):
    def __init__(self, data: DataPoints):
        self.data = data

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        fig1, ax1 = plt.subplots(tight_layout=True)
        ax1.pie(values, labels=labels, autopct='%1.1f%%', pctdistance=0.8)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str):
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-loot-pie.png")


class BarChart(Chart):
    def __init__(self, data: DataPoints, colors: List[str]):
        self.data = data
        self.colors = colors

    def populate_chart(self) -> None:
        labels, values = self.normalise_dataset()
        plt.rcdefaults()
        fig, ax = plt.subplots(tight_layout=True)

        y_pos = np.arange(len(labels))

        ax.barh(y_pos, values, align='center', color=self.colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Loot')
        ax.set_title('Loot Assignment Totals')
        ax.set_facecolor('grey')
        fig.patch.set_facecolor('grey')

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str) -> None:
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-loot-bars")


class Histogram(Chart):
    def __init__(self, data: DataPoints):
        self.data = data

    def populate_chart(self) -> None:
        values = self.normalise_dataset()[1]
        print(values)
        fig, ax = plt.subplots()
        ax.set_title("Loot Histogram")
        ax.set_xlabel("Total Loot Awarded")
        ax.set_ylabel("Raiders")
        ax.hist(values, bins=9, align="mid")

    def render(self) -> None:
        self.populate_chart()
        plt.show()

    def save_chart(self, team_name: str) -> None:
        self.populate_chart()
        plt.savefig(f"charts/{team_name}-histogram")
