from utils.tinyfish_client import search_web
from rich import print


class TinyFishDiscoveryAgent:

    def __init__(self):
        self.name = "TinyFish Discovery Agent"

    def run(self, target):

        print(f"[bold cyan]Running {self.name}[/bold cyan]")

        results = search_web(
            url="https://google.com",
            goal=f"Find websites related to {target}",
        )

        print("[green]Discovered websites:[/green]")

        for site in results.get("websites", []):
            print(site["url"])

        return results