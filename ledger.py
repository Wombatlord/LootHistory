from __future__ import annotations

import functools
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

DataSet = List[Tuple[str, int]]


@dataclass
class ReceivedItem:
    item_id: int
    item_name: str
    is_offspec: bool
    officer_note: str
    raw_data: dict

    @classmethod
    def parse(cls, data: dict) -> ReceivedItem:
        kwargs = {
            "item_id": data["item_id"],
            "item_name": data["name"],
            "is_offspec": data["pivot"]["is_offspec"],
            "officer_note": data["pivot"]["officer_note"] or "",
            "raw_data": data
        }
        return cls(**kwargs)

    @property
    def is_pattern_or_plan(self) -> bool:
        return "Pattern" in self.item_name or "Plan" in self.item_name

    @property
    def is_mainspec(self) -> bool:
        return "Mainspec BIS" in self.officer_note or "Best in Slot" in self.officer_note

    @property
    def is_upgrade(self) -> bool:
        return "Upgrade" in self.officer_note

    @property
    def is_banked(self) -> bool:
        return "Banking" in self.officer_note

    @property
    def is_pvp(self) -> bool:
        return "PvP" in self.officer_note or "OSPvP" in self.officer_note

    @property
    def is_other(self) -> bool:
        return "Other" in self.officer_note

    @property
    def is_excluded(self) -> bool:
        exclusions = ["Banking",
                      "PvP",
                      "OS",
                      "OSPvP",
                      "Other"]

        return any(exclusion in self.officer_note for exclusion in exclusions)


@dataclass
class Player:
    raw_data: dict
    name: str
    id: int
    raid_group_name: str

    @classmethod
    def parse(cls, data: dict) -> Player:
        kwargs = {
            key: data[key] for key in ["name", "id", "raid_group_name"]
        }
        kwargs["raw_data"] = data
        return cls(**kwargs)

    @property
    def received(self) -> List[ReceivedItem]:
        return [ReceivedItem.parse(item_data) for item_data in self.raw_data["received"]]

    @property
    def main_spec_received(self) -> List[ReceivedItem]:
        return [
            item for item in self.received
            if not item.is_excluded
        ]


class Team(str):
    def __contains__(self, item) -> bool:
        contains = False
        if isinstance(item, Player):
            contains = self == item.raid_group_name

        return contains


@dataclass
class HistoryData:
    players: List[Player]

    @classmethod
    def parse(cls, data: List[Dict]) -> HistoryData:
        kwargs = {
            'players': [Player.parse(datum) for datum in data]
        }
        return cls(**kwargs)


class Ledger:
    team: Dict[str, List[Player]] = {"members": []}
    loot_mapping: Dict[str, int]

    def __init__(self, history: List[dict]) -> None:
        self.history: HistoryData = HistoryData.parse(history)
        self.teams = {}
        self.split_teams()

    def split_teams(self) -> None:
        team_names = {player.raid_group_name for player in self.history.players}
        for name in team_names:
            self._split_team(name)

    def _split_team(self, team_name: str) -> None:
        for player in self.history.players:
            if player not in Team(team_name):
                continue

            self.teams[team_name] = [*self.teams.get(team_name, []), player]

    @property
    def loot_allocation_all(self) -> Dict[str, int]:
        return {
            team_name: {member.name: len(member.received) for member in members}
            for team_name, members in self.teams.items()
        }

    @property
    def loot_allocation_main_spec(self) -> Dict[str, int]:
        return {
            team_name: {member.name: len(member.main_spec_received) for member in members}
            for team_name, members in self.teams.items()
        }

    @functools.lru_cache(maxsize=2)
    def get_main_spec_dataset(self, team_name: str) -> DataSet:
        points = sorted(
            self.loot_allocation_main_spec.get(team_name, {}).items(),
            key=lambda item: item[1],
            reverse=True,
        )
        return points
