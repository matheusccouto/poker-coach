""" Poker coach web user ui. """

import streamlit as st
import numpy as np
import pandas as pd

import st_state_patch
import poker_coach
from poker_coach import handviz

SUITS_EMOJIS = {"s": ":spades:", "h": ":hearts:", "c": ":clubs:", "d": ":diamonds:"}

exception = None

# Session State
s = st.State()
if not s:
    s.random_state = np.random.randint(0, 1e9)

# Sidebar

st.sidebar.title("Poker Coach")
st.sidebar.text("Practice short-stacked no limit hold'em")

st.sidebar.subheader("Scenario")
scenario_options = ("Open Shove", "Call Shove")
scenario = st.sidebar.selectbox(label="Select scenario:", options=scenario_options)
n_players = st.sidebar.slider(
    label="Number of Players:", min_value=2, max_value=9, value=9
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
        label="Number of runs:", min_value=100, value=1000, step=100
    )
else:
    raise (NotImplementedError("To be developed."))

# Main

if st.button("Next"):
    s.random_state = np.random.randint(0, 1e9)

if "Open Shove" in scenario:

    scene = poker_coach.PushFoldScenario(
        n_seats=n_players,
        field_call_avg=field_avg,
        field_call_std=field_std,
        random_state=s.random_state,
    )

    fig = handviz.hand(
        n_seats=n_players,
        pot=scene.pot,
        hero_name=scene.hero_position,
        hero_hand=scene.hero_hand,
        hero_chips=scene.hero_chips,
        villains_names=scene.villains_after_position,
        villains_ranges=scene.villains_after_range,
        villains_chips=scene.villains_after_chips,
    )

    st.pyplot(fig, clear_figure=True)

    push = st.button("Push")
    fold = st.button("Fold")

    if push or fold:

        with st.spinner("Calculating..."):

            equities = scene.eval_ranges(
                hero_hand=scene.hero_hand,
                villains_range=scene.villains_after_range,
                times=monte_carlo,
            )
            win_value = scene.pot + np.minimum(
                scene.villains_after_chips, scene.hero_chips
            )
            lose_value = -1 * np.minimum(scene.villains_after_chips, scene.hero_chips)
            showdown_value = scene.expected_value(
                chances=equities, success=win_value, failure=lose_value,
            )
            fold_equity = scene.pot * (1 - scene.villains_after_range / 100)
            expected_values = np.add(showdown_value, fold_equity)
            composed_value = np.average(
                expected_values, weights=scene.villains_after_range
            )

            df = pd.DataFrame(
                {
                    "Equity (%)": equities,
                    "Showdown Value (BB)": showdown_value,
                    "Fold Equity (BB)": fold_equity,
                    "Expected Value (BB)": expected_values,
                },
                index=scene.villains_after_position
            )

        result = bool(min(expected_values) > 0)
        correct = (result and push) or (not result and fold)

        if correct:
            st.success(f"Correct")
        else:
            st.error(f"Wrong")

        st.table(data=df.style.format("{:.2f}"))

else:
    raise (NotImplementedError("To be developed."))
