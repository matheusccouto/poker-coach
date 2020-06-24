""" Poker coach web user interface. """

import streamlit as st
import numpy as np

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

    # TODO Create random case and show here.
    st.text("Case shows up here.")

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
