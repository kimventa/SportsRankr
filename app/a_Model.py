def ModelIt(fromUser = 'Default',population=0):
	print 'The population is %i' % population
	result = population/1000000.0
	if fromUser != 'Default':
		return result
	else:
		return 'check your input'
		
def fix_teamname(team):
	universityOf = team.lower().find('university of')
	university = team.lower().find(' university')
	#technology = team.lower().find('technology')
	#amper = team.find('&')
	if universityOf != -1:
		team = team[14:]
	if university != -1:
		team = team[:-11]
	#if technology != -1:
	#	team.replace('technology','Tech')
	#if amper != -1:
	#	team.replace('&','and')
	return team

def ScheduleStrength(fromUser = 'Default'):
	print 'first line of ScheduleStrength'
	import pandas as pd
	import MySQLdb as mdb
	import numpy as np

	login = pd.read_pickle('credentials.pkl')
	username = login.usernames.ix[0]
	password = login.passwords.ix[0]

	#db = mdb.connect(user=username,host="localhost",password=password,db="NCAA",charset='utf8')

	season = 2015
	week = 5
	team = fromUser
	team = fix_teamname(team)
	print 'schedule strength queries begin'
	#with db:
	#	cur = db.cursor()
	#	print 'just before first cur'
	#	print cur
	#	curtext = "select * from games where season = " + str(season) + " and Team = '" + team + "';"
	#	print curtext
	#	cur.execute(curtext)
	#	print 'first cur executed'
	#	teamseasongames = cur.fetchall()
		#print teamseasongames
	con = mdb.connect(host='localhost',user=username, passwd=password,db='NCAA')
	print 'started con, now doing 1st query...'
	teamseasongames = pd.read_sql_query('select * from currentgames where season = ' + str(season) + ' and Team = \'' + str(team) + '\'',con)
	print teamseasongames
	if len(teamseasongames) == 0:
		print 'not found'
		team = pd.read_sql_query("select team from acronyms where acronym = '%s';" % team,con)
		team =  team.ix[0][0]
		teamseasongames = pd.read_sql_query('select * from currentgames where season = ' + str(season) + ' and Team = \'' + str(team) + '\'',con)
		print teamseasongames
	print 'second query'
	teamratingquery = 'select Rating from finalratings5 where Team = \'' + str(team) + '\' and Week = ' + str(week)
	teamrating = pd.read_sql_query(teamratingquery,con)#.values[0]
	print 'queries end'
	opponents = []
	for index in teamseasongames.index:
		loser = teamseasongames.loser[index]
		if loser != team:
			opponents.append(loser)
		else:
			opponents.append(teamseasongames.winner[index])
	print 'getting opponent ratings'
	opponentratings = []
	for opponent in opponents:
		ratingValue = pd.read_sql_query('select Rating from finalratings5 where Team = \'' + str(opponent) + '\' and Week = ' + str(week),con).values[0]
		opponentratings.append(ratingValue)
	opponentrating = 100 * (1+(np.average(opponentratings)/5.7))
	print 'last line of ScheduleStrength'
	return '%.2f' % opponentrating
