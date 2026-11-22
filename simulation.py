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
    - Reward is N0 minus abs(goal minus F)
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
import copy

MIN_GOAL = 101
MAX_GOAL = 1000
NUMBERS = 10

class Simulation:
    """ An instance of the simulation and its state """
    
    class Stage(Enum):
        R_GET_GOAL = auto()
        PICKING_SIZES = auto()
        R_PICK_NUMBER = auto() # Random based on picked size
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
    class DrawNumber():
        number: int

    @dataclass(frozen=True)
    class PickOperation():
        operation: Simulation.Operation

    @dataclass(frozen=True)
    class PickNumber():
        number: int

    type Action = GetGoalAction | PickSize | DrawNumber | PickOperation | PickNumber

    def __init__(self) -> None:
        self.stage = Simulation.Stage.R_GET_GOAL
        self.available_numbers: List[int] = []
        self.stack: List[int] = []
        self.reward: Optional[float] = None
        self.goal: Optional[int] = None
        self.last_size: Optional[Simulation.NumberSize] = None

    def take_action(self, action: Simulation.Action) -> Simulation:
        """
        Take an action

        No rules enforcement; handled in possible_actions
        """

        new_instance = copy.copy(self)

        # Minimizing memory (a little) by copying every variable not modified
        match action:
            case self.GetGoalAction(number):
                new_instance.goal = number

            case self.PickSize(size):
                new_instance.last_size = size
                new_instance.stage = Simulation.Stage.R_PICK_NUMBER

            case self.DrawNumber(number):   
                available_numbers = copy.deepcopy(self.available_numbers)
                available_numbers.append(number)
                new_instance.available_numbers = available_numbers
                if len(available_numbers) < NUMBERS:
                    new_instance.stage = self.Stage.PICKING_SIZES
                else:
                    new_instance.stage = self.Stage.CHOOSE_OPERATION
                return new_instance

            case self.PickOperation(operation):
                stack = copy.deepcopy(self.stack)
                new_instance.stack = stack
                a = stack.pop(0)
                b = stack.pop(0)
                match operation:
                    case self.Operation.ADD:
                        stack.insert(0, a + b)
                    case self.Operation.SUBTRACT:
                        stack.insert(0, a - b)
                    case self.Operation.MULTIPLY:
                        stack.insert(0, a * b)
                    case self.Operation.DIVIDE:
                        stack.insert(0, int(a / b))
                    case self.Operation.DONE:
                        assert self.goal is not None
                        new_instance.reward = MAX_GOAL - abs(self.goal - stack.pop(0))

            case self.PickNumber(number):
                stack = copy.deepcopy(self.stack)
                available_numbers = copy.deepcopy(self.available_numbers)
                available_numbers.append(number)
                available_numbers.remove(number)
                stack.insert(0, number)
                new_instance.stack = stack
                new_instance.available_numbers = available_numbers


        return new_instance
                


    def possible_actions(self) -> List[Simulation.Action]:
        """All the possible actions the player may make at this time"""
        match self.stage:
            case self.Stage.R_GET_GOAL:
                return [self.GetGoalAction(goal) for goal in range(MIN_GOAL, MAX_GOAL)]

            case self.Stage.PICKING_SIZES:
                return [self.PickSize(self.NumberSize.SMALL), self.PickSize(self.NumberSize.LARGE)]

            case self.Stage.R_PICK_NUMBER:
                if self.last_size == self.NumberSize.SMALL:
                    self.last_size = None
                    return [self.DrawNumber(number) for number in range(1,10)]
                else:
                    self.last_size = None
                    return [self.DrawNumber(number) for number in [25, 50, 75, 100]]

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




