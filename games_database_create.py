import csv
import pandas as pd
import datetime
import os.path
import matplotlib as plt
import numpy as np
import MySQLdb as mdb

#choose years to work with
firstyear = '1985'
lastyear = '2015'
years = int(lastyear)-int(firstyear)


#Converts the date column into a datetime object for easier use
def convert_date(val):
	m, d, y = val.split(' ')
	months = {'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6,
		'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct': 10, 'Nov': 11, 'Dec' : 12}
	m = months[m]
	return datetime.date(int(y),m,int(d))
	
#Extracts rank from winner column
def find_winner_rank(row):
	if row['Winner/Tie'].find('(') == 0:
		ends = row['Winner/Tie'].find(')')
		return row['Winner/Tie'][1:ends]
	else:
		return ''
	
#extracts rank from loser column
def find_loser_rank(row):
	if row['Loser/Tie'].find('(') == 0:
		ends = row['Loser/Tie'].find(')')
		return row['Loser/Tie'][1:ends]
	else:
		return ''
	
#removes the rank from ranked teamnames
def remove_ranks(val):
	if val.find('(') == 0:
		ends = val.find(')')
		val = val[ends+2:]
	return val
	
#finds the hometeam
def find_location(row):
	if pd.notnull(row['WinnerAtLoser']):
		return row['loser']
	else:
		return row['winner']
	
#initialize dataframe with first year's results
games = pd.read_csv('cfb_years_'+firstyear+'-schedule_schedule.csv')
games['WinnerRank'] = games.apply(find_winner_rank, axis=1)
games['LoserRank'] = games.apply(find_loser_rank, axis=1)
games['Winner/Tie'] = games['Winner/Tie'].map(remove_ranks)
games['Loser/Tie'] = games['Loser/Tie'].map(remove_ranks)
games = games[games.Date != 'Date']
games['season'] = int(firstyear)
games['Date'] = games['Date'].map(convert_date)

#append dataframe with all other seasons
for year in range(int(firstyear)+1,int(lastyear)+1):
	filename = 'cfb_years_'+str(year)+'-schedule_schedule.csv'
	nextseason = pd.read_csv(filename)
	nextseason['WinnerRank'] = nextseason.apply(find_winner_rank, axis=1)
	nextseason['LoserRank'] = nextseason.apply(find_loser_rank, axis=1)
	nextseason['Winner/Tie'] = nextseason['Winner/Tie'].map(remove_ranks)
	nextseason['Loser/Tie'] = nextseason['Loser/Tie'].map(remove_ranks)
	nextseason = nextseason[nextseason.Date != 'Date']
	nextseason['season'] = year
	nextseason['Date'] = nextseason['Date'].map(convert_date)
	games = games.append(nextseason, ignore_index=True)
	
#improving formatting
seasons = games.season.unique()
games = games.rename(columns = {'Unnamed: 7':'WinnerAtLoser'})
games = games.rename(columns = {'Winner/Tie':'winner'})
games = games.rename(columns = {'Loser/Tie':'loser'})
games = games.rename(columns = {'Pts':'winnerPts'})
games = games.rename(columns = {'Pts.1':'loserPts'})
games['WinnerAtLoser'] = pd.concat([games['Unnamed: 6'].dropna(), games['WinnerAtLoser'].dropna()]).reindex_like(games)
del games['Unnamed: 6']
games['location'] = games.apply(find_location, axis=1)
del games['Notes']

#create column to sort by team
lostgames = games.copy()
wongames = games.copy()
lostgames['Team'] = lostgames.loser
lostgames['teamwon'] = 0
wongames['Team'] = wongames.winner
wongames['teamwon'] = 1
games2 = wongames.append(lostgames,ignore_index=True)

#standardize teamnames
games2.winner = games2.winner.replace({'William & Mary': 'William and Mary', 
	'North Carolina A&T': 'North Carolina A and T', 
	'Prairie View A&M': 'Prairie View A and M', 
	'Florida A&M': 'Florida A and M', 'West Texas A&M': 'West Texas A and M', 
	'Alabama A&M': 'Alabama A and M', 'Texas A&M': 'Texas A and M', 
	'West Texas A&amp;M': 'West Texas A and M', 
	'Texas A&amp;M': 'Texas A and M', 'Alabama A&amp;M': 'Alabama A and M', 
	'Florida A&amp;M': 'Florida A and M', 
	'Texas A&amp;M-Commerce': 'Texas A and M-Commerce', 
	'Texas A&amp;M-Kingsville': 'Texas A and M-Kingsville', 
	'Prairie View A&amp;M': 'Prairie View A and M', 
	'Cal State Fullerton': 'California State-Fullerton'})
games2.loser = games2.loser.replace({'William & Mary': 'William and Mary', 
	'North Carolina A&T': 'North Carolina A and T', 
	'Prairie View A&M': 'Prairie View A and M', 
	'Florida A&M': 'Florida A and M', 'West Texas A&M': 'West Texas A and M', 
	'Alabama A&M': 'Alabama A and M', 'Texas A&M': 'Texas A and M', 
	'West Texas A&amp;M': 'West Texas A and M', 
	'Texas A&amp;M': 'Texas A and M', 'Alabama A&amp;M': 'Alabama A and M', 
	'Florida A&amp;M': 'Florida A and M', 
	'Texas A&amp;M-Commerce': 'Texas A and M-Commerce', 
	'Texas A&amp;M-Kingsville': 'Texas A and M-Kingsville', 
	'Prairie View A&amp;M': 'Prairie View A and M', 
	'Cal State Fullerton': 'California State-Fullerton'})
games2.Team = games2.Team.replace({'William & Mary': 'William and Mary', 
	'North Carolina A&T': 'North Carolina A and T', 
	'Prairie View A&M': 'Prairie View A and M', 
	'Florida A&M': 'Florida A and M', 'West Texas A&M': 'West Texas A and M', 
	'Alabama A&M': 'Alabama A and M', 'Texas A&M': 'Texas A and M', 
	'West Texas A&amp;M': 'West Texas A and M', 
	'Texas A&amp;M': 'Texas A and M', 'Alabama A&amp;M': 'Alabama A and M', 
	'Florida A&amp;M': 'Florida A and M', 
	'Texas A&amp;M-Commerce': 'Texas A and M-Commerce', 
	'Texas A&amp;M-Kingsville': 'Texas A and M-Kingsville', 
	'Prairie View A&amp;M': 'Prairie View A and M', 
	'Cal State Fullerton': 'California State-Fullerton'})

#remove unnecessary columns
del games2['Date']
del games2['Day']
del games2['LoserRank']
del games2['Rk']
del games2['TV']
del games2['Time']
del games2['WinnerAtLoser']
del games2['WinnerRank']

#save results
games.to_pickle('games.pkl')
load credentials
login = pd.read_pickle('credentials.pkl')
username = login.usernames.ix[0]
password = login.passwords.ix[0]
con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA',
	unix_socket="/tmp/mysql.sock")
games.to_sql(con=con, name='games',if_exists='replace',flavor='mysql')

print 'done!'
