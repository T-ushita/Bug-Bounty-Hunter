from utils.tinyfish_client import search_web
from rich import print

class TinyFishDiscoveryAgent:

    def __init__(self):
        self.name = "TinyFish Discovery Agent"

    def run(self, target):

        print(f"[bold cyan]Running {self.name}[/bold cyan]")
        print(f"Searching web for: {target}")

        results = search_web(target)

        urls = []

        for item in results.get("results", []):
            url = item.get("url")
            if url:
                urls.append(url)

        print(f"[green]Discovered {len(urls)} URLs[/green]")

        return {
            "target": target,
            "urls": urls
        }