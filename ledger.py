from __future__ import annotations

import functools
import itertools
import operator
from typing import Dict, List, Tuple, Set, Generator
from dataclasses import dataclass
from rich import print as rprint

from config import Config
from styles import Style

DataSet = List[Tuple[str, int]]


@dataclass
class ReceivedItem:
    item_id: int
    item_name: str
    is_offspec: bool
    officer_note: str
    received_at: str
    instance_id: int
    raw_data: dict

    @classmethod
    def parse(cls, data: dict) -> ReceivedItem:
        kwargs = {
            "item_id": data["item_id"],
            "item_name": data["name"],
            "is_offspec": data["pivot"]["is_offspec"],
            "officer_note": data["pivot"]["officer_note"] or "",
            "received_at": data["pivot"]["received_at"],
            "instance_id": data["instance_id"],
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
        exclusions = Config.excluded_officer_note

        return any(exclusion in self.officer_note for exclusion in exclusions)

    @property
    def from_excluded_raid(self) -> bool:
        """
        Add any of the following ID's to exclude that raid from data.

        Gruul = 10
        Mag = 11
        SSC = 12
        TK = 14
        """
        instances: List[int] = [10, 11]

        return any(instance is self.instance_id for instance in instances)

    @property
    def date_received(self):
        if self.received_at:
            date_time_split = self.received_at.split(" ")
            return date_time_split[0]

    def received_after(self, date: str) -> bool:
        if self.received_at:
            date_time_split = self.received_at.split(" ")
            year_month_day = date_time_split[0].split("-")
            item_received_date = functools.reduce(operator.add, year_month_day)

            if date <= item_received_date:
                return True


@dataclass
class Player:
    raw_data: dict
    name: str
    id: int
    raid_group_name: str
    role: str
    role_color: str

    @classmethod
    def parse(cls, data: dict) -> Player:
        kwargs = {
            "raw_data": data,
            "name": data["name"],
            "id": data["id"],
            "raid_group_name": data["raid_group_name"],
            "role": data["class"],
            "role_color": None
        }

        return cls(**kwargs)

    @property
    def received(self) -> List[ReceivedItem]:
        return [ReceivedItem.parse(item_data) for item_data in self.raw_data["received"]]

    @property
    def main_spec_received(self) -> List[ReceivedItem]:
        return [
            item for item in self.received
            if not item.is_excluded and item.received_after(
                Config.date_filter) and not item.from_excluded_raid and not item.is_pattern_or_plan
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
    def __init__(self, history: List[dict]) -> None:
        self.history: HistoryData = HistoryData.parse(history)
        self.teams = {}
        self.assign_role_colors()
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

    def assign_role_colors(self) -> None:
        for player in self.history.players:
            if player.role in Style.role_colors[Config.style_choice]:
                player.role_color = Style.role_colors[Config.style_choice][player.role]

    def sequence_role_colors(self, dataset: DataSet, team_name: str) -> List[str]:
        return functools.reduce(
            operator.add,
            [
                [player.role_color for player in self.teams[team_name] if entry[0] == player.name]
                for entry in dataset
            ]
        )

    def get_unique_dates(self, team_name) -> Set[str]:
        return set(
            functools.reduce(
                operator.add,
                [
                    [item.date_received for item in player.main_spec_received]
                    for player in self.teams[team_name]
                ]
            )
        )

    def _unique_dates_to_dict(self, team_name) -> Dict[str, int]:
        return {date: 0 for date in sorted(self.get_unique_dates(team_name))}

    def loot_per_raid(self, team_name) -> List[Dict[str, Dict[str, int]]]:
        player_dates_loot_totals = []

        for player in self.teams[team_name]:
            loot_dates = {player.name: self._unique_dates_to_dict(team_name)}

            for item in player.main_spec_received:
                if item.date_received in loot_dates[player.name]:
                    loot_dates[player.name][item.date_received] += 1

            player_dates_loot_totals.append(loot_dates)

        return player_dates_loot_totals

    def _accumulate_loot_totals(self, team_name) -> Generator[List[int]]:
        player_dates_loot_totals = self.loot_per_raid(team_name)

        for player in player_dates_loot_totals:
            for loot_dates in player:
                loot_per_date = list(player[loot_dates].values())
                total_over_time = list(itertools.accumulate(loot_per_date))
                yield total_over_time

    def _accumulated_with_dates(self, team_name) -> Generator[Dict[str, int]]:
        player_dates_loot = self.loot_per_raid(team_name)
        totals = self._accumulate_loot_totals(team_name)

        for player in player_dates_loot:
            for loot_dates in player:
                dates = list(player[loot_dates].keys())
                for total in totals:
                    yield dict(zip(dates, total))

    def loot_over_time(self, team_name) -> Dict[str, Dict[str, int]]:
        accumulated_loot = self._accumulated_with_dates(team_name)

        return {player.name: next(accumulated_loot) for player in self.teams[team_name]}

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
