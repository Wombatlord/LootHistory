import json
from typing import List

import plots
from ledger import Ledger

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

with open("fusion-history.json") as fusion_history:
    history = json.load(fusion_history)

guild = Ledger(history)

team_y_dataset = guild.get_main_spec_dataset(team_y)
team_x_dataset = guild.get_main_spec_dataset(team_x)

charts: List[plots.Chart] = [
    plots.PieChart(team_y_dataset),
    plots.BarChart(team_y_dataset),
    plots.PieChart(team_x_dataset),
    plots.BarChart(team_x_dataset),
]

for chart in charts:
    chart.render()

print(guild.raiders)
print(guild.total_loot)
