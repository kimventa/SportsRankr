import pandas as pd
import MySQLdb as mdb


def validate_algorithm(year):
	
	#initialize variables
	year = int(year)
	unratedRating = 5000 #rating given to unrated teams
	BILright = 0 #Billingsley
	BILgames = 0
	COLright = 0 #Colley
	COLgames = 0
	MASright = 0 #Massey
	MASgames = 0
	SAGright = 0 #Sagarin
	SAGgames = 0
	WOLright = 0 #Wolfe
	WOLgames = 0
	AHright = 0 #Anderson & Hester
	AHgames = 0
	Coachright = 0 #Coaches' Poll
	Coachgames = 0
	APright = 0 #Associated Press Poll
	APgames = 0
	
	#connect to SQL
	login = pd.read_pickle('credentials.pkl')
	username = login.usernames.ix[0]
	password = login.passwords.ix[0]
	con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA',
		unix_socket="/tmp/mysql.sock")
		
		
	#season DataFrames
	seasonGames = pd.read_sql_query('select Team, Wk from games where season = ' + str(year),con)

	#for each week in the season, run all games to get percent correct
	for week in seasonGames.Wk.unique():
		weekGames = pd.read_sql_query('select winner, loser, winnerPts, loserPts from games where Wk = ' + week + ' and season = ' + str(year),con)
		weekGames = weekGames.dropna()
		
		#get the rank of a team
		def findRank(metric,NCAAtable,year,week,team):
			teamRank = pd.read_sql_query('select ' + metric + ' from ' + NCAAtable + ' where season = ' + str(year) + ' and Week = ' + str(week) + ' and team = \'' + str(team) + '\'',con).values
			if len(teamRank) == 0:
				teamRank = unratedRating
			elif teamRank[0][0] == None:
				teamRank = unratedRating
			elif type(teamRank[0][0]) == str:
				teamRank = int(teamRank[0][0])
			teamRank = int(teamRank)
			return teamRank
						
		#determine whether a game was guessed correctly
		def validate_game(system,NCAAtable,year,week,game,loserteam,right,games):
			winnerRank = findRank(system,NCAAtable,year,week,game)
			loserRank = findRank(system,NCAAtable,year,week,loserteam)
			if winnerRank < loserRank:
				right += 1
				games += 1
			elif winnerRank > loserRank:
				games += 1
			return right, games
		
		for winner in weekGames.winner.unique():
			loser = weekGames[weekGames.winner == winner].iloc[0].loser
					
			#validate each algorithm
			BILright, BILgames = validate_game('BIL','algorithmRankings',year,
				week,winner,loser,BILright,BILgames)
			COLright, COLgames = validate_game('COL','algorithmRankings',year,
				week,winner,loser,COLright,COLgames)
			MASright, MASgames = validate_game('MAS','algorithmRankings',year,
				week,winner,loser,MASright,MASgames)
			SAGright, SAGgames = validate_game('SAG','algorithmRankings',year,
				week,winner,loser,SAGright,SAGgames)
			WOLright, WOLgames = validate_game('WOL','algorithmRankings',year,
				week,winner,loser,WOLright,WOLgames)
			AHright, AHgames = validate_game('AandHRank','algorithmRankings',
				year,week,winner,loser,AHright,AHgames)
						
			#validate each poll
			Coachright, Coachgames = validate_game('CoachRank','combinedRankings',
				year,week,winner,loser,Coachright,Coachgames)
			APright, APgames = validate_game('APRank','combinedRankings',
				year,week,winner,loser,APright,APgames)
	
	#output results
	print 'BIL: ' + str(BILright*100./BILgames)
	print 'COL: ' + str(COLright*100./COLgames)
	print 'MAS: ' + str(MASright*100./MASgames)
	print 'SAG: ' + str(SAGright*100./SAGgames)
	print 'WOL: ' + str(WOLright*100./WOLgames)
	print 'AH: ' + str(AHright*100./AHgames)
	print 'Coach: ' + str(Coachright*100./Coachgames)
	print 'AP: ' + str(APright*100./APgames)
						
main(2014)