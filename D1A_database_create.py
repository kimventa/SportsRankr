import pandas as pd
import MySQLdb as mdb

#list of D1A teams for 2015
teams = {'team': ['Air Force', 'Akron', 'Alabama', 'Appalachian State', 
		'Arizona', 'Arizona State', 'Arkansas', 'Arkansas State', 'Army', 
		'Auburn', 'Ball State', 'Baylor', 'Boise State', 'Boston College', 
		'Bowling Green', 'Buffalo', 'Brigham Young', 'California', 
		'Fresno State', 'UCLA', 'Central Florida', 'Central Michigan', 
		'Charlotte', 'Cincinnati', 'Clemson', 'Colorado', 'Colorado State', 
		'Connecticut', 'Duke', 'Eastern Michigan', 'East Carolina', 'Florida', 
		'Florida Atlantic', 'Florida International', 'Florida State', 'Georgia', 
		'Georgia Southern', 'Georgia State', 'Georgia Tech', 'Hawaii', 
		'Houston', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Iowa State', 
		'Kansas', 'Kansas State', 'Kent State', 'Kentucky', 'Louisiana State', 
		'Louisiana Tech', 'Louisiana-Lafayette', 'Louisiana-Monroe', 
		'Louisville', 'Marshall', 'Maryland', 'Massachusetts', 'Memphis', 
		'Miami (FL)', 'Miami (OH)', 'Michigan', 'Michigan State', 
		'Middle Tennessee', 'Minnesota', 'Mississippi', 'Mississippi State', 
		'Missouri', 'Navy', 'Nebraska', 'Nevada', 'Nevada-Las Vegas', 
		'New Mexico', 'New Mexico State', 'North Carolina', 
		'North Carolina State', 'North Texas', 'Northern Illinois', 
		'Northwestern', 'Notre Dame', 'Ohio', 'Ohio State', 'Oklahoma', 
		'Oklahoma State', 'Old Dominion', 'Oregon', 'Oregon State', 
		'Penn State', 'Pittsburgh', 'Purdue', 'Rice', 'Rutgers', 
		'San Diego State', 'San Jose State', 'South Alabama', 'South Carolina', 
		'South Florida', 'Southern California', 'Southern Methodist', 
		'Southern Mississippi', 'Stanford', 'Syracuse', 'Temple', 'Tennessee', 
		'Texas', 'Texas A and M', 'Texas Christian', 'Texas State', 
		'Texas Tech', 'Texas-El Paso', 'Texas-San Antonio', 'Toledo', 'Troy', 
		'Tulane', 'Tulsa', 'Utah', 'Utah State', 'Vanderbilt', 'Virginia', 
		'Virginia Tech', 'Wake Forest', 'Washington', 'Washington State', 
		'West Virginia', 'Western Kentucky', 'Western Michigan', 'Wisconsin', 
		'Wyoming']}
	
#save as a dataframe
D1A = pd.DataFrame(teams)
D1A.to_pickle('D1A.pkl')

#load credentials
login = pd.read_pickle('credentials.pkl')
username = login.usernames.ix[0]
password = login.passwords.ix[0]

#save as a sql table
con = mdb.connect(host='localhost',user=username,passwd=password,db='NCAA', 
	unix_socket="/tmp/mysql.sock")
D1A.to_sql(con=con, name='D1A', if_exists='replace',flavor='mysql')
