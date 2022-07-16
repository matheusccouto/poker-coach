""" Poker coach web user ui. """

import joblib

import streamlit as st
import numpy as np
import pandas as pd

import st_state_patch
import poker_coach
from poker_coach import handviz
from PIL import Image

exception = None

# Session State
s = st.State()
if not s:
    s.random_state = np.random.randint(0, 1e9)

# Sidebar
myImage=Image.open("img/Logo.png")
myImage.show()
st.sidebar.image(myImage)
st.sidebar.markdown("# Aspiring Poker Pro Coach\nPractice short-stacked no limit hold'em")
st.sidebar.markdown("Back to [AspiringPokerPro.com](https://www.aspiringpokerpro.com)")

st.sidebar.subheader("Scenario")
scenario_options = ("Open Shove", "Call Shove")
scenario = st.sidebar.selectbox(label="Select scenario:", options=scenario_options)
n_players = st.sidebar.slider(
    label="Number of Players:", min_value=2, max_value=9, value=9
)

st.sidebar.subheader("Field")
field_mode = st.sidebar.slider(
    label="Action mode (%)", min_value=1, max_value=99, value=20, step=1
)
field_bandwidth = st.sidebar.slider(
    label="Action bandwidth (%)", min_value=1, max_value=99, value=50, step=1
)

field_min = float(np.clip(field_mode - (field_bandwidth / 2), 0, 100))
field_max = float(np.clip(field_mode + (field_bandwidth / 2), 0, 100))


st.sidebar.subheader("Evaluation")
eval_options = [
    "Monte Carlo",
    "Model",
]
eval_method = st.sidebar.selectbox(label="Evaluation method:", options=eval_options)
if "Monte Carlo" in eval_method:
    monte_carlo = st.sidebar.number_input(
        label="Number of runs:", min_value=100, value=10000, step=100
    )
else:
    model = joblib.load("model.pkl")

# Main

if st.button("Next"):
    s.random_state = np.random.randint(0, 1e9)

if "Open Shove" in scenario:

    scene = poker_coach.PushFoldScenario(
        n_seats=n_players,
        field=(field_min, field_mode, field_max),
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

            if "Monte Carlo" in eval_method:
                equities = scene.eval_ranges(
                    hero_hand=scene.hero_hand,
                    villains_range=scene.villains_after_range,
                    times=monte_carlo,
                )
            else:
                hero_descr = poker_coach.equity.hand_to_descr(scene.hero_hand)
                hero_rng = poker_coach.equity.descr_to_percentage(hero_descr)
                equities = np.array(
                    [
                        model.predict(np.array([[hero_rng, villain_rng]]))[0]
                        for villain_rng in scene.villains_after_range
                    ]
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

            df = pd.DataFrame(
                {
                    "Equity (%)": equities,
                    "Showdown Value (BB)": showdown_value,
                    "Fold Equity (BB)": fold_equity,
                    "Expected Value (BB)": expected_values,
                },
                index=scene.villains_after_position,
            )

        result = bool(min(expected_values) > 0)
        correct = (result and push) or (not result and fold)

        if correct:
            st.success(f"Correct")
        else:
            st.error(f"Wrong")

        st.table(data=df.style.format("{:.2f}"))

else:
    raise NotImplementedError("To be developed.")

st.sidebar.markdown("")
st.sidebar.markdown("")

