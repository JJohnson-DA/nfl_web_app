import pandas as pd
import streamlit as st
import nfl_data_py as nfl


@st.experimental_memo
def get_raw_pbp(years):
    """
    Returns raw play by play data for years desired.

    params:
        years (int): list of years to get data for. Available years are 1999-2021.
    
    Returns:
        Dataframe containing raw pbp data. Raw data has 372 columns. 
    """

    data = nfl.import_pbp_data(years=years, downcast=False)
    return data


@st.experimental_memo
def get_rosters(years):
    """
    Returns all team rosters for desired years.

    params:
        years (int): list of years to get data for. Available years are 1999-2021.
    
    Returns:
        Dataframe containing roster data. 
    """

    data = nfl.import_rosters(years=years)
    return data


@st.experimental_memo
def get_dc(years):
    """
    Returns teams depth charts for desired years

    params:
        years (int): list of years to get data for. Available years are 1999-2021.
    
    Returns:
        Dataframe containing depth chart data. 
    """
    data = nfl.import_depth_charts(years=years)
    return data


@st.experimental_memo
def get_team_info():
    """
    Use to get team info such as 

    Returns:
        Dataframe with team info such as Name, Abbreviation, conference, division, colors, and urls of team logos
    """
    data = nfl.import_team_desc()
    return data


def team_season_filter(data, team_dict, selected_team, game_type_pick):
    """
    Filters raw data based on selected filters for season, team, and home/away/both
    """
    team_data = data[
        (
            (data["home_team"] == team_dict[selected_team])
            | (data["away_team"] == team_dict[selected_team])
        )
    ]
    return team_data


def posteam_data(raw_data, team, game_type_pick):
    """
    Filters raw data to only include plays where the selected team is on offense.
    """
    data = raw_data[(raw_data.posteam == team)]
    return data


def avg_score(data, team_dict, game_type_pick):
    """
    Returns average score from all NFL teams for the given filters.
    """
    temp = data.copy()
    games = 0
    score = 0
    for team in team_dict.values():
        data = (
            temp[(temp.home_team == team) | (temp.away_team == team)]
            .groupby(["week", "home_team", "away_team"])["home_score", "away_score"]
            .max()
            .reset_index()
        )
        team_score = (
            data[data.home_team == team].home_score.sum()
            + data[data.away_team == team].away_score.sum()
        )
        games += data.shape[0]
        score += team_score
    return round(score / games, 1)


def season_kpis(season_games, team_dict, selected_team):
    """
    Returns wins, losses, avg points, and average points against
    """
    wins = sum(
        (season_games.home_team == team_dict[selected_team])
        & (season_games.home_score > season_games.away_score)
    ) + sum(
        (season_games.away_team == team_dict[selected_team])
        & (season_games.home_score < season_games.away_score)
    )
    losses = sum(
        (season_games.home_team == team_dict[selected_team])
        & (season_games.home_score < season_games.away_score)
    ) + sum(
        (season_games.away_team == team_dict[selected_team])
        & (season_games.home_score > season_games.away_score)
    )
    avg_points = round(
        (
            season_games[
                season_games.home_team == team_dict[selected_team]
            ].home_score.sum()
            + season_games[
                season_games.away_team == team_dict[selected_team]
            ].away_score.sum()
        )
        / season_games.shape[0],
        1,
    )
    avg_points_against = round(
        (
            season_games[
                season_games.home_team == team_dict[selected_team]
            ].away_score.sum()
            + season_games[
                season_games.away_team == team_dict[selected_team]
            ].home_score.sum()
        )
        / season_games.shape[0],
        1,
    )

    return wins, losses, avg_points, avg_points_against


def team_pass_stats(team_data, team_dict, selected_team):
    """
    Returns team passing attempts, comp %, yards, TD, and Int
    """
    data = team_data[team_data.posteam == team_dict[selected_team]]
    pass_attempts = round(data[data.sack == 0].pass_attempt.sum())
    comp_perc = round((data.complete_pass.sum() / pass_attempts) * 100, 1,)
    pass_yards = round(data[data.play_type == "pass"].yards_gained.sum())
    pass_td = round(
        data[(data.play_type == "pass") & (data.touchdown == 1)].touchdown.sum()
    )
    interceptions = round(
        data[(data.play_type == "pass") & (data.interception == 1)].interception.sum()
    )

    return pass_attempts, comp_perc, pass_yards, pass_td, interceptions


def league_avg_pass_stats(raw):
    """
    Returns league passing attempts, comp %, yards, TD, and Int
    """
    data = raw.copy()
    league_pass_attempts = round(
        data[data.sack == 0]
        .groupby("posteam")["pass_attempt"]
        .sum()
        .reset_index()
        .pass_attempt.mean()
    )
    league_comp_perc = round(
        (
            data.groupby("posteam")["complete_pass"]
            .sum()
            .reset_index()
            .complete_pass.mean()
            / league_pass_attempts
        )
        * 100,
        1,
    )
    league_pass_yards = round(
        data[data.play_type == "pass"]
        .groupby("posteam")["yards_gained"]
        .sum()
        .reset_index()
        .yards_gained.mean()
    )
    league_pass_td = round(
        data[(data.play_type == "pass") & (data.touchdown == 1)]
        .groupby("posteam")["touchdown"]
        .sum()
        .reset_index()
        .touchdown.mean()
    )
    league_interceptions = round(
        data[(data.play_type == "pass") & (data.interception == 1)]
        .groupby("posteam")["interception"]
        .sum()
        .reset_index()
        .interception.mean()
    )
    return (
        league_pass_attempts,
        league_comp_perc,
        league_pass_yards,
        league_pass_td,
        league_interceptions,
    )

