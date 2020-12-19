"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    goal = random.randrange(0, 2)
    goals = []
    picked = []

    while len(goals) < num_goals:

        colour = random.choice(COLOUR_LIST)
        while colour in picked:
            colour = random.choice(COLOUR_LIST)
        picked.append(colour)

        if goal == 0:
            goals.append(PerimeterGoal(colour))
        else:
            goals.append(BlobGoal(colour))

    return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    unit_num = int(math.pow(2, (block.max_depth - block.level)))

    # if this block has no children (including unit cell case)
    if len(block.children) == 0:
        flattened = []

        for _ in range(unit_num):
            column = []
            for _ in range(unit_num):
                column.append(block.colour)
            flattened.append(column)

        return flattened

    else:
        # collect flattened children
        flat_child = []
        for child in block.children:
            flat_child.append(_flatten(child))

        # combine children in the upper block and lower block
        upper = []
        lower = []
        for i in range(len(flat_child[0])):
            upper.append(flat_child[1][i] + flat_child[2][i])
            lower.append(flat_child[0][i] + flat_child[3][i])

        flattened = upper + lower

        return flattened


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A player goal in the game of Blocky.

    This goal aims to put the most possible units of the target colour on the
    outermost edges.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        total = 0
        length = len(_flatten(board))
        edge = length - 1
        flat_board = _flatten(board)

        for j in [0, edge]:
            for i in range(length):
                if flat_board[i][j] == self.colour:
                    total += 1
                if flat_board[j][i] == self.colour:
                    total += 1

        return total

    def description(self) -> str:
        """Return a description of this goal.
        """
        return f'Aim to put the most possible units of ' \
               f'{colour_name(self.colour)} on the edges.'


class BlobGoal(Goal):
    """A player goal in the game of Blocky.

    This goal aims to achieve the biggest blob of the target colour.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        # create a flat board
        flat = _flatten(board)
        length = len(flat)

        # create a parallel visited board
        visited = []
        for _ in range(length):
            column = []
            for _ in range(length):
                column.append(-1)
            visited.append(column)

        # check on each unit cell on board and store their related blob size
        all_scores = []
        for i in range(length):
            for j in range(length):
                score = self._undiscovered_blob_size((i, j), flat, visited)
                all_scores.append(score)

        return max(all_scores)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        column = pos[0]
        row = pos[1]

        # if pos is negative or out of the board, do nothing
        if column < 0 or row < 0 or column >= len(board) or row >= len(board):
            return 0

        # if the colour does not match target colour, mark it
        if board[column][row] != self.colour:
            visited[column][row] = 0
            return 0

        # if the cell has been visited, do nothing
        if visited[column][row] != -1:
            return 0

        # this unit cell has been verified, mark it
        count = 1
        visited[column][row] = 1

        # visit its neighbours
        left_pos = (column - 1, row)
        right_pos = (column + 1, row)
        up_pos = (column, row + 1)
        down_pos = (column, row - 1)

        for position in [left_pos, right_pos, up_pos, down_pos]:
            count += self._undiscovered_blob_size(position, board, visited)

        return count

    def description(self) -> str:
        """Return a description of this goal.
        """
        return f'Aim for the largest blob of {colour_name(self.colour)}.'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
