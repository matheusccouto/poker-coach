from typing import Iterator
from typing import Sequence, Optional, Tuple

import numpy as np

import bluff
from bluff.holdem import equity


def flatten(i: Iterator) -> Iterator:
    """ Flatten an irregular iterable. """
    for i in i:
        if isinstance(i, Iterator):
            yield from i
        else:
            yield i


class Scenario:
    """ General training scenario. """

    MIN_BB: int = 1
    MAX_BB: int = 20

    MIN_ACTION: float = 5
    MAX_ACTION: float = 100

    def __init__(
        self,
        n_seats: int = 9,
        field: Tuple[float, float, float] = (5, 20, 50),
        ante: float = 12.5,
        random_state: Optional[int] = None,
    ):
        """
        Args:
            n_seats: Number of players in the table.
            field: Tuple with min, mode and max field action.
            ante: Ante size (big blind percentage).
            random_state: Random State.
        """
        self._n_seats = n_seats
        self._ante = ante
        self._deck = bluff.Deck(random_state)

        r = np.random.RandomState(random_state)

        # Add hero.
        self._hero_chips = r.randint(self.MIN_BB, self.MAX_BB)
        self._hero_hand = "".join([str(self._deck.draw()) for _ in range(2)])
        self._hero_position = r.randint(0, n_seats - 1)

        # Add villains.
        self._villains_range = r.triangular(
            left=field[0], mode=field[1], right=field[2], size=n_seats - 1
        )

        self._villains_range = np.clip(
            self._villains_range, self.MIN_ACTION, self.MAX_ACTION
        )

        self._villains_chips = r.randint(self.MIN_BB, self.MAX_BB, n_seats - 1)

    @property
    def n_seats(self) -> int:
        """ Get number of seats on the table. """
        return self._n_seats

    @property
    def hero_chips(self) -> int:
        """ Get hero chips amount. """
        return self._hero_chips

    @property
    def villains_chips(self) -> np.ndarray:
        """ Get hero chips amount. """
        return np.array(self._villains_chips)

    @property
    def hero_hand(self) -> str:
        """ Get hero hand. """
        return self._hero_hand

    @property
    def hero_index(self) -> int:
        """ Get hero index. """
        return self._hero_position - self._n_seats

    @property
    def hero_position(self) -> str:
        """ Get hero position name. """
        return self.position_to_abbreviation(self.hero_index, self.n_seats)

    @property
    def villains_range(self) -> np.ndarray:
        """ Get villain ranges. """
        return np.array(self._villains_range)

    @property
    def villains_before_range(self) -> np.ndarray:
        """ Get ranges from villains before the hero. """
        return np.array(self.villains_range[: self._hero_position])

    @property
    def villains_after_range(self) -> np.ndarray:
        """ Get ranges from villains after the hero. """
        return np.array(self.villains_range[self._hero_position :])

    @property
    def villains_before_position(self) -> Sequence[str]:
        """ Get position name from villains before the hero. """
        return np.array(
            [
                self.position_to_abbreviation(i, self.n_seats)
                for i in range(-len(self.villains_range), self.hero_index)
            ]
        )

    @property
    def villains_after_position(self) -> Sequence[str]:
        """ Get position name from villains after the hero. """
        return np.array(
            [
                self.position_to_abbreviation(i, self.n_seats)
                for i in range(self.hero_index + 1, 0)
            ]
        )

    @property
    def villains_before_chips(self) -> np.ndarray:
        """ Get ranges from villains before the hero. """
        return np.array(self.villains_chips[: self._hero_position])

    @property
    def villains_after_chips(self) -> np.ndarray:
        """ Get ranges from villains after the hero. """
        return np.array(self.villains_chips[self._hero_position :])

    @property
    def ante(self) -> float:
        """ Get ante size (big blind percentage)."""
        return self._ante

    @property
    def pot(self) -> float:
        """ Get pot size (in big blinds). """
        return 1.5 + self.n_seats * self.ante / 100

    @staticmethod
    def position_to_abbreviation(position: int, n_seats: int) -> str:
        names = {
            -1: "BB",
            -2: "SB",
            -3: "BTN",
            -4: "CO",
            -5: "HJ",
            -6: "LJ",
        }
        if position in names:
            return names[position]
        elif n_seats + position == 0:
            return "UTG"
        else:
            return f"UTG+{n_seats + position}"

    @staticmethod
    def eval_ranges(
        hero_hand: str, villains_range: Sequence[float], times: int = 10000
    ) -> np.ndarray:
        """ Evaluate chances of hero winning against each villain range. """
        return np.array(
            [
                equity.equity([hero_hand, villain], times=times)[0]
                for villain in villains_range
            ]
        )

    @staticmethod
    def expected_value(chances, success, failure):
        """
        Expected value.

        Args:
            chances: Chances of winning.
            success: Success return value.
            failure: failure return value.

        Returns:
            Expected value.
        """
        return chances * success + (1 - chances) * failure

    def strategies_expected_value(self, chances, win_action, lose_action, no_action):
        """
        Calculate expected value for each strategy.

        Args:
            chances: Chances of winning.
            win_action: Return value when winning the action.
            lose_action: Return value when losing the action.
            no_action: Return value when avoiding the action.

        Returns:
            Tuple with expected value for action and no action
        """
        action_ev = self.expected_value(chances, win_action, lose_action)
        return action_ev, no_action


class PushFoldScenario(Scenario):
    """ Push fold training scenario. """

    MIN_ACTION: float = 3
    MAX_ACTION: float = 100

    # Override abstract class args names with more descriptive ones.
    def __init__(
        self,
        n_seats: int = 9,
        field: Tuple[float, float, float] = 10,
        ante: float = 12.5,
        random_state: Optional[int] = None,
    ):
        """
        Args:
            n_seats: Number of players in the table.
            field: Tuple with min, mode and max field action.
            ante: Ante size (big blind percentage).
            random_state: Random state.
        """
        super().__init__(
            n_seats=n_seats, field=field, ante=ante, random_state=random_state,
        )
