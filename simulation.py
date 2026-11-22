"""
Simulation for benchmarking MCTS implementations

We've got a basic implementation of a nasty version of the game show 'Countdown':
- Get a random number between MIN_GOAL and MAX_GOAL
- Pick NUMBERS numbers, pick large or small, given a number from the random pool
  - Large: 25, 50, 75, 100
  - Small: 1, 2, 3, 4, 5, 6, 7, 8, 9
- After all numbers picked - attempt to get as close as possible to the goal
  - Can use each number up to once, either adding to, multiplying, dividing or subtracting
  - Implemented as standard RPN with Stack (e.g., pushing 10 then 3 then SUBTRACT yields 10 - 3 = 7)
- Goal for the final number F to be as close as possible to the goal
- Reward is MAX_GOAL minus abs(goal minus F)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
import copy

MIN_GOAL = 101
MAX_GOAL = 1000
NUMBERS = 10


class Simulation:
    """An instance of the simulation and its state"""

    class Stage(Enum):
        R_GET_GOAL = auto()
        PICKING_SIZES = auto()
        R_PICK_NUMBER = auto()  # Random based on picked size
        CHOOSE_OPERATION = auto()
        TERMINAL = auto()

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
    class GetGoalAction:
        goal_number: int

    @dataclass(frozen=True)
    class PickSize:
        size: Simulation.NumberSize

    @dataclass(frozen=True)
    class DrawNumber:
        number: int

    @dataclass(frozen=True)
    class PickOperation:
        operation: Simulation.Operation

    @dataclass(frozen=True)
    class PickNumber:
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
        Take an action and return the next state.

        No rules enforcement; handled in possible_actions.
        """
        new_instance = copy.copy(self)

        match action:
            case self.GetGoalAction(number):
                new_instance.goal = number
                new_instance.stage = self.Stage.PICKING_SIZES

            case self.PickSize(size):
                new_instance.last_size = size
                new_instance.stage = self.Stage.R_PICK_NUMBER

            case self.DrawNumber(number):
                available_numbers = self.available_numbers.copy()
                available_numbers.append(number)
                new_instance.available_numbers = available_numbers
                new_instance.last_size = None

                if len(available_numbers) < NUMBERS:
                    new_instance.stage = self.Stage.PICKING_SIZES
                else:
                    new_instance.stage = self.Stage.CHOOSE_OPERATION

            case self.PickOperation(operation):
                stack = self.stack.copy()
                new_instance.stack = stack

                match operation:
                    case self.Operation.DONE:
                        assert self.goal is not None
                        new_instance.reward = MAX_GOAL - abs(self.goal - stack.pop())
                        new_instance.stage = self.Stage.TERMINAL

                    case _:
                        # Standard RPN: 'right' is top of stack (pushed last), 'left' is pushed earlier
                        right = stack.pop()
                        left = stack.pop()

                        match operation:
                            case self.Operation.ADD:
                                stack.append(left + right)
                            case self.Operation.SUBTRACT:
                                stack.append(left - right)
                            case self.Operation.MULTIPLY:
                                stack.append(left * right)
                            case self.Operation.DIVIDE:
                                stack.append(left // right)

            case self.PickNumber(number):
                stack = self.stack.copy()
                available_numbers = self.available_numbers.copy()
                available_numbers.remove(number)
                stack.append(number)

                new_instance.stack = stack
                new_instance.available_numbers = available_numbers

        return new_instance

    def possible_actions(self) -> List[Simulation.Action]:
        """All the possible actions the player may make at this time"""
        match self.stage:
            case self.Stage.R_GET_GOAL:
                # Note: range is exclusive of the upper bound, so MAX_GOAL + 1 includes MAX_GOAL
                return [self.GetGoalAction(goal) for goal in range(MIN_GOAL, MAX_GOAL + 1)]

            case self.Stage.PICKING_SIZES:
                return [
                    self.PickSize(self.NumberSize.SMALL),
                    self.PickSize(self.NumberSize.LARGE),
                ]

            case self.Stage.R_PICK_NUMBER:
                if self.last_size == self.NumberSize.SMALL:
                    return [self.DrawNumber(number) for number in range(1, 10)]
                return [self.DrawNumber(number) for number in (25, 50, 75, 100)]

            case self.Stage.CHOOSE_OPERATION:
                operations: List[Simulation.Action] = []

                if len(self.stack) >= 2:
                    left, right = self.stack[-2], self.stack[-1]
                    operations.extend([
                        self.PickOperation(self.Operation.ADD),
                        self.PickOperation(self.Operation.MULTIPLY),
                    ])
                    # No negatives or zero (keeps stack strictly positive)
                    if left > right:
                        operations.append(self.PickOperation(self.Operation.SUBTRACT))
                    # Whole numbers only
                    if left % right == 0:
                        operations.append(self.PickOperation(self.Operation.DIVIDE))

                if self.available_numbers:
                    operations.extend(
                        self.PickNumber(number) for number in self.available_numbers
                    )

                if len(self.stack) == 1:
                    operations.append(self.PickOperation(self.Operation.DONE))

                return operations

            case self.Stage.TERMINAL:
                return []
