# %% ==== Package Imports ======================================================

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import funcs
import nfl_data_py as nfl


def app():
    # ==== Collect Filters =====================================================
    # Get Team Info to use in filters
    team_info = funcs.get_team_info()

    # ---- Initial Filter Grabs ----
    # Define Lists and Dictionaries to use
    seasons = reversed([x for x in range(2010, 2022)])

    team_dict = dict(zip(team_info.team_nick, team_info.team_abbr))
    team_dict["Rams"] = "LA"
    team_dict["Chargers"] = "LAC"
    team_dict["Raiders"] = "LV"

    # Create filters
    with st.sidebar:
        st.header("Choose Your Filters")
        years = [st.selectbox("Select a Season:", options=seasons)]
        team_options = sorted([x for x in team_dict.keys()])
        selected_team = str(
            st.selectbox(
                "Select a Team:", options=team_options, index=len(team_options) - 1
            )
        )
        game_type_pick = st.selectbox(
            "Regular/Playoff Games:",
            options=["Regular Season", "Playoffs", "All Games"],
        )

    # ==== Team Customs ========================================================
    url_logo = team_info[team_info.team_nick == selected_team].team_logo_espn.values[0]
    url_team_wordmark = team_info[
        team_info.team_nick == selected_team
    ].team_wordmark.values[0]
    color1 = team_info[team_info.team_nick == selected_team].team_color.values[0]
    color2 = team_info[team_info.team_nick == selected_team].team_color2.values[0]

    # ==== Page Header Logo ====================================================
    title, wordmark = st.columns([3, 2])
    with title:
        st.header("Team Stats and Performance")
        st.write("Use the filters in the sidebar to explore.")
    with wordmark:
        st.image(url_team_wordmark, width=300)
    st.write("---")

    # ==== Data Import and Filtering ===========================================

    # Import raw data
    raw = funcs.get_raw_pbp(years)

    # Filter data based on game type
    if game_type_pick == "Regular Season":
        data = raw[raw.season_type == "REG"]
    elif game_type_pick == "Playoffs":
        data = raw[raw.season_type == "POST"]
    else:
        data = raw.copy()

    if team_dict[selected_team] not in data.posteam.unique():
        st.write(
            f"The selected team does not have any games in the {years[0]} {game_type_pick}"
        )
    else:
        # ---- Team Data Filtering ----
        team_data = funcs.team_season_filter(
            data, team_dict, selected_team, game_type_pick
        )

        # ==== KPI Strip ===========================================================
        with st.container():
            season_games = (
                team_data.groupby(["week", "home_team", "away_team"])[
                    "home_score", "away_score"
                ]
                .max()
                .reset_index()
            )
            st.subheader(f"{game_type_pick} - {years[0]}")

            # ---- Get data for KPIs ----
            wins, losses, avg_points, avg_points_against = funcs.season_kpis(
                season_games, team_dict, selected_team
            )
            nfl_avg_points = funcs.avg_score(data, team_dict, game_type_pick)

            # ---- Create KPI visuals ----
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric(
                    label="Wins", value=wins,
                )
            with kpi2:
                st.metric(
                    label="Losses", value=losses,
                )
            with kpi3:
                st.metric(
                    label="Avg Points",
                    value=avg_points,
                    delta=f"{round(avg_points - nfl_avg_points,1)} vs NFL",
                )
            with kpi4:
                st.metric(
                    "Avg Points Against",
                    value=avg_points_against,
                    delta=f"{round(avg_points_against - nfl_avg_points,1)} vs NFL",
                    delta_color="inverse",
                )

        # ==== High Level Stats ====================================================
        with st.expander("High Level Overall"):
            with st.container():  # ---- Yards ----
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                with kpi1:  # Total Yards
                    st.metric(
                        label="Total Yds",
                        value=round(
                            team_data[
                                team_data.posteam == team_dict[selected_team]
                            ].yards_gained.sum()
                        ),
                    )
                with kpi2:  # yards/game
                    st.metric(
                        label="Yds/Game",
                        value=round(
                            team_data[team_data.posteam == team_dict[selected_team]]
                            .groupby("week")["yards_gained"]
                            .sum()
                            .reset_index()
                            .yards_gained.mean()
                        ),
                    )
                with kpi3:  # rushing yards
                    st.metric(
                        label="Rushing Yds",
                        value=round(
                            team_data[
                                (team_data.posteam == team_dict[selected_team])
                                & (team_data.play_type == "run")
                            ].yards_gained.sum()
                        ),
                    )
                with kpi4:  # passing yards
                    st.metric(
                        label="Passing Yds",
                        value=round(
                            team_data[
                                (team_data.posteam == team_dict[selected_team])
                                & (team_data.play_type == "pass")
                            ].yards_gained.sum()
                        ),
                    )

                fig = px.bar(  # Yards/game barchart
                    data_frame=team_data[
                        (team_data.posteam == team_dict[selected_team])
                        & (
                            (team_data.play_type == "run")
                            | (team_data.play_type == "pass")
                        )
                    ][["week", "play_type", "yards_gained"]]
                    .groupby(["week", "play_type"])
                    .sum()
                    .reset_index(),
                    x="week",
                    y="yards_gained",
                    color="play_type",
                    color_discrete_sequence=[color1, color2],
                    opacity=0.6,
                    labels={
                        "week": "Week",
                        "yards_gained": "Yards Gained on Play",
                        "play_type": "Play Type",
                    },
                )
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False, rangemode="tozero")
                st.plotly_chart(
                    fig, config={"displayModeBar": False}, use_container_width=True
                )
                # st.write(
                #     team_data.groupby("week")[
                #         ["week", "home_team", "away_team", "posteam"]
                #     ].max()
                # )
                # game_data = team_data.groupby("week")[
                #     ["week", "home_team", "away_team", "posteam"]
                # ].max()
                # opponents = []
                # for i in game_data.index:
                #     if game_data.loc[i, "home_team"] == team_dict[selected_team]:
                #         opponents.append(game_data.loc[i, "away_team"])
                #     else:
                #         opponents.append(game_data.loc[i, "home_team"])
                # st.write(opponents)

        # --- Miscellaneous ----
        # Plays, 1st downs, 3rd down conversion rate, redzone appearances, TD, FG

        # ==== Offensive Stats =====================================================
        with st.expander("Offense"):
            with st.container():  # ---- Passing ----
                st.subheader(f"Passing Stats - {years[0]}")
                # get passing stats from function
                (
                    pass_attempts,
                    comp_perc,
                    pass_yards,
                    pass_td,
                    interceptions,
                ) = funcs.team_pass_stats(team_data, team_dict, selected_team)
                # Get League Passing Stats
                (
                    league_pass_attempts,
                    league_comp_perc,
                    league_pass_yards,
                    league_pass_td,
                    league_interceptions,
                ) = funcs.league_avg_pass_stats(data)

                # Create KPI layout
                kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                # Fill KPI containers
                with kpi1:  # Attempts
                    st.metric(
                        label="Attempts",
                        value=pass_attempts,
                        delta=f"{pass_attempts - league_pass_attempts} vs NFL",
                    )
                with kpi2:  # Completion %
                    st.metric(
                        label="Completion %",
                        value=comp_perc,
                        delta=f"{round(comp_perc - league_comp_perc, 1)} vs NFL",
                    )
                with kpi3:  # Yards
                    st.metric(
                        label="Passing Yds",
                        value=pass_yards,
                        delta=f"{pass_yards - league_pass_yards} vs NFL",
                    )
                with kpi4:  # TD
                    st.metric(
                        label="Touchdowns",
                        value=pass_td,
                        delta=f"{pass_td - league_pass_td} vs NFL",
                    )
                with kpi5:  # Interceptions
                    st.metric(
                        label="Interceptions",
                        value=interceptions,
                        delta=f"{interceptions - league_interceptions} vs NFL",
                        delta_color="inverse",
                    )
                st.write("---")

            with st.container():  # ---- Receiving ----
                st.subheader("Receiving Stats")
                # Receptions, yards, yards/rec, TD, avg rec length (dist), dist by down

                st.write("---")

            with st.container():  # ---- Rushing ----
                st.subheader("Rushing Stats")
                # rushes, Yds, TD, avg run length (dist), dist by down

        # ==== Defensive Stats =====================================================
        with st.expander("Defense"):
            st.write("Stats Here.")
        # ---- Tackles/Sacks ----
        # Tackles for loss, Sacks, 4th down stops (%), goal line stops (%)

        # ---- Turnovers ----
        # Int, Forced Fumbles, Fumble Recoveries

        # ---- Scoring ----
        # Fumble TD, Int TD, Safety

        # ---- Pass Defense ----

        # ---- Rush Defense ----

        # ==== Special Teams Stats =================================================
        with st.expander("Special Teams"):
            st.write("Stats Here.")

        # ==== Team Summary ========================================================

        # posteam_data = funcs.posteam_data(raw, team_dict[selected_team], game_type_pick)

        # run_pass_data = posteam_data[
        #     (posteam_data.play_type == "run") | (posteam_data.play_type == "pass")
        # ][["yards_gained", "play_type"]]

        # fig = px.histogram(
        #     run_pass_data[run_pass_data.yards_gained != 0],
        #     x="yards_gained",
        #     color="play_type",
        #     barmode="overlay",
        #     title="Distribution of Yards Gained",
        #     color_discrete_sequence=[color1, color2],
        #     labels={"count": "Number of Plays", "yards_gained": "Yards Gained on Play"},
        # )
        # fig.update_layout(legend=dict(y=0.98, x=0.01))
        # # fig.update_layout({"plot_bgcolor": "lightgray"})
        # fig.update_xaxes(showgrid=False)
        # fig.update_yaxes(showgrid=False, rangemode="tozero")

        # st.plotly_chart(fig, use_container_width=True)
