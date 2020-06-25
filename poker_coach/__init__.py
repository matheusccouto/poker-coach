# TODO Create round generator
# TODO Create hand visualizer
# TODO Improve evaluation speed

from typing import Sequence, Dict

import numpy as np

import poker
from poker import holdem
from poker_coach import equity

MIN_BB: int = 1
MAX_BB: int = 15


class Scenario:
    """ Training scenario. """

    def __init__(
        self, n_seats: int = 9, avg: float = 20, std: float = 20, times: int = 1000
    ):
        self._n_seats = n_seats
        self._times = times
        self._game = holdem.Poker(n_seats=self.n_seats)
        self._deck = poker.Deck()

        hero_chips = np.random.randint(MIN_BB, MAX_BB)
        hero = poker.Player("Hero", chips=hero_chips)
        self._game.add_player(hero, seat=0)

        self._villain_range_dict = dict()
        for i in range(1, n_seats):
            villain_chips = np.random.randint(MIN_BB, MAX_BB)
            villain = poker.Player(name=str(i), chips=villain_chips)
            self._game.add_player(villain, seat=i)
            villain_range = np.random.normal(loc=avg, scale=std, size=1)
            villain_range = np.clip(villain_range, 0, 100)
            self._villain_range_dict.update({i: float(villain_range)})

        self._game.dealer = np.random.randint(0, n_seats)
        hero.add_cards([self._deck.draw() for _ in range(2)])

    @property
    def times(self) -> int:
        """ Get number of times to run Monte Carlo procedure. """
        return self._times

    @property
    def n_seats(self) -> int:
        """ Get number of seats on the table. """
        return self._n_seats

    @property
    def seats(self) -> Sequence[poker.Player]:
        """ Get the seats (and consequently players). """
        return self._game.seats

    @property
    def hero_hand(self) -> poker.Hand:
        """ Get hero hand. """
        return self.seats[0].hand

    @property
    def hero_hand_descr(self) -> str:
        """ Get hero hand description. """
        hand = self.seats[0].hand
        return "".join([rank + suit for rank, suit in zip(hand.ranks, hand.suits)])

    @property
    def villain_range(self) -> Dict[int, float]:
        """ Get villain ranges. """
        return self._villain_range_dict

    # TODO Calculate chances against a single caller
    def eval_ranges(self, n_callers: int = 1):
        """ Evaluate hands and ranges chances of winning. """
        hero = [self.hero_hand_descr]
        # TODO Filter villains after
        villains = np.array(self.villain_range.values())
        # TODO Calculate compound range
        eq = equity.equity(np.concatenate([hero, villains]), self.times)


    # TODO Calculate chances of stealing blinds
