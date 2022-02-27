# %% ==== Package Imports ======================================================

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import funcs
import nfl_data_py as nfl


def app():
    # ==== App Setup ===========================================================
    st.header("Quarterback Stats and Performance")
    st.write("---")

    # Get Team Info to use in filters
    team_info = funcs.get_team_info()

    # ==== Initial Filter Grabs ================================================

    # Create filters
    with st.sidebar:
        st.header("Choose Your Filters")
        # Season Selection
        seasons = reversed([x for x in range(2010, 2022)])
        years = [st.selectbox("Select a Season:", options=seasons)]
        raw = funcs.get_raw_pbp(years)
        depth_chart = funcs.get_dc(years)

        # QB Selection
        player_key = depth_chart[
            (depth_chart.position == "QB") & (depth_chart.depth_team == 1)
        ]["full_name"].unique()
        player_value = [name[0] + "." + name.split(" ")[1] for name in player_key]
        player_dict = dict(zip(player_key, player_value))
        selected_player_key = str(
            st.selectbox(
                "Select a QB (type to search):", options=sorted(player_dict.keys()),
            )
        )
        selected_player = player_dict[selected_player_key]

    # %% ==== Data Import ======================================================

    st.subheader(f"Pass Plays for {selected_player} in {years[0]}")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.write("none")
    with kpi2:
        st.write("none")
    with kpi3:
        st.write("none")
    with kpi4:
        st.write("none")

    # ==== Team Summary ========================================================

    pass_cols = [
        "week",
        "qtr",
        "passer",
        "yardline_100",
        "yrdln",
        "pass_length",
        "pass_location",
        "pass_touchdown",
        "yards_gained",
        "yards_after_catch",
        "receiver",
    ]
    pass_plays = raw[
        (raw.passer == selected_player)
        & (raw["pass"] == 1)
        & (raw.sack == 0)
        & (raw.interception == 0)
        & (raw.incomplete_pass == 0)
        & (pd.isnull(raw.pass_location) == False)
    ][pass_cols]
    pass_plays["air_yards"] = pass_plays.yards_gained - pass_plays.yards_after_catch
    st.write(pass_plays)

