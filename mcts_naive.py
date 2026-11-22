import argparse
from dataclasses import dataclass
from typing import Optional, Dict
import random
import simulation
from simulation import Action, Simulation

rng = random.Random()

@dataclass()
class Node:
    """A node of the MCTS tree"""
    parent: Optional[Node] = None
    children: Dict[Action, Node] = {}
    state: Optional[Simulation] = None
    n: int = 0
    q: int = 0

    def select(self) -> Node:
        raise NotImplementedError()

    def expand(self):
        assert self.state is not None
        for action in self.state.possible_actions():
            self.children[action] = Node(self)

    def simulate(self):
        s = simulation.Simulation()
        s = s.take_action(rng.choice(s.possible_actions()))
        print(f"Goal is {s.goal}")

        while s.reward is None:
            choice = rng.choice(s.possible_actions())
            print(choice)
            s=s.take_action(choice)
        
        print(s.reward)


def run_game(iterations: int):
    # Hacky (for now), but any R_ prefixed stage is random.
    # We're also hard picking a goal to start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", "-i", default=1000)
    parsed = parser.parse_args()

    run_game(parsed.iterations)

    pass

if __name__ == "__main__":
    main()
