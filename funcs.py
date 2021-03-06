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


def team_season_filter(data, team_abb):
    """
    Filters raw data based on selected filters for season, team, and home/away/both
    """
    team_data = data[
        ((data["home_team"] == team_abb) | (data["away_team"] == team_abb))
    ]
    return team_data


def posteam_data(raw_data, team):
    """
    Filters raw data to only include plays where the selected team is on offense.
    """
    data = raw_data[(raw_data.posteam == team)]
    return data


def season_kpis(season_games, team_abb):
    """
    Returns wins, losses, avg points, and average points against
    """
    wins = sum(
        (season_games.home_team == team_abb)
        & (season_games.home_score > season_games.away_score)
    ) + sum(
        (season_games.away_team == team_abb)
        & (season_games.home_score < season_games.away_score)
    )
    losses = sum(
        (season_games.home_team == team_abb)
        & (season_games.home_score < season_games.away_score)
    ) + sum(
        (season_games.away_team == team_abb)
        & (season_games.home_score > season_games.away_score)
    )
    avg_points = round(
        (
            season_games[season_games.home_team == team_abb].home_score.sum()
            + season_games[season_games.away_team == team_abb].away_score.sum()
        )
        / season_games.shape[0],
        1,
    )
    avg_points_against = round(
        (
            season_games[season_games.home_team == team_abb].away_score.sum()
            + season_games[season_games.away_team == team_abb].home_score.sum()
        )
        / season_games.shape[0],
        1,
    )

    return wins, losses, avg_points, avg_points_against


def avg_score(data, team_dict, comparison):
    """
    Returns average score from all NFL teams for the given filters.
    """
    temp = data.copy()
    if comparison == "All NFL":
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
        return round(score / games, 1), round(score / games, 1)
    else:
        team = team_dict[comparison]
        data = data[((data["home_team"] == team) | (data["away_team"] == team))]
        avg_points = round(
            (
                data[data.home_team == team].home_score.sum()
                + data[data.away_team == team].away_score.sum()
            )
            / data.shape[0],
            1,
        )
        avg_points_against = round(
            (
                data[data.home_team == team].away_score.sum()
                + data[data.away_team == team].home_score.sum()
            )
            / data.shape[0],
            1,
        )
        return avg_points, avg_points_against


def team_pass_stats(team_data, team_abb):
    """
    Returns team passing attempts, comp %, yards, TD, and Int
    """
    data = team_data[team_data.posteam == team_abb]
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


def team_rec_stats(team_data, team_abb):
    """
    Returns team receptions, avg pass length, yds/rec, and rec td
    """
    # Data Adjustments
    data = team_data[team_data.posteam == team_abb]
    data["pass_length"] = data.yards_gained - data.yards_after_catch
    # Metrics
    receptions = round(data.complete_pass.sum())
    avg_rec_yds = round(data[data.complete_pass == 1].yards_gained.mean(), 1)
    avg_pass_length = round(data[data.complete_pass == 1].pass_length.mean(), 1)
    yds_after_catch = round(data[data.complete_pass == 1].yards_after_catch.mean(), 1)
    rec_td = round(data[data.complete_pass == 1].touchdown.sum())

    return receptions, avg_rec_yds, avg_pass_length, yds_after_catch, rec_td


def league_avg_rec_stats(raw):
    """
    Returns league receptions, avg pass length, yds/rec, and rec td
    """
    # Data Adjustments
    data = raw.copy()
    data["pass_length"] = data.yards_gained - data.yards_after_catch
    # Metrics
    league_receptions = round(
        data.groupby("posteam")["complete_pass"]
        .sum()
        .reset_index()
        .complete_pass.mean()
    )
    league_pass_length = round(data[data.play_type == "pass"].pass_length.mean(), 1)
    league_rec_yards = round(data[data.complete_pass == 1].yards_gained.mean(), 1)
    league_yds_after_catch = round(
        data[data.complete_pass == 1].yards_after_catch.mean(), 1
    )
    league_rec_td = round(
        data[data.complete_pass == 1]
        .groupby("posteam")["touchdown"]
        .sum()
        .reset_index()
        .touchdown.mean()
    )
    return (
        league_receptions,
        league_rec_yards,
        league_pass_length,
        league_yds_after_catch,
        league_rec_td,
    )


def team_rush_stats(team_data, team_abb):
    """
    Returns team rushes, yds/rush, total rush yards, and rushing TD
    """
    # Data Adjustments
    data = team_data[team_data.posteam == team_abb]
    # Metrics
    rushes = round(data.rush_attempt.sum())
    avg_rush_length = round(data[data.rush_attempt == 1].yards_gained.mean(), 1)
    rush_yards = round(data[data.rush_attempt == 1].yards_gained.sum())
    rush_td = round(data[data.rush_attempt == 1].touchdown.sum())

    return rushes, avg_rush_length, rush_yards, rush_td


def league_avg_rush_stats(raw):
    """
    Returns league receptions, avg pass length, yds/rec, and rec td
    """
    # Data Adjustments
    data = raw.copy()
    # Metrics
    league_rushes = round(
        data.groupby("posteam")["rush_attempt"].sum().reset_index().rush_attempt.mean()
    )
    league_rush_length = round(data[data.rush_attempt == 1].yards_gained.mean(), 1)
    league_rush_yards = round(
        data[data.rush_attempt == 1]
        .groupby("posteam")["yards_gained"]
        .sum()
        .reset_index()
        .yards_gained.mean()
    )
    league_rush_td = round(
        data[data.rush_attempt == 1]
        .groupby("posteam")["touchdown"]
        .sum()
        .reset_index()
        .touchdown.mean()
    )
    return (
        league_rushes,
        league_rush_length,
        league_rush_yards,
        league_rush_td,
    )


def team_def_stats(def_data):
    data = def_data.copy()
    df = pd.DataFrame()
    # tackles
    df.loc[0, "tackles"] = round(data.assist_tackle.sum() + data.solo_tackle.sum())
    # sacks
    df["sacks"] = round(data.sack.sum())
    # yards allowed
    df["yds_allowed"] = round(data.yards_gained.sum())
    # Turnovers
    df["turnovers"] = round(data.interception.sum() + data.fumble_lost.sum())
    # TD
    df["td"] = round(data[data.td_team == data.defteam].shape[0])
    # tackles for loss
    df["tfl"] = data[
        ((data.solo_tackle == 1) | (data.assist_tackle == 1)) & (data.yards_gained < 0)
    ].shape[0]
    # sacks/game
    df["sacks_per_game"] = round(data.groupby("week")["sack"].sum().mean(), 1)
    # yards given/game
    df["yds_given_per_game"] = round(data.groupby("week")["yards_gained"].sum().mean())
    # 3rd down stop % (third_down_failed, third_down_converted)
    df["third_perc"] = round(data[data.down == 3].third_down_failed.mean() * 100, 1)
    # goal line stands
    df["gl_stand_perc"] = round(
        (
            1
            - data[data.goal_to_go == 1]
            .groupby(["week", "drive"])["touchdown"]
            .sum()
            .mean()
        )
        * 100,
        1,
    )

    return df


def league_def_stats(data):
    data = data.copy()
    data["total_tackles"] = data.solo_tackle + data.assist_tackle
    data["total_turnovers"] = data.interception + data.fumble_lost
    grouped = data.groupby(["defteam"])
    df = pd.DataFrame()
    # tackles
    df.loc[0, "tackles"] = round(grouped.total_tackles.sum().mean())
    # sacks
    df["sacks"] = round(grouped.sack.sum().mean())
    # yards allowed
    df["yds_allowed"] = round(grouped.yards_gained.sum().mean())
    # Turnovers
    df["turnovers"] = round(grouped.total_turnovers.sum().mean())
    # TD
    df["td"] = round(
        data[data.td_team == data.defteam].groupby("defteam").size().mean(), 1
    )
    # tackles for loss
    df["tfl"] = round(
        data[
            ((data.solo_tackle == 1) | (data.assist_tackle == 1))
            & (data.yards_gained < 0)
        ]
        .groupby("defteam")
        .size()
        .mean()
    )
    # sacks/game
    df["sacks_per_game"] = round(
        data.groupby(["defteam", "week"])["sack"].sum().mean(), 1
    )
    # yards given/game
    df["yds_given_per_game"] = round(
        data.groupby(["defteam", "week"])["yards_gained"].sum().mean()
    )
    # 3rd down stop % (third_down_failed, third_down_converted)
    df["third_perc"] = round(
        data[data.down == 3].groupby("defteam")["third_down_failed"].mean().mean()
        * 100,
        1,
    )

    # goal line stands
    df["gl_stand_perc"] = round(
        (
            1
            - data[data.goal_to_go == 1]
            .groupby(["defteam", "week", "drive"])["touchdown"]
            .sum()
            .reset_index()
            .groupby("defteam")["touchdown"]
            .mean()
            .mean()
        )
        * 100,
        1,
    )

    return df


def get_qb_stats(data):
    data = data.copy()
    # Pass Yds
    pass_yds = round(data[data.complete_pass == 1].yards_gained.sum())
    # Yds/Att
    yds_per_att = round(pass_yds / data[data.sack == 0].shape[0], 1)
    # Att
    att = data.shape[0]
    # Completions
    comp = data[data.complete_pass == 1].shape[0]
    # Cmp %
    comp_perc = round((comp / att) * 100, 1)
    # TD
    td = round(data.pass_touchdown.sum())
    # INT
    interceptions = round(data.interception.sum())
    # 20+ yards
    over_20 = data[(data.yards_gained >= 20) & (data.sack == 0)].shape[0]
    # 40+ yards
    over_40 = data[(data.yards_gained >= 40) & (data.sack == 0)].shape[0]
    # Longest pass
    long_pass = round(data.yards_gained.max())
    # Sacks
    sacks = round(data.sack.sum())
    # Sack yards
    sack_yards = round(data[data.sack == 1].yards_gained.sum())

    return (
        pass_yds,
        yds_per_att,
        att,
        comp,
        comp_perc,
        td,
        interceptions,
        over_20,
        over_40,
        long_pass,
        sacks,
        sack_yards,
    )

