"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random



class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


"""
This is the baseline scoring function and is copied from sample_players.py since the project
submission fails if we try to import it from sample_players.py. We will be using this function
as part of our own custom scoring functions
"""
def improved_score(game, player):
    """The "Improved" evaluation function discussed in lecture that outputs a
    score equal to the difference in the number of moves available to the
    two players.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns
    ----------
    float
        The heuristic value of the current game state
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves)


"""
We now define a few custom heuristics. Note: We have given them more descriptive
names and have defined the project-required custom_score etc at the end
"""

def cover_opponent_moves(game, player):
    """The idea here is to use the number of common moves between the player
    and the opponent as the score. This is an indication of how well a player
    controls the board wrt the opponent

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    return float(len(set(own_moves).intersection(opp_moves)))


def look_ahead_by_one(game, player):
    """The idea here to take all possible moves from the current position and then
    evaluate how good each of them is (using improved_score) and then sum up
    the scores to get the total score. As an additional tweak, we ignore losing positions

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = game.get_legal_moves(player)
    score = 0.0
    for move in own_moves:
        forecast_game = game.forecast_move(move)
        s = improved_score(forecast_game, player)
        if s == float('inf'):
            return s
        elif s != -float('inf'):
            score += s

    return score

def select_one_of(game, player):
    """The idea here is to use one of look_ahead_by_one, cover_opponent_moves and improved_score
    depending on how many moves have elapsed in the game

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    free_squares = len(game.get_blank_spaces())
    if free_squares <= 15:
        return look_ahead_by_one(game, player)
    elif free_squares <= 20:
        return cover_opponent_moves(game, player)
    else:
        return improved_score(game, player)


def aggregate_heuristics(game, player):
    """The idea here is to use multiple individual heuristics aggregate their scores

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    enumerate"""

    def is_inf(score):
        return score == float('inf') or -float('inf')

    total_score = 0.0
    for heuristic in [improved_score, cover_opponent_moves, look_ahead_by_one]:
        score = heuristic(game, player)
        if is_inf(score):
            return score
        total_score += score

    return total_score

"""
Define some functions required by the project submission
"""

def custom_score(game,player) :
    return aggregate_heuristics(game,player)

def custom_score_2(game,player):
    return cover_opponent_moves(game, player)

def custom_score_3(game, player):
    return look_ahead_by_one(game,player)

def custom_score_4(game, player):
    return select_one_of(game, player)



class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        def terminal_state(game) :
            return not bool(game.get_legal_moves())

        def min_val(game,depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            if terminal_state(game):
                return float('+inf')
            if depth == 0:
                return self.score(game, game.inactive_player)

            return min([max_val(game.forecast_move(move), depth-1) for move in game.get_legal_moves()])

        def max_val(game,depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            if terminal_state(game):
                return float('-inf')
            if depth == 0:
                return self.score(game, game.active_player)

            return max([min_val(game.forecast_move(move), depth-1) for move in game.get_legal_moves()])

        best_move = (-1,-1)
        moves = game.get_legal_moves()
        val = float("-inf")
        for move in moves:
            v = min_val(game.forecast_move(move), depth-1)
            if v > val:
                val = v
                best_move = move

        return best_move

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        best_move = (-1, -1)
        self.time_left = time_left
        depth = 1
        try:
            while True:
                best_move = self.alphabeta(game,depth)
                depth += 1
        except SearchTimeout :
            return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        def terminal_state(game):
            return not bool(game.get_legal_moves())

        def max_val(game, depth, alpha, beta) :

            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            if terminal_state(game):
                return float('-inf')
            if depth == 0:
                return self.score(game, game.active_player)

            val = float('-inf')
            for next_move in game.get_legal_moves():
                val = max(val, min_val(game.forecast_move(next_move), depth-1, alpha, beta))
                if val >= beta:
                    return val
                alpha = max(val, alpha)

            return val

        def min_val(game,depth,alpha,beta) :

            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            if terminal_state(game):
                return float('+inf')
            if depth == 0:
                return self.score(game, game.inactive_player)

            val = float('+inf')
            for move in game.get_legal_moves():
                val = min(val, max_val(game.forecast_move(move), depth-1, alpha, beta))
                if val <= alpha:
                    return val
                beta = min(val, beta)

            return val

        best_move = (-1, -1)
        val = float('-inf')
        for move in game.get_legal_moves():
            new_game = game.forecast_move(move)
            v = min_val(new_game, depth-1, alpha, beta)
            if v > val:
                val = v
                best_move = move
            alpha = max(alpha,v)

        return best_move


