""" Poker coach web user ui. """

import streamlit as st
import numpy as np

import st_state_patch
import poker_coach
from poker_coach import handviz

SUITS_EMOJIS = {"s": ":spades:", "h": ":hearts:", "c": ":clubs:", "d": ":diamonds:"}

exception = None


def push_fold(n_seats, avg, std, random_state):
    """ Push fold training scenario. """

    return result, explanation


s = st.State()
if not s:
    s.random_state = np.random.randint(0, 1e9)

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

            called_ev = list()
            for action, chips in zip(equities, scene.villains_after_chips):
                win = scene.pot + min(chips, scene.hero_chips)
                lose = -1 * min(chips, scene.hero_chips)
                ev = scene.expected_value(chances=action, success=win, failure=lose)
                called_ev.append(ev)

            overall_ev = list()
            for action, aev in zip(scene.villains_after_range, called_ev):
                ev = scene.expected_value(
                    chances=1 - (action / 100), success=scene.pot, failure=aev
                )
                overall_ev.append(ev)

            iterator = zip(
                equities, called_ev, overall_ev, scene.villains_after_position
            )
            min_ev = np.inf
            for eq, call, ev, villain in iterator:
                if ev < min_ev:
                    min_ev = ev
                    explanation = (
                        f"Hero hand is {scene.hero_hand}",
                        f"Equity against {villain} is {100 * eq:.0f}%",
                        f"Expected value when being called by {villain} is {call:.1f} BB",
                        f"Expected value when stealing blinds is {scene.pot:n} BB",
                        f"Expected value against {villain} is {ev:.1f} BB",
                    )
                    explanation = "\n".join(explanation)

        result = min(overall_ev) > 1

        st.write(result, push, fold)
        if result is True and push is True:
            st.success(f"Correct")
        elif result is False and fold is True:
            st.success(f"Correct")
        else:
            st.error(f"Wrong")
        st.text(explanation)

else:

    raise (NotImplementedError("To be developed."))
