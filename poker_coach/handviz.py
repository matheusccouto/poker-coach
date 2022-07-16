# TODO: Implement session state to control test and next button
# TODO: Show results in the plot
# TODO: Conditional coloring in the plot

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

from . import equity

rcParams["font.family"] = "monospace"


SUITS_COLORS = {"s": "k", "h": "r", "c": "g", "d": "b"}


def ellipse(theta):
    """ Ellipse shape."""
    a = 2
    b = 1
    return a * b / np.sqrt((a * np.sin(theta) ** 2) + (b * np.cos(theta) ** 2))


def hand(
    n_seats,
    pot,
    hero_name,
    hero_hand,
    hero_chips,
    villains_names,
    villains_ranges,
    villains_chips,
):
    """ Hand viewer. """

    # Table line
    theta_arr = np.linspace(start=0, stop=2 * np.pi, num=100, endpoint=True)
    radius_arr = [ellipse(t) for t in theta_arr]

    # Seats coordinates.
    seats_theta = -1 * np.linspace(start=0, stop=2 * np.pi, num=n_seats, endpoint=False)
    seats_radius = [ellipse(t) for t in seats_theta]

    # Place players into the seats. (+ 1 because of the hero).
    players_theta = [seats_theta[i] for i in range(len(villains_names) + 1)]
    players_radius = [seats_radius[i] for i in range(len(villains_names) + 1)]

    # Create figure and polar axes.
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_axes([0.1, 0, 0.8, 1], polar=True)

    # Create table.
    ax.plot(theta_arr, radius_arr, color="green", linewidth=5)
    ax.fill_between(theta_arr, radius_arr, color="lightgray")
    ax.axis("off")

    # Get hero hand percentage.
    hero_descr = equity.hand_to_descr(hero_hand)
    hero_percent = equity.descr_to_percentage(hero_descr)

    # Concatenate hero and villains.
    players_name = np.concatenate([[hero_name], villains_names])
    players_range = np.concatenate([[hero_percent], villains_ranges])
    players_chips = np.concatenate([[hero_chips], villains_chips])

    iterator = zip(
        players_name, players_range, players_chips, players_theta, players_radius,
    )

    # Players
    for name, rng, chips, theta, radius in iterator:

        bbox_props = dict(boxstyle="Round", fc="whitesmoke", ec="green")
        ax.annotate(
            f"{name} {rng:.0f}%\n{chips} BB",
            xy=(theta, radius),
            ha="center",
            va="center",
            bbox=bbox_props,
        )

    # How much the small blind will be moved to avoid overlapping.
    move_small_blind = 0

    # Dealer index.
    if n_seats == 2:
        dealer_idx = -2
        move_small_blind = -0.2  # Displace small blind to not overlap the button.
    elif len(players_name) == 2:
        dealer_idx = None
    else:
        dealer_idx = -3

    if dealer_idx is not None:
        bbox_props = dict(boxstyle="Circle", fc="pink", ec="k")
        ax.annotate(
            "D",
            xy=(players_theta[dealer_idx], 0.7 * players_radius[dealer_idx]),
            ha="center",
            va="center",
            bbox=bbox_props,
        )

    # Blinds and antes
    ax.annotate(f"Antes\n{pot - 1.5} BB", xy=(0, 0), ha="center", va="center")
    ax.annotate(
        "1 BB",
        xy=(players_theta[-1], 0.7 * players_radius[-1]),
        ha="center",
        va="center",
    )
    ax.annotate(
        ".5 BB",
        xy=(players_theta[-2], (0.7 + move_small_blind) * players_radius[-2]),
        ha="center",
        va="center",
    )

    # Hero cards.
    card0 = hero_hand[:2]
    card1 = hero_hand[2:]

    rank0 = card0[0]
    rank1 = card1[0]

    suit0 = card0[1]
    suit1 = card1[1]

    bbox_props = dict(boxstyle="Round", fc="w", ec="green")
    hero_cards_kwargs = dict(
        va="center",
        bbox=bbox_props,
        fontsize="x-large",
        fontweight="bold",
        annotation_clip=False,
    )
    ax.annotate(
        rank0,
        xy=(players_theta[0], 1.35 * players_radius[0]),
        ha="right",
        color=SUITS_COLORS[suit0],
        **hero_cards_kwargs,
    )
    ax.annotate(
        rank1,
        xy=(players_theta[0], 1.41 * players_radius[0]),
        ha="left",
        color=SUITS_COLORS[suit1],
        **hero_cards_kwargs,
    )

    return fig
