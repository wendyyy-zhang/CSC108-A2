# The Blocky game

================ Program Implementation ================

Objectives:
- model hierarchical data using trees
- implement recursive operations on trees (both non-mutating and mutating)
- convert a tree into a flat, two-dimensional structure
- use inheritance to design classes according to a common interface

==================== GAME RULE ====================

Objective: Achieve the given goal with the highest score.
Suggested number of players: 1 to 4

Note:
- Each player has a different goal to work towards, which appears at the bottom of the pop-out window
- The score is shown after each move, is calculated based on two things:
	1) The move has been made:
     * Rotating, Swapping, and Passing cost 0 points.
     * Painting and Combining cost 1 point each time they are performed.
     * Smashing costs 3 points each time it is performed.
	2) How well has the goal has been achieved (determined by counting the number of the unit cells)

==================== GAME INFO ====================

Configuration of the game:
1. Maximum allowed depth: controls how finely subdivided the squares can be
2. Number and type of players: Any number of player of each type
3. Difficulty: the difficulty of a smart player
2. Number of moves: the number of moves each player can make

More details:
Support 3 types of players
1. human player: chooses moves based on user input
2. random player: chooses moves randomly
3. smart player: chooses moves that yields the best score

Provide 2 types of goals:
1. Blob goal: the player aims for the largest blob of a specific colour
2. Perimeter goal: the player aims to put the most possible units of a given colour on the edge of the board

NOTE: This is a school project, not entirely created by the author. Files that get implemented are: block.py, blocky.py, goal.py, player.py
