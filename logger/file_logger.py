from config import Config
from table.table import Schema, Table


class Logger:
    @classmethod
    def log_main_spec(cls, ledger, team_name: str) -> None:
        pass


class FilesystemLogger(Logger):
    @classmethod
    def log_main_spec(cls, ledger, team_name: str) -> None:
        """
        Writes a log with player & item names to accompany main spec loot charts.
        """
        schema = Schema(["Player Name", "Item Name", "Item Count"])
        table: Table = schema.new_table()
        table.hline()
        for player in ledger.teams[team_name]:
            for i, item in enumerate(player.main_spec_received):
                table.add_row(player.name, item.item_name, i + 1)
            table.hline()

        log = table.format(headings=True)
        with open(f"{Config.logs_dir}/{team_name}-chart-log.txt", "w") as logfile:
            logfile.write(log)
