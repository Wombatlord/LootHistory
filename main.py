import json
from plots import loot_pie, loot_bars
from ledger import Ledger

team_x = "Team X - Rainbow"
team_y = "Team Y - nicorn"

with open("fusion-history.json") as fusion_history:
    history = json.load(fusion_history)

guild = Ledger(history)

guild.split_teams(history, team_y)
guild.name_list()
guild.loot_count_no_os()

loot_pie(guild.total_loot, guild.raiders)

loot_bars(guild.total_loot, guild.raiders)

print(guild.raiders)
print(guild.total_loot)
