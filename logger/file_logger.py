from config import Config
from table.table import Schema, Table
from rich.console import Console
from rich.table import Table as RichTable


class Logger:
    @classmethod
    def log_main_spec(cls, ledger, team_name: str) -> None:
        pass


class FilesystemLogger(Logger):
    @classmethod
    def log_main_spec(cls, ledger, team_name: str) -> None:
        """
        Writes a log to file with player & item names to accompany main spec loot charts.
        Uses custom table logic for formatting.
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


class TerminalLogger(Logger):
    @classmethod
    def log_main_spec(cls, ledger, team_name: str) -> None:
        """
        Prints a log to terminal with player & item names to accompany main spec loot charts.
        Uses RichTable for fancy formatting.
        """
        table = RichTable(title="Mainspec / Upgrade Loot Count")
        headings = ["Player Name", "Item Name", "Item Count"]
        col_colors = ["cyan", "magenta", "gold3"]
        for i, heading in enumerate(headings):
            table.add_column(heading, justify="center", style=col_colors[i])

        for player in ledger.teams[team_name]:
            table.show_lines = True
            for i, item in enumerate(player.main_spec_received):
                table.add_row(player.name, item.item_name, str(i + 1))

        console = Console()
        console.print(table)
