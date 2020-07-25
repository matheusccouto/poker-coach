""" An abstract Poker module. """

import itertools
import random
import re
from typing import Union, List, Iterable, Sequence, Optional, Dict

import more_itertools
import numpy as np


class NotEnoughCardsError(Exception):
    """ Raise when the deck runs out of cards. """


class SeatOccupiedError(Exception):
    """ Raise when trying to put a player in an already occupied seat. """


class Card:
    """ French-style deck card."""

    def __init__(self, abbreviation: str):
        self._rank = self._abbreviation_to_rank(abbreviation)
        self._suit = self._abbreviation_to_suit(abbreviation)
        self._numerical_rank = self._rank_to_numerical(self._rank)

    def __repr__(self):
        return self.rank + self.suit

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    @property
    def rank(self) -> str:
        """ Get the card rank. """
        return self._rank

    @property
    def suit(self) -> str:
        """ Get the card suit. """
        return self._suit

    @property
    def numerical_rank(self) -> int:
        """ Get the card numerical rank. """
        return self._numerical_rank

    @property
    def hex_rank(self) -> str:
        """ Get the card alpha numerical rank (hexadecimal) """
        return np.base_repr(self.numerical_rank, 16)

    @staticmethod
    def _abbreviation_to_rank(card_abbreviation: str) -> str:
        """ Get the rank from the card abbreviation. """
        rank = card_abbreviation[0].upper()
        valid = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        if rank not in valid:
            raise ValueError(f"'{card_abbreviation}' is not a valid card abbreviation.")
        return rank

    @staticmethod
    def _abbreviation_to_suit(card_abbreviation: str) -> str:
        """ Get the suit from the card abbreviation. """
        suit = card_abbreviation[-1].lower()
        valid = ["s", "h", "c", "d"]
        if suit not in valid:
            raise ValueError(f"'{card_abbreviation}' is not a valid card abbreviation.")
        return suit

    @staticmethod
    def _rank_to_numerical(rank: str) -> int:
        """ Get the numerical rank from an alpha-numerical rank. """
        numbers = {"T": "10", "J": "11", "Q": "12", "K": "13", "A": "14"}
        if rank in numbers:
            for key, value in numbers.items():
                if key in rank:
                    rank = rank.replace(key, value)
        return int(rank)


class Deck:
    """ French-style deck. """

    ranks: Sequence[str] = [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "T",
        "J",
        "Q",
        "K",
        "A",
    ]
    suits: Sequence[str] = ["s", "h", "c", "d"]

    def __init__(self, random_state=None):
        self._cards: List[Card] = []
        self.set_and_shuffle(random_state)

    def __len__(self):
        return len(self._cards)

    def __iter__(self):
        return self._cards

    @property
    def cards(self):
        """ Get deck cards. """
        return self._cards

    def set_and_shuffle(self, random_state=None):
        """ Set the deck cards and shuffle. """
        self._cards = [
            Card(rank + suit)
            for rank, suit in itertools.product(self.ranks, self.suits)
        ]
        r = np.random.RandomState(random_state)
        r.shuffle(self._cards)

    def draw(self) -> Card:
        """ Draw a card. """
        try:
            return self._cards.pop(-1)
        except IndexError:
            raise NotEnoughCardsError("There are no cards left in the deck.")


class Hand:
    """ Poker hand. Formed by Card objects. """

    def __init__(self, *args: Union[Card, str]):
        self._ranks: List[str] = []
        self._suits: List[str] = []
        self._numerical_ranks: List[int] = []
        self._hex_ranks: List[str] = []
        self._cards: List[Card] = []

        self.add(*args)

    def __repr__(self):
        return " ".join(sorted([str(card) for card in self.cards]))

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]

    def __setitem__(self, key, value: Card):
        self._cards[key] = value
        self._ranks[key] = value.rank
        self._suits[key] = value.suit
        self._numerical_ranks[key] = value.numerical_rank
        self._hex_ranks[key] = value.hex_rank

    def __delitem__(self, key):
        self.cards.pop(key)
        self.ranks.pop(key)
        self.suits.pop(key)
        self.numerical_ranks.pop(key)
        self.hex_ranks.pop(key)

    def __contains__(self, item):
        return item in self._cards

    @property
    def ranks(self) -> List[str]:
        """ Get hand ranks. """
        return self._ranks

    @property
    def suits(self) -> List[str]:
        """ Get hand suits. """
        return self._suits

    @property
    def numerical_ranks(self) -> List[int]:
        """ Get hand numerical ranks. """
        return self._numerical_ranks

    @property
    def hex_ranks(self) -> List[str]:
        """ Get hand alpha-numerical ranks (hexadecimal). """
        return self._hex_ranks

    @property
    def cards(self) -> List[Card]:
        """ Get hand cards. """
        return self._cards

    @property
    def value(self) -> int:
        """
        Get the numerical value of the hand. The bigger the value, the better the hand.
        """
        value = ""

        value = self._high_card() + value
        value = self._pair() + value
        value = self._two_pairs() + value
        value = self._three_of_a_kind() + value
        value = self._straight() + value
        value = self._flush() + value
        value = self._full_house() + value
        value = self._four_of_a_kind() + value
        value = self._straight_flush() + value

        value = self._compensate_missing_cards_value(len(self), value)
        value = self._compensate_extra_cards_value(len(self), value)

        return int(value, 16)

    @property
    def name(self) -> str:
        """ Get ranking name of the hand. """

        names = [
            "high_card",
            "pair",
            "two_pairs",
            "three_of_a_kind",
            "straight",
            "flush",
            "full_house",
            "four_of_a_kind",
            "straight_flush",
            "royal_straight_flush",
        ]
        for name in names:
            if getattr(self, f"is_{name}")():
                return name
        raise ValueError("Hand has unexpected value.")

    def _args_to_cards(self, *args: Union[Card, str]) -> List[Card]:
        """ Parse class arguments to Cards instances. """
        # Separate args if the user used a concatenated argument.
        cards = self._separate_concatenated_cards(*args)
        # Create cards instances if the user used string arguments.
        return [Card(card) if isinstance(card, str) else card for card in cards]

    def _separate_concatenated_cards(self, *args: Union[Card, str]) -> Iterable[str]:
        """ Separate concatenated cards repr in a argument. """
        nested = [
            re.findall(r"[2-9TJQKA][shcd]", card) if isinstance(card, str) else card
            for card in args
        ]
        flat = self._flatten(nested)
        return flat

    @staticmethod
    def _flatten(i: Iterable) -> Iterable:
        """ Flatten an irregular iterable. """
        for val in i:
            # pylint: disable=W1116
            if isinstance(val, Iterable):
                yield from val
            else:
                yield val

    def add(self, *args: Union[Card, str]):
        """ Add cards to the hands. """
        cards = self._args_to_cards(*args)
        self._ranks += [card.rank for card in cards]
        self._suits += [card.suit for card in cards]
        self._numerical_ranks += [card.numerical_rank for card in cards]
        self._hex_ranks += [
            np.base_repr(card.numerical_rank, 16)
            if card.numerical_rank > 9
            else card.rank
            for card in cards
        ]
        self._cards += cards

    @staticmethod
    def _find_repeated_ranks(ranks: Sequence, reps: int) -> set:
        """ Find ranks that are repeated a certain number of times in a hand. """
        return {rank for rank in ranks if ranks.count(rank) == reps}

    # The next methods are useful for the value property only. They
    # work by transforming a hand in a huge integer number. The bigger
    # the number, the stronger the hand. Bellow the construction of this
    # number is better explained.

    # Each pair of letter bellow represent a numerical rank. For
    # example: 02 stands for the deuce, while 11 stands for the Jack.

    # In order to have only 1-dig numbers I'll work with hexadecimal.

    # Every type of hand takes its magnitude multiplied for the
    # numerical rank. The integer formation is bellow.
    # ABCCDEFGGHIIIII
    # A - Straight Flush
    # B - Quads
    # C - Full House
    # D - Flush
    # E - Straight
    # F - Trips
    # G - Two Pair
    # H - Pair
    # I - High Card (Actually, the rank of every card)

    # In a nutshell, the next methods return a code used to form the
    # hand value. This is also where all the logic for deciding the hand
    # level lies.

    def _high_card(self) -> str:
        """ Hand value code for a high card."""
        # Concatenate each cards value in a string, from the biggest to
        # the smallest.
        return "".join(sorted(self.hex_ranks, reverse=True))

    def _pair(self) -> str:
        """ Hand value code for a pair."""
        pairs = list(self._find_repeated_ranks(self.hex_ranks, 2))
        if len(pairs) == 1:
            return pairs[0]
        return "0"

    def _two_pairs(self) -> str:
        """ Hand value code for a two pair."""
        pairs = list(self._find_repeated_ranks(self.hex_ranks, 2))
        if len(pairs) == 2:
            return max(pairs) + min(pairs)
        return "00"

    def _three_of_a_kind(self) -> str:
        """ Hand value code for a three of a kind."""
        trips = list(self._find_repeated_ranks(self.hex_ranks, 3))
        if trips:
            return trips[0]
        return "0"

    def _straight(self) -> str:
        """ Hand value code for a straight."""
        # Work with base 10 numbers because more_itertools.consecutive_groups do work
        # with hexadecimals.
        aces_count = self.numerical_ranks.count(14)
        hand = set(self.numerical_ranks + [1] * aces_count)

        # This next comparisons only work when the Hand is not empty.
        # When the list is empty, it should return no value.
        if not hand:
            return "0"

        groups = [list(group) for group in more_itertools.consecutive_groups(hand)]
        longest_sequence = max([group[-1] - group[0] for group in groups]) + 1

        if longest_sequence >= 5:
            largest_value = max([max(group) for group in groups if len(group) >= 5])
            return np.base_repr(largest_value, 16)  # Convert to hex.
        return "0"

    def _flush(self) -> str:
        """ Hand value code for a flush."""
        suits = {suit for suit in self.suits if self.suits.count(suit) > 5}
        if len(suits) == 0:
            return "0"
        ranks = [r for r, s in zip(self.numerical_ranks, self.suits) if s in suits]
        return np.base_repr(max(ranks), 16)

    def _full_house(self) -> str:
        """ Hand value code for a full house."""
        trips = list(self._find_repeated_ranks(self.hex_ranks, 3))
        pair = list(self._find_repeated_ranks(self.hex_ranks, 2))
        if trips and pair:
            return trips[0] + pair[0]
        return "00"

    def _four_of_a_kind(self) -> str:
        """ Hand value code for a four of a kind."""
        quads = list(self._find_repeated_ranks(self.hex_ranks, 4))
        if quads:
            return quads[0]
        return "0"

    def _straight_flush(self) -> str:
        """ Hand value code for a straight flush."""
        flush = self._flush()
        if flush == "0":
            return "0"
        straight = self._straight()
        if straight == "0":
            return "0"
        return straight

    @staticmethod
    def _compensate_missing_cards_value(n_cards: int, value: str) -> str:
        """ Add trailing zeros to the value in order to compensate missing cards. """
        if n_cards < 5:
            missing = 5 - n_cards
            return value + "0" * missing
        return value

    @staticmethod
    def _compensate_extra_cards_value(n_cards: int, value: str) -> str:
        """ Remove trailing zeros to the value in order to compensate extra cards. """
        if n_cards > 5:
            extras = n_cards - 5
            return value[: -1 * extras]
        return value

    def is_high_card(self) -> bool:
        """ Check if the hand is a high card. """
        return self.value < int("E" * 5, 16)

    def is_pair(self) -> bool:
        """ Check if the hand is a pair. """
        return int("E" * 5, 16) < self.value < int("E" * 6, 16)

    def is_two_pairs(self) -> bool:
        """ Check if the hand is a two pair. """
        return int("E" * 6, 16) < self.value < int("E" * 8, 16)

    def is_three_of_a_kind(self) -> bool:
        """ Check if the hand is a three of a kind. """
        return int("E" * 8, 16) < self.value < int("E" * 9, 16)

    def is_straight(self) -> bool:
        """ Check if the hand is a straight. """
        return int("E" * 9, 16) < self.value < int("E" * 10, 16)

    def is_flush(self) -> bool:
        """ Check if the hand is a flush. """
        return int("E" * 10, 16) < self.value < int("E" * 11, 16)

    def is_full_house(self) -> bool:
        """ Check if the hand is a full house. """
        return int("E" * 11, 16) < self.value < int("E" * 13, 16)

    def is_four_of_a_kind(self) -> bool:
        """ Check if the hand is a four of a kind. """
        return int("E" * 13, 16) < self.value < int("E" * 14, 16)

    def is_straight_flush(self) -> bool:
        """ Check if the hand is a straight flush. """
        return int("E" * 14, 16) < self.value < int("D" * 15, 16)

    def is_royal_straight_flush(self) -> bool:
        """ Check if the hand is a royal straight flush. """
        return self.value > int("D" * 15, 16)


class Player:
    """ Poker player. """

    def __init__(self, name: str, chips: float):
        self._name: str = name
        self._chips: float = self._validate_chips(chips)
        self._hand: Hand = Hand()

    def __repr__(self):
        return self._name

    @property
    def name(self) -> str:
        """ Get player name. """
        return self._name

    @property
    def chips(self) -> float:
        """ Get or set player chips amount. """
        return self._chips

    @chips.setter
    def chips(self, value: float):
        value = self._validate_chips(value)
        self._chips = value

    @property
    def hand(self) -> Hand:
        """ Get or set player hand. """
        return self._hand

    @hand.setter
    def hand(self, value: Hand):
        self._hand = value

    @staticmethod
    def _validate_chips(chips: float) -> float:
        """ Validate player chips amount. """
        if chips < 0:
            raise ValueError("Chips must equal or greater to zero.")
        return chips

    def add_cards(self, cards: Iterable[Card]):
        """ Add cards to a player hand. """
        for card in cards:
            self.hand.add(card)

    def clear_hand(self):
        """" Clear a player hand"""
        self.hand = Hand()


class Round:
    """ Poker game round. """

    def __init__(self, players: Sequence[Player], n_starting_cards: int = 5):
        self._players = players
        self._deck = Deck()
        self._n_starting_cards = n_starting_cards
        self.new()

    @property
    def players(self) -> Sequence[Player]:
        """ Get or set round players. """
        return self._players

    @players.setter
    def players(self, value: Sequence[Player]):
        self._players = value

    @property
    def deck(self) -> Deck:
        """ Get round deck. """
        return self._deck

    @property
    def n_starting_cards(self) -> int:
        """ Get round number of starting cards. """
        return self._n_starting_cards

    def deal_cards(self, player: Player, n_cards: int):
        """ Deal a number of cards to a single players. """
        cards = [self.deck.draw() for _ in range(n_cards)]
        player.add_cards(cards)

    def deal_cards_to_all(self, n_cards: int):
        """ Deal cards to all players. """
        for player in self.players:
            self.deal_cards(player=player, n_cards=n_cards)

    def new(self):
        """ Start a new round. """
        for player in self.players:
            player.clear_hand()
        self.deck.set_and_shuffle()
        self.deal_cards_to_all(self.n_starting_cards)

    def winner(self) -> np.ndarray:
        """ Evaluate the winner player. """
        return np.argmax([player.hand.value for player in self.players])


class Poker:
    """ Abstract class for a bluff game. """

    _N_STARTING_CARDS: int = 5

    def __init__(self, n_seats: int = 9):
        self._seats: List[Optional[Player]] = [None] * n_seats
        self._dealer = random.choice(range(n_seats))

    @property
    def seats(self) -> List[Optional[Player]]:
        """ Get list of seats. """
        return self._seats

    @property
    def dealer(self) -> int:
        """ Get dealer position. """
        return self._dealer

    @dealer.setter
    def dealer(self, value: int):
        if value >= len(self.seats):
            raise ValueError("Dealer must be set to an existing seat.")
        self._dealer = value

    def add_player(self, player: Player, seat: int):
        """ Add a player to a seat. """
        if self.seats[seat] is None:
            self.seats[seat] = player
        else:
            raise SeatOccupiedError(f"The seat {seat} is already occupied.")

    def add_players(
        self, players: Iterable[Player], seats: Optional[Iterable[int]] = None,
    ):
        """
        Add players to their seats. Use seats=None to choose seats
        randomly.
        """
        # When no seats are passed, chooses randomly.
        if seats is None:
            free_seats = [seat for seat, player in enumerate(self.seats) if not player]
            seats = [self._random_pop(free_seats) for _ in players]
        for player, seat in zip(players, seats):
            self.add_player(player=player, seat=seat)

    @staticmethod
    def _random_pop(lst: list):
        """ Randomly pop an item from a list."""
        return lst.pop(random.randrange(len(lst)))

    def remove_player(self, seat: int):
        """ Remove a player from a seat. """
        self.seats[seat] = None

    @staticmethod
    def _item_to_beginning(list_: list, index: int) -> List:
        """ Move an item to the beginning of a list. """
        return list_[index:] + list_[:index]

    def _validate_dealer(self):
        """ Find a valid position for the dealer. """
        # I sort the seats to put the dealer in the beginning so then I
        # only have to add values to the seat number until I find a
        # valid player. The move variable represents how  many seats the
        # dealer button must move until it finds a valid player.
        seats = self._item_to_beginning(self.seats, self.dealer)
        move = 0
        while seats[move] is None:
            move += 1
        self.dealer += move

    def new_round(self) -> Round:
        """ Start a new round with available players. """
        # Firstly, organize players list so it is passed to the Round
        # class in the playing order.
        self._validate_dealer()
        ordered_seats = self._item_to_beginning(self.seats, self.dealer)
        players = [seat for seat in ordered_seats if seat is not None]

        # Start a round
        rnd = Round(players=players, n_starting_cards=self._N_STARTING_CARDS)
        rnd.new()

        return rnd
