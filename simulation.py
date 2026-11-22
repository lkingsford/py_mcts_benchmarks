"""
Simulation for benchmarking MCTS implementations

We've got a basic implementation of a nasty version of the game show 'Countdown':
    - Get a random number between 1 and N0
    - Pick N1 numbers, pick large or small, given a number from the random pool
        - Large: 25, 50, 75, 100
        - Small: 1, 2, 3, 4, 5, 6, 7, 8, 9
    - After all numbers picked - attempt to get as close as possible to the goal
        - Can use each number up to once, either adding to, multiplying, dividing or subtracting from the previous number
        - Implemented as RPN with Stack, because game permits parentheses (and that seemed like a very easy way to emulate it)
    - Goal for the final number F to be as close as possible to the goal
    - Reward is N0 minus F
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
import random

MIN_GOAL = 101
MAX_GOAL = 1000
NUMBERS = 10

class Simulation:
    """ An instance of the simulation and its state """
    
    class Stage(Enum):
        GET_GOAL = auto()
        PICKING_SIZES = auto()
        CHOOSE_OPERATION = auto()

    class NumberSize(Enum):
        SMALL = auto()
        LARGE = auto()

    class Operation(Enum):
        ADD = auto()
        SUBTRACT = auto()
        DIVIDE = auto()
        MULTIPLY = auto()
        DONE = auto()
    
    @dataclass(frozen=True)
    class GetGoalAction():
        goal_number: int

    @dataclass(frozen=True)
    class PickSize():
        size: Simulation.NumberSize

    @dataclass(frozen=True)
    class PickOperation():
        operation: Simulation.Operation

    @dataclass(frozen=True)
    class PickNumber():
        number: int

    type Action = GetGoalAction | PickSize | PickOperation | PickNumber

    def __init__(self) -> None:
        self.stage = Simulation.Stage.GET_GOAL
        self.available_numbers: List[int] = []
        self.stack: List[int] = []

    def take_action(self) -> Simulation:
        raise NotImplementedError()

    def possible_actions(self) -> List[Simulation.Action]:
        match self.stage:
            case self.Stage.GET_GOAL:
                return [self.GetGoalAction(goal) for goal in range(MIN_GOAL, MAX_GOAL)]
            case self.Stage.PICKING_SIZES:
                return [self.PickSize(self.NumberSize.SMALL), self.PickSize(self.NumberSize.LARGE)]
            case self.Stage.CHOOSE_OPERATION:
                operations: List[Simulation.Action] = []
                if len(self.stack) >= 2:
                    operations.extend([self.PickOperation(self.Operation.ADD), self.PickOperation(self.Operation.MULTIPLY)])
                    # No negatives
                    if self.stack[0] > self.stack[1]:
                        operations.append(self.PickOperation(self.Operation.SUBTRACT))
                    # Whole numbers only
                    if self.stack[0] % self.stack[1] == 0:
                        operations.append(self.PickOperation(self.Operation.DIVIDE))
                if len(self.available_numbers) > 0:
                        operations.extend([self.PickNumber(number) for number in self.available_numbers])
                if len(self.stack) == 1:
                    operations.append(self.PickOperation(self.Operation.DONE))
                return operations


    def terminal(self) -> Optional[float]:
        # Returns None if still going, float if there's a reward
        raise NotImplementedError()


