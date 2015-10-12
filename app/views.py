from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ScheduleStrength, fix_teamname
import pandas as pd
from operator import itemgetter
import numpy as np
import scipy.stats


#login = pd.read_pickle('credentials.pkl')
#username = login.usernames.ix[0]
#password = login.passwords.ix[0]
#db = mdb.connect(user = username, host = "localhost", password = password, db = "NCAA", charset = 'utf8')
	
@app.route('/')
@app.route('/index')
def homepage():
	print 'first line of homepage in views.py'
	
	login = pd.read_pickle('credentials.pkl')
	username = login.usernames.ix[0]
	password = login.passwords.ix[0]
	db = mdb.connect(user = username, host = "localhost", password = password, db = "NCAA", charset = 'utf8')
	
	with db:
		cur = db.cursor()
		cur.execute("select Team from D1A group by Team")
		query_results = cur.fetchall()
		D1A = '('
		for query in query_results:
			D1A += '\'' + str(query[0]) + '\', '
		D1A = D1A[:-2]
		D1A += ')'
		cur.execute("select Team, Rating, Rank from finalratings5 where season = '2015' and week = '5' and Team in " + D1A + " order by Rating desc;")
		query_results = cur.fetchall()
	teams = []
	for result in query_results:
		rating='%.2f' % result[1]
		myquery = "select APRank, CoachRank from polls5 where Team = \'" + result[0] + "\';"
		rankingResults = ()
		cur.execute(myquery)
		rankingResults = cur.fetchall()
		if len(rankingResults) < 1:
			#print 'empty'
			APrank = ' '
			Coachrank = ' '
		else:
			for rank in rankingResults:
				#print rankingResults[0], rankingResults[1]
				if rank[0] != None:
					APrank = rank[0]
				else:
					APrank = ' '
				if rank[1] != None:
					Coachrank = rank[1]
				else:
					Coachrank = ' '
				
		teams.append(dict(name=result[0], rating=rating, rank=int(result[2]), APrank = APrank, Coachrank = Coachrank))
	return render_template('teams.html', teams=teams)
	
@app.route('/about')
def about():
	return render_template('about.html')
	
@app.route('/contact')
def contact():
	return render_template('contact.html')
	
@app.route('/error')
def noteam():
	return render_template('error.html')
	
@app.route('/output')
def team_output():
        print 'first line of team_output in views.py'
	#pull 'ID' from input field and store it
	team = request.args.get('ID')
	team = fix_teamname(team)
	
	login = pd.read_pickle('credentials.pkl')
	username = login.usernames.ix[0]
	password = login.passwords.ix[0]
	db = mdb.connect(user = username, password = password, db = "NCAA", charset = 'utf8')
	
	
	with db:
                print 'start of sql queries'
		cur = db.cursor()
		#just select the team that the user inputs
		cur.execute("select Team, Rating, Rank from finalratings5 where Team = '%s' and Week = '5' and season = 2015;" % team)
		query_results = cur.fetchall()
		if len(query_results) == 0:
			print 'not found'
			cur.execute("select team from acronyms where acronym = '%s';" % team)
			nickname = cur.fetchall()
			print nickname[0][0]
			cur.execute("select Team, Rating, Rank from finalratings5 where Team = '%s' and Week = '5' and season = 2015;" % nickname[0][0])
			query_results = cur.fetchall()
			teamname = nickname[0][0]
			team = nickname[0][0]
			
		cur.execute("select winner, winnerPts, loser, loserPts, Wk from currentgames where Team = '%s' and season = 2015 order by Wk;" % team)
		schedule = cur.fetchall()
		print 'end of first queries'
	teams = []
	for result in query_results:
		print 'Rating is...'
		Rating = '%.2f' %result[1]
		print Rating
		Rank = '%.0f' %result[2]
		teams.append(dict(Team=result[0], Rating=Rating, Rank=Rank))
		teamname = result[0]
		
        print 'finished appending teams'
	games = []
	
	rating='%.2f' % result[1]
	
	if 'nickname' in locals():
		teamname = nickname[0][0]
	else:
		teamname = result[0]
	teamname = str(teamname)
	print 'next queries starting...'
	cur.execute("select RatingMu, RatingSigma from finalratings5 where season = 2015 and Week = '5' and team = '%s';" % teamname)
	teamRating = cur.fetchall()
	teamMu = teamRating[0][0]		
	teamSigma = teamRating[0][1]
	print 'retrieved schedule'
	for result in schedule:
		print 'getting opponents'
		if result[0] != teamname:
			opponent = result[0]
			pointsfor = result[3]
			pointsagainst = result[1]
		else:
			opponent = result[2]
			pointsfor = result[1]
			pointsagainst = result[3]
		print 'getting probabilities' 
		if pointsfor == 'None' and pointsagainst == 'None':
			cur.execute("select RatingMu, RatingSigma from finalratings5 where season = 2015 and Week = '5' and team = '%s';" % opponent)
			opponentRating = cur.fetchall()
			opponentMu = opponentRating[0][0]
			opponentSigma = opponentRating[0][1]
			
			gameMu = opponentMu - teamMu
			gameSigma = 10000*np.sqrt(opponentSigma*opponentSigma + teamSigma*teamSigma - 2*opponentSigma*teamSigma)
		
			prob = 100*scipy.stats.norm(gameMu,gameSigma).cdf(0)
			prob ='%.1f' % prob
			prob = prob+'%'
			pointsfor = prob
			pointsagainst = opponentMu - 3*opponentSigma
			pointsagainst = '%.2f' % pointsagainst
		print 'finalizing games'
		games.append(dict(pointsfor=pointsfor, opponent=opponent, pointsagainst=pointsagainst, week=int(result[4])))
		games = sorted(games, key=itemgetter('week'))
	print 'games finalized'
	gamesplayed = []
	futuregames = []
	for game in games:
		print game
		if game['pointsfor'].find('%') != -1:
			gamesplayed.append(game)
		else:
			futuregames.append(game)
	print len(teams)
	print len(games)
	print gamesplayed
	print futuregames
	#call a function from a_Model package. note we are only pulling one result in the query
	pop_input = teams[0]['Rating']
	the_result = ScheduleStrength(team)
	print the_result
	print 'finished views.py section!'
	return render_template("output.html", teams=teams, the_result = the_result, gamesplayed=gamesplayed, futuregames=futuregames)
