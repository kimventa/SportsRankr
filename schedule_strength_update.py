import pandas as pd

def main(week,season):
	
	#collect relevant info
	week = str(week)
	season = int(season)
	games = pd.read_pickle('games.pkl')
	ranks = pd.read_pickle('ratingsTable_final3.pkl')
	
	#initialize variables
	seasonGames = games[(games.season == season)]
	avgStrength = 0
	
	#get season schedule for each team
	for team in seasonGames.Team.unique():
		
		#initialize variables
		teamGames = seasonGames[seasonGames.Team == team]
		opponents = []
		strength = 0
		
		#find opponent for each game in the team's schedule
		for i in range(len(teamGames)):
			game = teamGames.iloc[i]
			if game.winner == team:
				opponents.append(game.loser)
			else:
				opponents.append(game.winner)
				
		#for each opponent, calculate the opponent strength
		for opponent in opponents:
			try:
				oppStrength = ranks[(ranks.Team == opponent) & (ranks.season == str(season)) & (ranks.Week == week)].Rating.values[0]
			except IndexError:
				oppStrength = 1
			strength += oppStrength
			
		#calculate the team's season strength, and add to the average
		strength = strength/len(opponents)
		avgStrength += strength
	
	#calculate the average season strength and output
	avgStrength = avgStrength/len(seasonGames.Team.unique())
	print avgStrength
	
main(5,2015)