from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playbyplay, leaguegamefinder
from collections import defaultdict
from nba_api.stats.library.parameters import Season, SeasonType
import pandas, sys
import player, time
from bs4 import BeautifulSoup
import json, requests
from datetime import date


def get_team_id(team_name):
	nba_teams = teams.get_teams()
	if(type(team_name) == int):
		for t in nba_teams:
			if t['id'] == team_name:
				return t
	for t in nba_teams:
		if t['abbreviation'] == team_name.upper():
			return t['id']
		elif team_name in t['nickname'].lower():
			return t['id']

def get_game_url(team_id):
	gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=Season.default, season_type_nullable=SeasonType.regular)
	games_dict = gamefinder.get_normalized_dict()
	games = games_dict['LeagueGameFinderResults']
	game = games[0]
	game_id = game['GAME_ID']
	game_matchup = game['MATCHUP']
	today = date.today()
	d1 = today.strftime("%Y%m%d")

	return f'https://data.nba.net/prod/v1/{d1}/{game_id}_boxscore.json'


# Get play-by-play of any game that has ended

def get_pbp(team_id):
	gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=Season.default, season_type_nullable=SeasonType.regular)

	games_dict = gamefinder.get_normalized_dict()
	games = games_dict['LeagueGameFinderResults']
	game = games[0]
	game_id = game['GAME_ID']
	game_matchup = game['MATCHUP']

	print(f'Searching through {len(games)} game(s) for the game_id of {game_id} where {game_matchup}')

	df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
	df = playbyplay.PlayByPlay(game_id).get_normalized_dict()['PlayByPlay']
	pandas.set_option('display.max_colwidth',300)
	pandas.set_option('display.max_rows',1000)

	scorelist = ['0 - 0']
	most_recent_score = '0 - 0'
	counter = 1
	for p in df:
		if(p['SCORE']): scorelist.append(p['SCORE'])

		if(p['HOMEDESCRIPTION']):
			if most_recent_score != scorelist[-1]:
				print('{score:<10}   {desc:>5}'.format(score=scorelist[-1], desc=p['HOMEDESCRIPTION']))
				counter = 1
			else:
				print((11+counter)*' ', p['HOMEDESCRIPTION'])
				#counter += 1
		if(p['VISITORDESCRIPTION']):
			if most_recent_score != scorelist[-1]:
				print('{score:<10}   {desc:>5}'.format(score=scorelist[-1], desc=p['VISITORDESCRIPTION']))
				counter = 1
			else:
				print((11+counter)*' ', p['VISITORDESCRIPTION'])
				#counter += 1

		if(p['SCORE']): most_recent_score = p['SCORE']






def main():
	print('What team that is currently playing?')
	team_name = input()
	url = get_game_url(get_team_id(team_name))
	print(url)
	res = requests.get(url)
	data = res.json()
	visitor_team = get_team_id(data['basicGameData']['vTeam']['teamId'])
	home_team = get_team_id(data['basicGameData']['hTeam']['teamId'])
	player_stats = {}

	start_time = time.time()

	keys = ['personId', 'firstName', 'lastName', 'jersey', 'teamId', 'isOnCourt', 'points', 'pos', 'position_full', 'player_code',
			'min', 'fgm', 'fga', 'fgp', 'ftm', 'fta', 'ftp', 'tpm',
			'tpa', 'tpp', 'offReb', 'defReb', 'totReb', 'assists', 'pFouls',
			'steals', 'turnovers', 'blocks', 'plusMinus', 'dnp', 'sortKey']
	while True:
		res = requests.get(url)
		data = res.json()
		home_points = data['stats']['hTeam']['totals']['points']
		vis_points = data['stats']['vTeam']['totals']['points']
		for p in data['stats']['activePlayers']:
			#print(p.keys())
			if p['personId'] not in player_stats:
				player_stats[p['personId']] = p
			else:
				current_id = p['personId']
				FT = False
				bucket = False
				sub_out = None
				sub_in = None
				for item in p.items():
					#print(item)
					# if item[0] == 'points':
						# player_stats[current_id][item[0]] = 1
					if player_stats[current_id][item[0]] != item[1]:
						name = players.find_player_by_id(current_id)['full_name']
						#print(f'For player {name}, {item[0]} changed from {player_stats[current_id][item[0]]} to {item[1]}')
						if (item[0]) == 'isOnCourt':
							if item[1] == False:
								sub_out = name
							elif item[1] == True:
								sub_in = name
						if sub_out and sub_in:
							print(f'\t{sub_in} SUBBED IN for {sub_out}')
						elif item[0] == 'fgm':
							bucket = True
							print(f'{home_points} - {vis_points}\t{name} SCORED a field goal')
						elif item[0] == 'fga' and not bucket:
							print(f'\t{name} MISSED a field goal')
						if item[0] == 'ftm':
							FT = True
							print(f'{name} SCORED a free throw')
						elif item[0] == 'fta':
							print(f'{name} MISSED a free throw')

						player_stats[current_id][item[0]] = item[1]
						
		time.sleep(2)



	for d in data['stats']['vTeam'].items():
		print(d)

	for d in data['stats']['hTeam'].items():
		print(d)

	print('\n\n')

	
	

	#print(data['stats']['hTeam']['totals']['points'], '-', data['stats']['vTeam']['totals']['points'])
	for p in data['stats']['activePlayers']:
		if(p['isOnCourt']):
			print(get_team_id(int(p['teamId']))['nickname'], end=' ')
			print(p['jersey'], p['firstName'], p['lastName'], '(%s points)' % p['points'], '[%s]' % p['plusMinus'])
	for item in player_stats.items():
		print(item[0])
		for i in item[1].items():
			print('\t', i)
	exit(1)
	print('Game or stats')
	i = input()
	if i.lower() in ['game', 'g']:
		print('Enter team:')
		team = input()
		s = team.split()
		if len(s) == 1:
			team = s[0]
			if not get_team_id(team)['nickname']:
				main()
			else: get_pbp(get_team_id(team)['nickname'])
		else:
			team1 = s[0]
			team2 = s[-1]

	elif i.lower() in ['stats','s']:
		print('Enter player:')
		name = input()
		p = player.get_id(name)
		if not p:
			while (not p):
				print('Enter player:')
				name = input()
				p = player.get_id(name)
			player.print_stats(p)
		else: player.print_stats(p)

	else:
		main()

	

if __name__ == '__main__':
	main()






















