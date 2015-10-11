import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import MySQLdb as mdb

#connect to website
soup = BeautifulSoup(urllib2.urlopen('http://espn.go.com/college-football/rankings').read(),'lxml')

#initialize dataframe
cols = ['Team','season','Week','Rank','Pts']
currentAPRankings = pd.DataFrame(columns = cols)
currentCoachRankings = pd.DataFrame(columns = cols)
combinedRankings = pd.read_pickle('combinedRankings.pkl')

#get season and week
season = soup('button',
	{'class': 'button-filter med dropdown-toggle'})[2].string
week = int(soup('button',
	{'class': 'button-filter med dropdown-toggle'})[3].string.split(' ')[1])-1
print season, week

#get rankings
for row in soup('table',{'class': 'rankings has-team-logos'})[0].tbody('tr'):
	tds = row('td')
	start = str(tds[1]).find('abbr title=\"')
	cutBefore = str(tds[1])[start+12:]
	end = cutBefore.find('\"')
	team = cutBefore[:end]
	if tds[0].string == None:
		print 'None'
		rank = currentAPRankings.APRank.astype('int').max()
	else:
		rank = tds[0].string
	data = {'Team': unicode(team), 'season': unicode(season), 'Week': unicode(week), 'APRank': unicode(rank), 'APPts': unicode(tds[3].string)}
	teamrow = pd.DataFrame(data,index=[1])
	currentAPRankings = currentAPRankings.append(teamrow,ignore_index=True)
	
for row in soup('table',{'class': 'rankings has-team-logos'})[1].tbody('tr'):
	tds = row('td')
	start = str(tds[1]).find('abbr title=\"')
	cutBefore = str(tds[1])[start+12:]
	end = cutBefore.find('\"')
	team = cutBefore[:end]
	
	if tds[0].string == None:
		print 'None'
		rank = currentCoachRankings.CoachRank.astype('int').max()
		print rank
	else:
		rank = tds[0].string
	data = {'Team': unicode(team), 'season': unicode(season), 
		'Week': unicode(week), 'CoachRank': unicode(rank), 
		'CoachPts': unicode(tds[3].string)}
	teamrow = pd.DataFrame(data,index=[1])
	currentCoachRankings = currentCoachRankings.append(teamrow,ignore_index=True)
	
rankings = pd.read_pickle('ratingsTable.pkl')
combinedRankings2 = currentCoachRankings.merge(currentAPRankings,how='outer')
combinedRankings2.Team = combinedRankings2.Team.replace({'Texas A&amp;M': 'Texas A and M', 
	'TCU': 'Texas Christian', 'LSU': 'Louisiana State', 
	'USC': 'Southern California', 'Ole Miss': 'Mississippi'})

combinedRankings = combinedRankings.append(combinedRankings2,ignore_index=True)

print combinedRankings[combinedRankings.Week == '5']
combinedRankings.to_pickle('combinedRankings5.pkl')

login = pd.read_pickle('credentials.pkl')
username = login.usernames.ix[0]
password = login.passwords.ix[0]

con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA', unix_socket="/tmp/mysql.sock")
combinedRankings.to_sql(con=con, name='polls', if_exists='replace',flavor='mysql')

print 'done!'