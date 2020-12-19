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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    id_ = 0
    players = []

    for i in range(num_human + num_random):
        goal = generate_goals(1)[0]
        if i < num_human:
            players.append(HumanPlayer(id_, goal))
        else:
            players.append(RandomPlayer(id_, goal))
        id_ += 1

    for num in smart_players:
        goal = generate_goals(1)[0]
        players.append(SmartPlayer(id_, goal, num))
        id_ += 1

    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    # if have reached a block that has no children
    if len(block.children) == 0 or block.level == level:
        return block

    # else, locate the <location> in one of the four children
    x = location[0]
    y = location[1]
    half_x = block.position[0] + block.size / 2
    half_y = block.position[1] + block.size / 2

    # in child 3, (half_size, half_size), the lower right corner
    if x >= half_x and y >= half_y:
        return _get_block(block.children[3], location, level)

    # in child 0, (half_size, 0), the upper right corner
    elif x >= half_x:
        return _get_block(block.children[0], location, level)

    # in child 2, (0, half_size), the lower left corner
    elif y >= half_y:
        return _get_block(block.children[2], location, level)

    # in child 1, (0, 0), the upper left corner
    else:
        return _get_block(block.children[1], location, level)


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A random player who makes random but valid moves except for pass.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this RandomPlayer with the given <player_id> and <goal>.
        """
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """No block is selected by the player, return None.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        # collect a list of actions applicable
        actions = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, SWAP_HORIZONTAL,
                   SWAP_VERTICAL, SMASH, COMBINE, PAINT]

        if not self._proceed:
            return None  # Do not remove

        # randomly generate a block
        copy = board.create_copy()

        unit_length = int(2 ** board.max_depth)
        column = random.randrange(unit_length)
        row = random.randrange(unit_length)
        level = random.randrange(board.max_depth + 1)  # level <= max_depth

        picked = _get_block(copy, (column, row), level)  # block from copy
        block = _get_block(board, (column, row), level)  # block from the board

        # randomly generate moves and apply to the block until find one fits
        action = random.choice(actions)
        while not _move(picked, action):
            action = random.choice(actions)

        self._proceed = False  # Must set to False before returning!
        return _create_move(action, block)


class SmartPlayer(Player):
    """A smart player who always makes the best move (move with highest score).
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _difficulty:
    #   Indicating how difficult it is to play against this player.
    #
    # == Representation Invariants concerning the private attributes ==
    #    _difficulty > 0
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this SmartPlayer with the given <player_id> and <goal>.
        """
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """No block is selected by the player, return None.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        scores = {}
        for _ in range(self._difficulty):
            copy = board.create_copy()
            helper = RandomPlayer(0, self.goal)

            # use the random player to generate a valid move
            helper._proceed = True
            move = helper.generate_move(copy)  # (action, block from copy)

            # make the move on the copy
            _move(move[-1], move[:-1])

            # record the score of the copy
            score = self.goal.score(copy)

            # collect all scores into a dictionary
            scores[score] = move  # (action, block from copy)

        # find the highest score that is generated among all valid moves
        highest = max(scores)

        self._proceed = False  # before return

        # compare it to the current score of the current board
        # if it is better with no move made, pass
        if highest < self.goal.score(board):
            return None

        # if the move increase the score, prepare to make the move
        # find the block on board corresponding to the one from copy
        copied_block = scores[highest][-1]
        location = copied_block.position
        level = copied_block.level
        block = _get_block(board, location, level)

        return _create_move(scores[highest][:-1], block)


def _move(block: Block, action: Tuple[str, Optional[int]]) -> bool:
    """Try to make the given <action> on the given <block>, return True if and
    only if the action is successful applied.

    >>> block = Block((0, 0), 100, None, 0, 2)
    >>> child_pos = block._children_positions()
    >>> for i in range(4):
    ...     child = Block(child_pos[i], 50, colour_list[i], 1, 2)
    ...     block.children.append(child)

    >>> _move(block.children[2], SMASH)
    True
    >>> _move(block.children[2], ROTATE_CLOCKWISE)
    True
    >>> _move(block, COMBINE)
    False
    """
    colour_list = [(1, 128, 181), (199, 44, 58), (138, 151, 71), (255, 211, 92)]

    if action[0] == 'rotate':
        is_valid = block.rotate(action[1])
    elif action[0] == 'swap':
        is_valid = block.swap(action[1])
    elif action[0] == 'smash':
        is_valid = block.smash()
    elif action[0] == 'combine':
        is_valid = block.combine()
    else:
        is_valid = block.paint(random.choice(colour_list))
    return is_valid


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
