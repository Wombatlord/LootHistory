from typing import Dict, List


class Ledger:
    team: Dict = {"member": []}
    raiders: List = []
    total_loot: List = []

    def __init__(self, history: Dict) -> None:
        self.history: Dict = history

    def split_teams(self, history: Dict, team_name: str) -> None:
        index = 0
        for entry in history:
            if history[index]["raid_group_name"] == team_name:
                self.team["member"].append(entry)
            index += 1

    def name_list(self) -> None:
        member_index = 0
        for entry in self.team["member"]:
            self.raiders.append(self.team["member"][member_index]["name"])
            member_index += 1

    def loot_count(self) -> None:
        loot_total = 0
        member_index = 0
        for entry in self.team["member"]:
            for item in self.team["member"][member_index]["received"]:
                loot_total += 1
            self.total_loot.append(loot_total)
            loot_total = 0
            member_index += 1

    def loot_count_no_os(self) -> None:
        loot_total = 0
        item_counter = 0
        member_index = 0
        for entry in self.team["member"]:
            for item in self.team["member"][member_index]["received"]:
                if self.team["member"][member_index]["received"][item_counter]["pivot"]["is_offspec"] == 0:
                    loot_total += 1
                if self.team["member"][member_index]["received"][item_counter]["pivot"][
                    "officer_note"] == "Votes: 0 \"Banking\"":
                    loot_total -= 1
                item_counter += 1
            self.total_loot.append(loot_total)
            loot_total = 0
            item_counter = 0
            member_index += 1
