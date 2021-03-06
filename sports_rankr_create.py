import trueskill as ts
import pandas as pd
import numpy as np
import math
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import MySQLdb as mdb
import time
import mpmath

def main():
	mpmath.mp.dps = 1000
	start_time = time.time()
	years = range(1985,2015)
	
	#these parameters values were not varied during optimization
	#initial values for (AP) ranked and unranked teams
	ratedFactor = 30 
	unratedMu = 1 
	unratedSigma = 10 
	ratedSigma = 10 
	beta = 4 
	tau = 0.6 
	unratedRating = 5000 #only used for validation against other metrics
	
	#these parameters were optimized using a truncated Newton algorithm to search
	#8 years were optimized, and each year's values were cross-validated with all other years
	newseasonSigma = 32.038469 
	continuingSigma = 0.0001 
	hometau = 0.0982 
	awaytau = 0.54607 
	diffclose = 9.262603 
	diffblowout = 10.538232 
	
	cols = ['season','Week','Team','RatingMu','RatingSigma','Rating']
	ratingsTable = pd.DataFrame(columns = cols)
	
	ts.setup(mu=unratedMu,sigma=unratedSigma,beta=beta,tau=tau)
	
	#connect to SQL
	login = pd.read_pickle('credentials.pkl')
	username = login.usernames.ix[0]
	password = login.passwords.ix[0]
	con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA',unix_socket="/tmp/mysql.sock")
	
	#create lists that can hold Rating values
	ratings = []
	ratings.append([])
	ratings.append([])
	
	#season DataFrames
	seasonTeams = pd.read_sql_query('select team from games where season = ' + str(years[0]) + ' group by team',con)
	initialSeasonRankings = pd.read_sql_query('select Team, APrank from rankings where Year = ' + str(years[0]) + ' and Week = 0',con)
	
	#initialize preseason values
	for team in seasonTeams:
		ratings[0].append(team)
		try:
			initialRank = initialSeasonRankings[initialSeasonRankings.Team == team].APrank.values
			teamRating = ts.Rating(mu=(ratedFactor/int(initialRank)), sigma = ratedSigma)
		except (ValueError, TypeError):
			teamRating = ts.Rating()
		ratings[1].append(teamRating)
	del initialSeasonRankings
	del seasonTeams
	
	
	def run_season(year,ratings, ratingsTable):
		#initialize parameters
		year = [year]
	
		for year in year:
			year = str(year)
			year_start_time = time.time()
			
			#season DataFrames
			seasonGames = pd.read_sql_query('select Team, Wk from games where season = ' + year,con)
			
			#initializing values
			for team in seasonGames.Team.unique():
				try:
					teamindex = ratings[0].index(team)
					ratings[1][teamindex] = ts.Rating(mu=ratings[1][teamindex].mu,sigma=newseasonSigma)
				except ValueError:
					ratings[0].append(team)
					teamRating = ts.Rating()
					ratings[1].append(teamRating)			
				
			for week in seasonGames.Wk.unique():
				#initialize week
				week_start_time = time.time()
				print 'week ' + str(week)
				week = str(week)
				weekGames = pd.read_sql_query('select winner, loser, winnerPts, loserPts from games where Wk = ' + week + ' and season = ' + year,con)
				weekGames = weekGames.dropna()
				
				for game in weekGames.winner.unique():
					#getting values
					winnerIndex = ratings[0].index(game)
					loserteam = weekGames[weekGames.winner == game].iloc[0].loser
					loserIndex = ratings[0].index(weekGames[weekGames.winner == game].iloc[0].loser)
					winnerRating = ratings[1][winnerIndex]
					loserRating = ratings[1][loserIndex]
					
					#get location
					location = pd.read_sql_query('select location from games where season = ' + str(year) + ' and Wk = ' + str(week) + ' and winner = \'' + str(game) + '\'',con).values[0]
						
					#get points differential
					winnerPts = weekGames[(weekGames.winner == game) & (weekGames.winnerPts != None)].winnerPts.unique()[0]
					loserPts = weekGames[(weekGames.winner == game) & (weekGames.loserPts != None)].loserPts.unique()[0]
					differential = int(winnerPts) - int(loserPts)
					if differential < 3:
						differential = 1
					elif differential < 14:
						differential = diffclose
					else:
						differential = diffblowout
						
					#playing the game
					winnerRating = ts.Rating(mu=winnerRating.mu,sigma=continuingSigma*winnerRating.sigma)
					loserRating = ts.Rating(mu=loserRating.mu,sigma=continuingSigma*loserRating.sigma)
					
					if location == game:
						env = ts.TrueSkill(tau=hometau*differential, backend='mpmath')
					elif location == loserteam:
						env = ts.TrueSkill(tau=awaytau*differential, backend='mpmath')
					else:
						env = ts.TrueSkill(backend='mpmath')
					winnerRating, loserRating = ts.rate_1vs1(winnerRating, loserRating, env=env)
					del location
					del env
					ratings[1][winnerIndex] = winnerRating
					ratings[1][loserIndex] = loserRating
					
				#saving ranking information'
				ratingsmu = []
				ratingssigma = []
				TSrating = []
				for i in range(len(ratings[0])):
					ratingsmu.append(ratings[1][i].mu)
					ratingssigma.append(ratings[1][i].sigma)
					TSrating.append(ratings[1][i].mu - 3*ratings[1][i].sigma)
				data = {'season': year, 'Week': week, 'Team': ratings[0], 'RatingMu': ratingsmu, 'RatingSigma': ratingssigma, 'Rating': TSrating}
				teamRatings = pd.DataFrame(data) #,index=[1])
				teamRatings['Rank'] = len(teamRatings.index)-np.argsort(teamRatings.sort(['Rating'],ascending=False),axis=0).Rating
				ratingsTable = ratingsTable.append(teamRatings,ignore_index=True)
				del teamRatings
						
				print time.time() - week_start_time
			print time.time() - year_start_time
		
		return ratings, ratingsTable
		
	for year in years:
		print 'running year ' + str(year)
		ratings, ratingsTable = run_season(year,ratings,ratingsTable)
		
	#saving results
	ratingsTable.to_pickle('ratingsTable_final.pkl')
	
	print (time.time() - start_time)
	#return (-1*percent)
	
if __name__=='__main__':
	main()