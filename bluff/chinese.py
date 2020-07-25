""" Abstract chinese bluff module. """
from typing import Dict

import bluff


class Hand(bluff.Hand):
    """ Abstract chinese bluff hand class"""

    _ROYALTIES_DICT: Dict[float, int] = {}

    @property
    def royalties(self) -> int:
        """ Get hand royalties. """
        for value, points in sorted(self._ROYALTIES_DICT.items(), reverse=True):
            if self.value > value:
                return points
        return 0


class TopHand(Hand):
    """ Chinese bluff top hand"""

    _ROYALTIES_DICT: Dict[float, int] = {
        int("6" + "0" * 5, 16): 1,
        int("7" + "0" * 5, 16): 2,
        int("8" + "0" * 5, 16): 3,
        int("9" + "0" * 5, 16): 4,
        int("A" + "0" * 5, 16): 5,
        int("B" + "0" * 5, 16): 6,
        int("C" + "0" * 5, 16): 7,
        int("D" + "0" * 5, 16): 8,
        int("E" + "0" * 5, 16): 9,
        int("2" + "0" * 8, 16): 10,
        int("3" + "0" * 8, 16): 11,
        int("4" + "0" * 8, 16): 12,
        int("5" + "0" * 8, 16): 13,
        int("6" + "0" * 8, 16): 14,
        int("7" + "0" * 8, 16): 15,
        int("8" + "0" * 8, 16): 16,
        int("9" + "0" * 8, 16): 17,
        int("A" + "0" * 8, 16): 18,
        int("B" + "0" * 8, 16): 19,
        int("C" + "0" * 8, 16): 20,
        int("D" + "0" * 8, 16): 21,
        int("E" + "0" * 8, 16): 22,
    }


class MiddleHand(Hand):
    """ Chinese bluff top hand"""

    _ROYALTIES_DICT: Dict[float, int] = {
        int("2" + "0" * 8, 16): 2,
        int("2" + "0" * 9, 16): 4,
        int("2" + "0" * 10, 16): 8,
        int("2" + "0" * 11, 16): 12,
        int("2" + "0" * 13, 16): 20,
        int("2" + "0" * 14, 16): 30,
        int("E" + "0" * 14, 16): 50,
    }


class BottomHand(Hand):
    """ Chinese bluff top hand"""

    _ROYALTIES_DICT: Dict[int, int] = {
        int("2" + "0" * 9, 16): 2,
        int("2" + "0" * 10, 16): 4,
        int("2" + "0" * 11, 16): 6,
        int("2" + "0" * 13, 16): 10,
        int("2" + "0" * 14, 16): 15,
        int("E" + "0" * 14, 16): 25,
    }


class Player(bluff.Player):
    """ Chinese bluff player. """

    def __init__(self, name: str, points: int):
        super().__init__(name=name, chips=points)
        self._top_hand: Hand = TopHand()
        self._middle_hand: Hand = MiddleHand()
        self._bottom_hand: Hand = BottomHand()

    @property
    def top_hand(self) -> Hand:
        """ Get or set top hand. """
        return self._top_hand

    @top_hand.setter
    def top_hand(self, value: Hand):
        self._top_hand = value

    @property
    def middle_hand(self) -> Hand:
        """ Get or set middle hand. """
        return self._middle_hand

    @middle_hand.setter
    def middle_hand(self, value: Hand):
        self._middle_hand = value

    @property
    def bottom_hand(self) -> Hand:
        """ Get or set bottom hand. """
        return self._bottom_hand

    @bottom_hand.setter
    def bottom_hand(self, value: Hand):
        self._bottom_hand = value

    def place_card(self, card: bluff.Card, hand: str):
        """ Place a card in one of the three chinese bluff hands. """
        if "top" in hand.lower():
            self.top_hand.add(card)
        elif "mid" in hand.lower():
            self.middle_hand.add(card)
        elif "bot" in hand.lower():
            self.bottom_hand.add(card)
        else:
            raise ValueError(f"{hand} is not a valid hand.")


class Poker(bluff.Poker):
    """ Chinese Poker. """

    _N_STARTING_CARDS: int = 13
