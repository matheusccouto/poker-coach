""" Poker coach web user ui. """

import streamlit as st
import numpy as np

import poker_coach
from poker_coach import handviz

SUITS_EMOJIS = {"s": ":spades:", "h": ":hearts:", "c": ":clubs:", "d": ":diamonds:"}

exception = None


def push_fold(n_seats, avg, std):
    """ Push fold training scenario. """
    scene = poker_coach.PushFoldScenario(
        n_seats=n_seats, field_call_avg=avg, field_call_std=std
    )

    # Insert spaces for easily replacing for emojis.
    hero_hand = " ".join([char for char in scene.hero_hand])
    for old, new in SUITS_EMOJIS.items():
        hero_hand = hero_hand.replace(f" {old}", new)

    hero_hand_descr = poker_coach.equity.hand_to_descr(scene.hero_hand)
    hero_percentage = poker_coach.equity.descr_to_percentage(hero_hand_descr)

    # Hero.
    hero_position_name = scene.position_to_abbreviation(
        scene.hero_index, scene.n_seats
    )

    # Villains
    villains_after_name = list()
    villain_position = scene.hero_index
    for v_range, v_chips in zip(scene.villains_after_range, scene.villains_after_chips):
        villain_position += 1
        villain_position_name = scene.position_to_abbreviation(
            villain_position, scene.n_seats
        )
        villains_after_name.append(villain_position_name)

    fig = handviz.hand(
        n_seats=n_seats,
        pot=scene.pot,
        hero_name=scene.hero_position,
        hero_hand=scene.hero_hand,
        hero_chips=scene.hero_chips,
        villains_names=scene.villains_after_position,
        villains_ranges=scene.villains_after_range,
        villains_chips=scene.villains_after_chips,
    )

    st.pyplot(fig, clear_figure=True)

    # User choices.
    shove = st.button("Shove")
    fold = st.button("Fold")
    show_answer = any((shove, fold))

    if show_answer:

        with st.spinner("Calculating..."):

            equities = scene.eval_ranges(
                hero_hand=scene.hero_hand,
                villains_range=scene.villains_after_range,
                times=monte_carlo,
            )

            action_ev = list()
            for action, chips in zip(equities, scene.villains_after_chips):
                win = scene.pot + min(chips, scene.hero_chips)
                lose = -1 * min(chips, scene.hero_chips)
                ev = scene.expected_value(chances=action, success=win, failure=lose)
                action_ev.append(ev)

            excpected_values = list()
            for action, aev in zip(scene.villains_after_range, action_ev):
                ev = scene.expected_value(
                    chances=1 - (action / 100), success=scene.pot, failure=aev
                )
                excpected_values.append(ev)

            for eq, aev, ev in zip(equities, action_ev, excpected_values):
                explanation = (
                    f"Hero hand: {scene.hero_hand}\n"
                    f"Equity against villain range: {eq}\n"
                    f"Expected value when being called: {aev}\n"
                    f"Expected value when stealing: {scene.pot}\n"
                    f"Overall expected value {ev}"
                )
                st.text(explanation)

        correct = np.random.choice([True, False])

        if correct:
            st.success(f"Correct")
        else:
            st.error(f"Wrong")

        next_ = st.button("Next")
        if next_:
            show_answer = False


# Sidebar

st.sidebar.title("Poker Coach")
st.sidebar.text("Practice short-stacked no limit hold'em")

st.sidebar.subheader("Scenario")
scenario_options = (
    "Open Shove",
    "Call Shove",
)
scenario = st.sidebar.selectbox(label="Select scenario:", options=scenario_options)
n_players = st.sidebar.slider(
    label="Number of Players:", min_value=2, max_value=9, value=9, step=1
)

st.sidebar.subheader("Field")
field_options = [
    "Custom",
    "Micro-stakes",
    "Small-stakes",
    "Medium-stakes",
    "High-stakes",
]
field_level = st.sidebar.selectbox(label="Select field level:", options=field_options)
if "Custom" in field_level:
    field_avg = st.sidebar.number_input(
        label="Average action (%)", min_value=1, max_value=100, value=20, step=1
    )

    field_std = st.sidebar.number_input(
        label="Action standard deviation (%)",
        min_value=1,
        max_value=100,
        value=20,
        step=1,
    )
else:
    raise (NotImplementedError("To be developed."))

st.sidebar.subheader("Evaluation")
eval_options = ["Monte Carlo", "Linear Model"]
eval_method = st.sidebar.selectbox(label="Evaluation method:", options=eval_options)
if "Monte Carlo" in eval_method:
    monte_carlo = st.sidebar.number_input(
        label="Number of runs:", min_value=100, value=100, step=100
    )
else:
    raise (NotImplementedError("To be developed."))

# Main
if "Open Shove" in scenario:
    push_fold(n_players, field_avg, field_std)
else:
    raise (NotImplementedError("To be developed."))
