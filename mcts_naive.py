import argparse
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import logging
import math
import random
import simulation
from simulation import Action, Simulation

rng = random.Random()

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

LOG_LEVELS = (logging.WARNING, logging.INFO, logging.DEBUG, TRACE)

logger = logging.getLogger(__name__)


def configure_logging(verbosity: int) -> None:
    level = LOG_LEVELS[min(verbosity, len(LOG_LEVELS) - 1)]
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


@dataclass()
class Node:
    """A node of the MCTS tree"""
    parent: Optional[Node] = None
    children: Dict[Action, Node] = {}
    state: Optional[Simulation] = None
    n: int = 0
    q_sum: float = 0

    @staticmethod
    def _ucb(q: float, n: int, t: int) -> float:
        return q + math.sqrt(2) * math.log(t) / n

    def select(self) -> Tuple[Action, Node]:
        assert self.state is not None

        # Using 'R_' as an indicator of random - not a good practice, but
        # sample for now
        # If random, pick the option with the least visits
        if str(self.state.stage).startswith("R_"):
            sorted_by_n = sorted(self.children.items(), key=lambda item: item[1].n)
            return sorted_by_n[0]

        # Get UCB of each child
        # q_sum / n is to get the estimated value - the q
        sorted_by_ucb = sorted(self.children.items(), key=lambda item: self._ucb((item[1].q_sum / item[1].n), item[1].n, self.n))
        return sorted_by_ucb[-1]
        

    def expand(self, action: Action):
        assert self.parent is not None
        assert self.parent.state is not None
        self.state = self.parent.state.take_action(action)
        for action in self.state.possible_actions():
            self.children[action] = Node(self)

    def simulate(self) -> float:
        assert self.state is not None
        s = self.state
        while s.reward is None:
            choice = rng.choice(self.state.possible_actions())
            s = s.take_action(choice)

        logger.debug("Reward %s", s.reward)
        return s.reward

    def backprop(self, reward: float):
        self.n += 1
        self.q_sum += reward
        if self.parent:
            self.parent.backprop(reward)



def run_game(iterations: int):
    # Hacky (for now), but any R_ prefixed stage is random.
    # We're also hard picking a goal to start

    s = simulation.Simulation()
    s = s.take_action(rng.choice(s.possible_actions()))
    print(f"Goal is {s.goal}")

    root = Node(state = s)
    selected_action, selected_node = root.select()

    best_reward = float('-inf')

    for iteration in range(iterations):
        logger.info("Starting iteration %s", iteration)
        logger.info("---------------------")

        # No children means unexpanded
        while len(selected_node.children) == 0:
            selected_action, selected_node = selected_node.select()
            selected_node.expand(selected_action)
            if len(selected_node.children) == 0:
                # Terminal state
                # Using this method until 'proven' added
                assert selected_node.state is not None
                selected_node.backprop(selected_node.state.reward)
            reward = selected_node.simulate()
            if reward > best_reward:
                best_reward = reward
                logger.critical("Reward improved iteration %s: %s", iteration, best_reward)
            selected_node.children[0].backprop(reward)
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", "-i", default=1000)
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parsed = parser.parse_args()

    configure_logging(parsed.verbose)

    run_game(parsed.iterations)

    pass

if __name__ == "__main__":
    main()
