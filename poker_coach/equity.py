""" Hand evaluation. """

import cProfile
import itertools
import os
import random
from typing import Sequence, Dict, Iterator, Union

import numpy as np
import pandas as pd

import poker

from poker_coach import utils

BROADWAY_NUMBERS: Dict[str, int] = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10}
BROADWAY_NUMBERS.update({str(i): i for i in range(2, 10)})

DATA_FOLDER: str = "data"
HAND_RANKING_FILE: str = "sk_hand_rankings.csv"

RANKS: Sequence[str] = list(BROADWAY_NUMBERS.keys())
SUITS: Sequence[str] = ["s", "h", "c", "d"]
DECK: Sequence[str] = [rank + suit for rank, suit in itertools.product(RANKS, SUITS)]

hand_ranking_rel_path = os.path.join(DATA_FOLDER, HAND_RANKING_FILE)
hand_ranking_path = os.path.join(os.path.dirname(__file__), hand_ranking_rel_path)
hand_ranking = pd.read_csv(hand_ranking_path)

reversed_broadway = {val: key for key, val in BROADWAY_NUMBERS.items()}


def prepare_descr(descr: str) -> str:
    """
    Prepare description to the desired format.

    Args:
        descr: Hand description.

    Returns:
        Hand description.
    """
    # If no indication of the suits, then append "o" to indicate that it is offsuit.
    if "s" not in descr.lower() and "o" not in descr.lower():
        descr += "o"

    # Ranks uppercase and suits lowercase.
    descr = descr[:-1].upper() + descr[-1:].lower()

    return descr


def descr_to_hands(descr: str) -> Iterator[str]:
    """
    Enumerate every possible hand from a description.

    Args:
        descr: Hand description.

    Returns:
        Generator for every hand from the descriptor.
    """
    # Suit is the last character.
    ranks = descr[:-1]
    suit = descr[-1:]

    if ranks[0] == ranks[1]:  # Pair.
        suits_combo = itertools.combinations(SUITS, 2)
    elif "o" in suit:  # Off-suited.
        suits_combo = itertools.permutations(SUITS, 2)
    else:  # Suited
        suits_combo = (suit * 2 for suit in SUITS)

    ranks_combo = itertools.combinations(ranks, 2)

    cards = itertools.product(ranks_combo, suits_combo)
    cards_concat = (rank[0] + suit[0] + rank[1] + suit[1] for rank, suit in cards)

    return cards_concat


def descr_to_range(descr: str) -> Sequence[str]:
    """
    Enumerate every hand equal or higher from from description.

    Args:
        descr: Range description.

    Returns:
        Generator for every hand description from the range description.
    """
    # Suit is the last character.
    ranks = descr[:-1]
    suit = descr[-1:]

    lead = ranks[0]
    trail = ranks[1]

    # Transform in numerical to use the built-in function range.
    for old, new in BROADWAY_NUMBERS.items():
        lead = lead.replace(str(old), str(new))
        trail = trail.replace(str(old), str(new))

    lead = int(lead)
    trail = int(trail)

    # Prepare a reversed dictionary to transform back into letters.
    back_to_str = {value: key for key, value in BROADWAY_NUMBERS.items()}

    if lead == trail:
        return [f"{back_to_str[i] * 2}o" for i in range(lead, 15)]

    return [
        back_to_str[i] + back_to_str[j] + suit
        for i in range(lead, 15)
        for j in range(trail, i)
    ]


def range_to_hands(rng: Sequence[str]) -> Iterator[str]:
    """
    Transform a descriptions sequence into hands iterator.

    Args:
        rng: Hand descriptions range.

    Returns:
        Hands generator.
    """
    nested = (descr_to_hands(descr) for descr in rng)
    return utils.flatten(nested)


def descr_to_higher_or_equal_hands(descr: str) -> Iterator[str]:
    """
    Get every hand higher or equal (from the same high card) from a hand description.

    Args:
        descr: Hand description.

    Returns:
        Hands iterator.
    """
    descr = prepare_descr(descr)
    rng = descr_to_range(descr)
    return range_to_hands(rng)


def get_all_hands(descr_range: str) -> Sequence[str]:
    """
    Get every possible hand from a description of several hands range.

    If the card has the full description, it won't try to get all hands.

    Args:
        descr_range: Description range where each description is separated by space.

    Returns:
        Sequence with all hands possible.
    """
    descr_list = descr_range.split(" ")
    hands_nested = [
        descr_to_higher_or_equal_hands(descr) if len(descr) < 4 else descr
        for descr in descr_list
    ]
    return list(set(utils.flatten(hands_nested)))  # Remove duplicates


def hand_to_descr(hand: str) -> str:
    """
    Get hand general description from detailed hand description.

    Args:
        hand: Detailed hand description.

    Returns:
        Hand percentage.
    """
    # Check if suited.
    is_suited = hand[1] == hand[3]
    # Extract cards ranks
    hand = [hand[0], hand[2]]
    # Transform into numerical, sort, then transform back into a string.
    num_ranks = [BROADWAY_NUMBERS[rank] for rank in hand]
    sorted_ranks = sorted(num_ranks, reverse=True)
    str_ranks = [reversed_broadway[rank] for rank in sorted_ranks]
    descr = "".join(str_ranks)
    # Add suited mark if it is the case.
    if is_suited:
        descr += "s"
    return descr


def descr_to_percentage(descr: str) -> float:
    """
    Get ranking percentage from a hand description.

    Args:
        descr: Hand description.

    Returns:
        Hand percentage.
    """
    descr = descr.replace("o", "")  # The ranking does not use the o notation.
    return hand_ranking[hand_ranking["hand"] == descr]["value"].values[0]


def percentage_range(percentage: float) -> str:
    """
    Get hand range from a ranking percentage.

    Args:
        percentage: Hand percentage.

    Returns:
        Hand range.
    """
    percentage = np.clip(percentage, 0.5, 100)
    return hand_ranking[hand_ranking["value"] <= percentage]["range"].values[-1]


def percentage_descr(percentage: float) -> str:
    """
    Get hand descr from a ranking percentage.

    Args:
        percentage: Hand percentage.

    Returns:
        Hand description.
    """
    percentage = np.clip(percentage, 0.5, 100)
    return hand_ranking[hand_ranking["value"] <= percentage]["hand"].values[-1]


def flop_turn_river(dead: Sequence[str]) -> Sequence[str]:
    """
    Get flop turn and river cards.

    Args:
        dead: Dead cards.

    Returns:
        5 cards.
    """
    dead_concat = "".join(dead)
    deck = [card for card in DECK if card not in dead_concat]
    return random.sample(deck, 5)


def eval_combinations(hand, board):
    """
    Evaluate every possible combination of hole cards and board.

    Args:
        hand: Hole cards.
        board: Board cards.

    Returns:
        Highest hand value.
    """
    cards = np.concatenate([[hand[:2], hand[2:]], board])
    combos = itertools.combinations(cards, r=5)
    return np.max([poker.Hand("".join(combo)).value for combo in combos])


def eval_directly(hand, board):
    """
    Evaluate all cards at the same time.

    Please notice that this function fails at evaluating ties.

    Args:
        hand: Hole cards.
        board: Board cards.

    Returns:
        Highest hand value.
    """
    cards = np.concatenate([[hand[:2], hand[2:]], board])
    return poker.Hand("".join(cards)).value


# TODO: Create less precise but faster way
def eval_single(
    player_hands: Sequence[Iterator[str]], precise: bool = False
) -> np.array:
    """
    Evaluate a single game.

    Args:
        player_hands: Each players possible hands.
        precise: Evaluate precisely (time-consuming).

    Returns:
        Array where the hand winner is 1 and loser is 0.
    """
    hands_list = [random.choice(hands) for hands in player_hands]
    board = flop_turn_river(dead=hands_list)
    if precise:
        eval_func = eval_combinations
    else:
        eval_func = eval_directly
    values_list = [eval_func(hand, board) for hand in hands_list]
    results = np.where(values_list == np.max(values_list), 1, 0)
    return results


def equity_from_range_descr(
    players_ranges: Sequence[str], times: int = 10000
) -> Sequence[float]:
    """
    Calculate each player pre-flop equity from their range descriptions using Monte
    Carlo procedure.

    Args:
        players_ranges: Sequence of range descriptions.
        times: Number of times to evaluate.

    Returns:
        Sequence of equities.
    """
    all_hands = [get_all_hands(descr_range) for descr_range in players_ranges]
    results = [eval_single(all_hands, precise=False) for _ in range(times)]
    mean = np.mean(results, axis=0)
    norm_mean = mean / mean.sum()
    return norm_mean


def equity(
    players_ranges: Sequence[Union[str, float]], times: int = 10000
) -> Sequence[float]:
    """
    Calculate each player pre-flop equity from their range descriptions or percentage
    using Monte Carlo procedure.

    Args:
        players_ranges: Sequence of range descriptions or percentages.
        times: Number of times to evaluate.

    Returns:
        Sequence of equities.
    """
    players_ranges = [
        descr if isinstance(descr, str) else percentage_range(descr)
        for descr in players_ranges
    ]
    return equity_from_range_descr(players_ranges, times)
