""" Poker coach web user interface. """

import streamlit as st
import numpy as np

import poker_coach

SUITS_EMOJIS = {"s": ":spades:", "h": ":hearts:", "c": ":clubs:", "d": ":diamonds:"}

# Sidebar

st.sidebar.title("Poker Coach")
st.sidebar.text("Practice short-stacked no limit hold'em")

scenario_option = (
    "Open Shove",
    "Call Shove",
)
scenario = st.sidebar.radio(label="Select scenario:", options=scenario_option)

# Main
if "Open Shove" in scenario:

    scene = poker_coach.PushFoldScenario()

    hero_hand = scene.hero_hand

    # introduce spaces for easily replacing
    hero_hand = " ".join([char for char in hero_hand])

    for old, new in SUITS_EMOJIS.items():
        hero_hand = hero_hand.replace(f" {old}", new)

    hero_position_name = scene.position_to_abbreviation(
        scene.hero_position, scene.n_seats
    )
    st.write(f"Hero hand is **{hero_hand}** at @ **{hero_position_name}**")
    st.write("")

    villain_position = scene.hero_position
    for villain_range in scene.villains_after_range:
        villain_position += 1
        villain_position_name = scene.position_to_abbreviation(
            villain_position, scene.n_seats
        )
        st.write(
            f"**{villain_position_name}** call push range is **{villain_range:.0f}%**"
        )
    st.write("")

    shove = st.button("Shove")
    fold = st.button("Fold")

    show_answer = any((shove, fold))

    # TODO Evaluate choice
    if show_answer:
        correct = np.random.choice([True, False])
        print(correct)

        if correct:
            st.success("Correct")
        else:
            st.error("Wrong")

        next_ = st.button("Next")
        if next_:
            show_answer = False

else:
    st.exception(NotImplementedError("To be developed."))
