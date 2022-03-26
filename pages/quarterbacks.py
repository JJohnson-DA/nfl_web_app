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
        rosters = funcs.get_rosters([2021])
        # player_id_df = nfl.import_ids()

        # QB Selection
        player_key = depth_chart[
            (depth_chart.position == "QB") & (depth_chart.depth_team == 1)
        ]["full_name"].unique()
        player_id_list = [
            depth_chart[
                (depth_chart.position == "QB") & (depth_chart.full_name == x)
            ].gsis_id.unique()[0]
            for x in player_key
        ]
        player_dict = dict(zip(player_key, player_id_list))
        selected_player_key = str(
            st.selectbox(
                "Select a QB (type to search):", options=sorted(player_dict.keys()),
            )
        )
        player1_id = player_dict[selected_player_key]
        playe1_team = depth_chart[depth_chart.gsis_id == player1_id]["team"].unique()[0]
        player1_info = rosters[rosters.player_id == player1_id]

        team_info[team_info.team_abbr == playe1_team]
    photo_url = rosters[rosters.player_id == player1_id]["headshot_url"].values[0]
    # st.write(player_id_df[player_id_df.name == selected_player_key])
    # st.write(rosters)

    # ==== Team Customs ========================================================
    url_logo = team_info[team_info.team_abbr == playe1_team].team_logo_espn.values[0]
    url_team_wordmark = team_info[
        team_info.team_abbr == playe1_team
    ].team_wordmark.values[0]
    color1 = team_info[team_info.team_abbr == playe1_team].team_color.values[0]
    color2 = team_info[team_info.team_abbr == playe1_team].team_color2.values[0]

    # %% ==== Data Import ======================================================
    # st.subheader(f"Pass Plays for {selected_player_key} in {years[0]}")
    photo, desc = st.columns([1, 1.5])
    with photo:
        st.image(photo_url, width=300)
    with desc:
        st.subheader(selected_player_key)
        st.write(f"Height: {player1_info.height.values[0]} inches")
        st.write(f"Weight: {player1_info.weight.values[0]} pounds")
        st.write(f"College: {player1_info.college.values[0]}")
        st.write(f"Years in NFL: {round(player1_info.years_exp.values[0])} years")

    # kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    # with kpi1:
    #     st.write("none")
    # with kpi2:
    #     st.write("none")
    # with kpi3:
    #     st.write("none")
    # with kpi4:
    #     st.write("none")

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
        (raw.passer_player_id == player1_id)
        & (raw["pass"] == 1)
        & (raw.sack == 0)
        & (raw.interception == 0)
        & (raw.incomplete_pass == 0)
        & (pd.isnull(raw.pass_location) == False)
    ][pass_cols]
    pass_plays["air_yards"] = pass_plays.yards_gained - pass_plays.yards_after_catch

    weekly_passing = pd.melt(
        pass_plays.groupby("week")["yards_after_catch", "air_yards"]
        .sum()
        .reset_index(),
        id_vars="week",
        var_name="Yards Type",
        value_vars=["air_yards", "yards_after_catch"],
        value_name="Yards",
    )

    # st.write(weekly_passing)

    fig = px.bar(  # Yards/game barchart
        data_frame=weekly_passing,
        title="Weekly Passing Yards",
        x="week",
        y="Yards",
        color="Yards Type",
        color_discrete_sequence=[color1, color2],
        opacity=0.6,
        labels={
            "week": "Week",
            "air_yards": "Air Yards",
            "yards_after_catch": "Yards After Catch",
        },
    )
    fig.update_xaxes(showgrid=False,)
    fig.update_yaxes(showgrid=False,)
    st.plotly_chart(fig, config={"displayModeBar": False}, use_container_width=True)

    st.write(pass_plays)

