import csv
import pandas as pd
import datetime
import os.path
import matplotlib as plt
import numpy as np
import MySQLdb as mdb

#import the Rankings file
rankings = pd.read_csv('Rankings 1998-2010.csv')

#change the column names to nicer, more SQL-friendly versions
rankings = rankings.rename(columns = {'w': 'wToNow'})
rankings = rankings.rename(columns = {'l': 'lToNow'})
rankings = rankings.rename(columns = {'W': 'seasonWins'})
rankings = rankings.rename(columns = {'L': 'seasonLosses'})
rankings = rankings.rename(columns = {'AP rank': 'APrank'})
rankings = rankings.rename(columns = {'AP votes': 'APvotes'})
rankings = rankings.rename(columns = {'AP 1st place votes': 'AP1stVotes'})
rankings = rankings.rename(columns = {'Coaches rank': 'coachesRank'})
rankings = rankings.rename(columns = {'Coaches votes': 'coachesVotes'})
rankings = rankings.rename(columns = {'Coaches 1st place votes': 'coaches1stVotes'})
rankings = rankings.rename(columns = {'Harris rank': 'HarrisRank'})
rankings = rankings.rename(columns = {'Harris votes': 'HarrisVotes'})
rankings = rankings.rename(columns = {'Harris 1st place votes': 'Harris1stVotes'})
rankings = rankings.rename(columns = {'Team Alt Name': 'altName'})


#Change names to match other tables
rankings.Conf = rankings.Conf.replace({'SunBelt': 'Sun Belt', 
	'Big10': 'Big Ten', 'Big12': 'Big 12', 'Pac10': 'Pac-10', 
	'Indy': 'Independent', 'MtnWest': 'Mountain West', 'BigEast': 'Big East'})
rankings.Team = rankings.Team.replace({'W Michigan': 'Western Michigan',
	'E Carolina': 'East Carolina', 'E Michigan': 'Eastern Michigan', 
	'N Carolina': 'North Carolina', 'N Illinois': 'Northern Illinois', 
	'S Carolina': 'South Carolina', 'S Florida': 'South Florida', 
	'N Texas': 'North Texas', 'C Michigan': 'Central Michigan', 
	'W Virginia': 'West Virginia', 'W Kentucky': 'Western Kentucky', 
	'Ohio St': 'Ohio State', 'Oklahoma St': 'Oklahoma State', 
	'Iowa St': 'Iowa State', 'Kansas St': 'Kansas State', 
	'Penn St': 'Penn State', 'San Diego St': 'San Diego State', 
	'San Jose St': 'San Jose State', 'Arizona St': 'Arizona State', 
	'Arkansas St': 'Arkansas State', 'Ball St': 'Ball State', 
	'Boise St': 'Boise State', 'Boston Coll': 'Boston College', 
	'Bowl Green': 'Bowling Green State', 'Colorado St': 'Colorado State', 
	'Florida Atl': 'Florida Atlantic', 'Florida St': 'Florida State', 
	'Florida Intl': 'Florida International', 'Fresno St': 'Fresno State', 
	'Utah St': 'Utah State', 'Wash St': 'Washington State', 
	'VA Tech': 'Virginia Tech', 'Michigan St': 'Michigan State', 
	'GA Tech': 'Georgia Tech', 'New Mex St': 'New Mexico State', 
	'Oregon St': 'Oregon State', 'Miss St': 'Mississippi State', 
	'Kent': 'Kent State', 'S Miss': 'Southern Mississippi', 
	'USC': 'Southern California', 'UConn': 'Connecticut', 
	'LA Tech': 'Louisiana Tech', 'SMU': 'Southern Methodist', 
	'TCU': 'Texas Christian', 'BYU': 'Brigham Young', 
	'UNLV': 'Nevada-Las Vegas', 'NC State': 'North Carolina State', 
	'LA-Lafayette': 'Louisiana-Lafayette', 'LA-Monroe': 'Louisiana-Monroe', 
	'LSU': 'Louisiana State', 'Mid Tenn St': 'Middle Tennessee State', 
	'UTEP': 'Texas-El Paso', 'UAB': 'Alabama-Birmingham', 
	'UCF': 'Central Florida', 'Texas A&M': 'Texas A and M'})

#save as a pickle
rankings.to_pickle('rankings.pkl')

#save as a dataframe
#load credentials
login = pd.read_pickle('credentials.pkl')
username = login.usernames.ix[0]
password = login.passwords.ix[0]

con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA', unix_socket="/tmp/mysql.sock")
rankings.to_sql(con=con, name='rankings', if_exists='replace',flavor='mysql')

print 'done!'