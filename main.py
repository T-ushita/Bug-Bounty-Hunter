from agents.tinyfish_discovery_agent import TinyFishDiscoveryAgent


def main():

    agent = TinyFishDiscoveryAgent()

    result = agent.run("test websites with login forms")

    print(result)


if __name__ == "__main__":
    main()