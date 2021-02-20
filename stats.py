# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:25:04 2021

@author: Joacim
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#returns dataset with all matches that a team has played, with an additional 
#match_won column consisting of 1(win) or 0(loss)
def getTeam(s):
    temp = results.loc[results['team_1']==s]
    temp = temp.append(results.loc[results['team_2']==s], ignore_index=True)
    temp = temp.sort_values(by=['date'],ascending=False)
    temp['match_won'] = getMatchWinner(temp,s)
    return temp  

#returns a numpy array with wins and loss stats
def getMatchWinner(df, team_name):
    k = df.to_numpy()
    index = df.index
    number_of_rows = len(index)
    winner =  np.empty(number_of_rows, dtype=object) 
    counter = 0
    for row in k:
        if k[counter][18]==1 and k[counter][1]==team_name:
            winner[counter] = 1
        elif k[counter][18]==2 and k[counter][2]==team_name:
            winner[counter] = 1
        else:
            winner[counter] = 0
        counter+=1
    return winner

#returns a dataframe with player rating, team rating, match id and win/loss for the match
def playerVsRest(team, player, match_ids, team_result):
    index = player.index
    number_of_rows = len(index)
    player_rating =  np.empty(number_of_rows, dtype=float) 
    team_rating = np.empty(number_of_rows, dtype=float) 
    match_winner = np.empty(number_of_rows, dtype=float) 
    for i in range(number_of_rows):
        player_rating[i] = player.loc[player['match_id']==match_ids[i]].rating.to_numpy()
        team_rating[i] = (np.sum(team.loc[team['match_id']==match_ids[i]].rating.to_numpy())- player_rating[i])/4
        temp = team_result.loc[team_result['match_id']==match_ids[i]].match_won.to_numpy()
        if temp.size!=0:
            match_winner[i] = temp[0]     
    return pd.DataFrame({'Player': player_rating,'Team':team_rating, 'Match ID':match_ids, 'match_won':match_winner})   

#plots a the rating comparison
def plot(df, player_name, team_name):
    w = df.loc[df['match_won']==1]
    l = df[~df.isin(w)]
    l = l.dropna()

    x1 = w.Player
    y1 = w.Team
    x2 = l.Player
    y2 = l.Team

    fig, ax = plt.subplots()

    ax.plot(x1, y1, 'o', color='green',label='Win', markersize=2);
    ax.plot(x2, y2, 'o', color='red',label='Loss', markersize=2);
    ax.set_xlabel(player_name+" rating")
    ax.set_ylabel(team_name+" rating")
    legend = ax.legend(loc='upper left', shadow=False, fontsize='small')
    plt.xlim([0, 2.5])
    plt.ylim([0, 2.5])
    plt.show()

#returns all players who's played in the team sometime during the established time frame
def getPlayers(team_name):
    return players.loc[players['team']==team_name]

#returns a dataframe consisting of all data of the player from players.csv
def getCarryPlayer(player_name, team):
    return team.loc[team['player_name']==player_name]

def barChart(player_average, player_names, team_name):
    
    x = np.arange(len(player_names))  # the label locations
    width = 0.9  # the width of the bars
    
    fig, ax = plt.subplots()
    barchart = ax.bar(x, player_average, width, label=team_name)
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Rating')
    ax.set_title('Player ratings')
    ax.set_xticks(x)
    ax.set_xticklabels(player_names)
    ax.legend()
    axes = plt.gca()
    axes.set_ylim([0.8,1.6])
    
    fig.tight_layout()
    
    plt.show()  
#data downloaded from https://www.kaggle.com/mateusdmachado/csgo-professional-matches
#since roster moves are so frequent in csgo I decided to only check data between 2018-2020
#loading map results
results = pd.read_csv('archive/results.csv')
mask = (results['date'] > '2018-01-01') & (results['date'] <= '2020-03-18')
results = results.loc[mask]

#loading player stats
players = pd.read_csv('archive/players.csv')
mask = (players['date'] > '2018-01-01') & (players['date'] <= '2020-03-18')
players = players.loc[mask]

#top 8 teams 2019, to get players from other teams just add or replace in top_teams
top_teams = ["Natus Vincere" ,"Vitality" ,"Astralis","Liquid", "fnatic","mousesports","ENCE","FaZe"]
ta = []
pa = []
pn = []
for i in range(len(top_teams)):
    #a team consists of 5 players, this makes sure that the five players selected are the most recent ones 
    player_names = getPlayers(top_teams[i]).head(5).player_name.to_numpy()
    team_name = top_teams[i]
    for j in range(5):
        player_name = player_names[j]
        _players = getPlayers(team_name)
        _player = getCarryPlayer(player_name,getPlayers(team_name))
        result = playerVsRest(_players,_player,_player.match_id.to_numpy(),getTeam(team_name))
        player_average = np.average(result.Player.to_numpy())
        team_average = np.average(result.Team.to_numpy())
        ta.append(team_average)
        pa.append(player_average)
        pn.append(player_name)
        #get a plot for each individual player vs team
        #plot(result, player_name, team_name)

#bar chart comparing all players in a team
for i in range(len(top_teams)):
    team_name = top_teams[i]
    barChart(pa[(5*i):(5*(i+1))],pn[(5*i):(5*(i+1))], team_name)

#plots a rating comparison between all players from the selected teams
fig, ax = plt.subplots()
ax.set_xlabel("Player rating")
ax.set_ylabel("Team rating")
ax.scatter(pa,ta, s=2)
plt.xlim([0.9, 1.4])
plt.ylim([0.9, 1.4])
for i, txt in enumerate(pn):
    ax.annotate(txt, (pa[i], ta[i]), size='x-small')
plt.show()