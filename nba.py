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

def make_dict(d, url):
	res = requests.get(url)
	data = res.json()
	for p in data['stats']['activePlayers']:
		#print(p)
		if p['personId'] not in d:
			d[p['personId']] = p
	#print(d)
	return d



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


def check_diff(player_stats, kv):
	k = kv[0]
	v = kv[1]
	if player_stats[k] != v:
		return k, v
	return None

def refresh_stats(url):
	res = requests.get(url)
	data = res.json()
	return data

def main():
	print('What team that is currently playing?')
	team_name = input()
	url = get_game_url(get_team_id(team_name))
	print(url)
	res = requests.get(url)
	if not res:
		print('Game has not started yet.\n')
		main()
	data = res.json()
	if not data:
		print('Game has not started yet')
		main()
	visitor_team = get_team_id(data['basicGameData']['vTeam']['teamId'])
	home_team = get_team_id(data['basicGameData']['hTeam']['teamId'])
	player_stats = {}
	start_time = time.time()
	keys = ['personId', 'firstName', 'lastName', 'jersey', 'teamId', 'isOnCourt', 'points', 'pos', 'position_full', 'player_code',
			'min', 'fgm', 'fga', 'fgp', 'ftm', 'fta', 'ftp', 'tpm',
			'tpa', 'tpp', 'offReb', 'defReb', 'totReb', 'assists', 'pFouls',
			'steals', 'turnovers', 'blocks', 'plusMinus', 'dnp', 'sortKey']
	i_keys = ['isOnCourt', 'points', 'fgm', 'fga', 'ftm', 'fta', 'tpm', 'tpa', 'offReb', 'defReb', 'totReb', 'assists', 'pFouls',
			'steals', 'turnovers', 'blocks']
	player_stats = make_dict(player_stats, url)
	while True:
		data = refresh_stats(url)
		home_points = data['stats']['hTeam']['totals']['points']
		vis_points = data['stats']['vTeam']['totals']['points']
		#print(f'{home_points} - {vis_points}')

		for p in data['stats']['activePlayers']:
			sub_out = None
			sub_in = None
			current_id = p['personId']
			name = None
			if players.find_player_by_id(current_id):
				name = players.find_player_by_id(current_id)['full_name']
			if not name: name = p['player_code']
			current_player_points = p['points']
			if check_diff(player_stats[current_id], ('defReb', p['defReb'])):
				k, v = check_diff(player_stats[current_id], ('defReb', p['defReb']))
				print(f'\tDEFENSIVE REBOUND: {name} ({v} rebounds)')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('offReb', p['offReb'])):
				k, v = check_diff(player_stats[current_id], ('offReb', p['offReb']))
				print(f'\tOFFENSIVE REBOUND: {name} ({v} rebounds)')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('tpa', p['tpa'])):
				k, v = check_diff(player_stats[current_id], ('tpa', p['tpa']))
				if check_diff(player_stats[current_id], ('tpm', p['tpm'])):
					k, v = check_diff(player_stats[current_id], ('tpm', p['tpm']))
					print(f'{home_points} - {vis_points}\t{name} MADE a three pointer [{current_player_points}]')
					player_stats[current_id][k] = v
					break
				print(f'{home_points} - {vis_points}\t{name} MISSED a field goal')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('fga', p['fga'])):
				k, v = check_diff(player_stats[current_id], ('fga', p['fga']))
				if check_diff(player_stats[current_id], ('fgm', p['fgm'])):
					k, v = check_diff(player_stats[current_id], ('fgm', p['fgm']))
					print(f'{home_points} - {vis_points}\t{name} MADE a field goal [{current_player_points}]')
					player_stats[current_id][k] = v
					break
				print(f'{home_points} - {vis_points}\t{name} MISSED a field goal')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('fta', p['fta'])):
				k, v = check_diff(player_stats[current_id], ('fta', p['fta']))
				if check_diff(player_stats[current_id], ('ftm', p['ftm'])):
					print(f'{home_points} - {vis_points}\t{name} MADE a free throw ({current_player_points} points)')
					player_stats[current_id][k] = v
					break
				print(f'{home_points} - {vis_points}\t{name} MISSED a free throw')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('pFouls', p['pFouls'])):
				k, v = check_diff(player_stats[current_id], ('pFouls', p['pFouls']))
				print(f'\tFOUL on {name} ({v} fouls)')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('steals', p['steals'])):
				k, v = check_diff(player_stats[current_id], ('steals', p['steals']))
				print(f'\tSTEAL: {name} ({v} steals)')
				player_stats[current_id][k] = v
				break
			elif check_diff(player_stats[current_id], ('turnovers', p['turnovers'])):
				k, v = check_diff(player_stats[current_id], ('turnovers', p['turnovers']))
				print(f'\tTURNOVER: {name} ({v} turnovers)')
				player_stats[current_id][k] = v
				break
			
		time.sleep(2)
		data = refresh_stats(url)





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






















