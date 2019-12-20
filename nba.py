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
			p['teamName'] = get_team_id(p['teamId'])
	#print(d)
	return d

def make_game_dict(d, url):
	res = requests.get(url)
	data = res.json()
	for s in data['stats']['vTeam']:
		None



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
	print(url, '\n')
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
	game_stats = {}
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
		flag = False
		data = refresh_stats(url)
		for p in data['stats']['activePlayers']:
			if flag: break
			data = refresh_stats(url)
			sub_out = None
			sub_in = None
			current_id = p['personId']
			name = None

			if players.find_player_by_id(current_id):
				name = players.find_player_by_id(current_id)['full_name']
			if not name: name = p['player_code']
			current_player_points = p['points']
			if current_id not in player_stats:
				player_stats[current_id] = p
			if check_diff(player_stats[current_id], ('offReb', p['offReb'])):
				k, v = check_diff(player_stats[current_id], ('offReb', p['offReb']))
				player_stats[current_id][k] = v
				print(12*' ', f'OFFENSIVE REBOUND: {name} (offReb:{v}, totalReb: %s)' % p['totReb'])
				flag = True
				break
			elif check_diff(player_stats[current_id], ('fga', p['fga'])):
				k, v = check_diff(player_stats[current_id], ('fga', p['fga']))
				if check_diff(player_stats[current_id], ('fgm', p['fgm'])):
					i, j = check_diff(player_stats[current_id], ('fgm', p['fgm']))
					if check_diff(player_stats[current_id], ('tpm', p['tpm'])):
						a, b =  check_diff(player_stats[current_id], ('tpm', p['tpm']))
						player_stats[current_id][a] = b
						a, b =  check_diff(player_stats[current_id], ('tpa', p['tpa']))
						print(f'{home_points} - {vis_points}'.ljust(12), f'{name} MADE a three pointer ({current_player_points} points)')
						player_stats[current_id][a] = b
					elif check_diff(player_stats[current_id], ('tpa', p['tpa'])):
						a, b =  check_diff(player_stats[current_id], ('tpa', p['tpa']))
						tpm = p['tpm']
						tpa = p['tpa']
						player_stats[current_id][a] = b
						print(12*' ', f'{name} MISSED a three pointer ({tpm}/{tpa})')
					else:
						print(f'{home_points} - {vis_points}'.ljust(12), f'{name} MADE a field goal ({current_player_points} points)')
					player_stats[current_id][i] = j
				else:
					player_stats[current_id][k] = v
					fgm = p['fgm']
					fga = p['fga']
					print(12*' ', f'{name} MISSED a field goal ({fgm}/{fga})')
				player_stats[current_id][k] = v
				flag = True
				break
			elif check_diff(player_stats[current_id], ('fta', p['fta'])):
				k, v = check_diff(player_stats[current_id], ('fta', p['fta']))
				if check_diff(player_stats[current_id], ('ftm', p['ftm'])):
					a, b = check_diff(player_stats[current_id], ('ftm', p['ftm']))
					player_stats[current_id][a] = b
					player_stats[current_id][k] = v
					print(f'{home_points} - {vis_points}'.ljust(12), f'{name} MADE a free throw ({current_player_points} points)')
					flag = True
					break
				else:
					player_stats[current_id][k] = v
					ftm = p['ftm']
					fta = p['fta']
					print(f'{home_points} - {vis_points}'.ljust(12), f'{name} MISSED a free throw ({ftm}/{fta})')
					flag = True
					break
			elif check_diff(player_stats[current_id], ('pFouls', p['pFouls'])):
				k, v = check_diff(player_stats[current_id], ('pFouls', p['pFouls']))
				player_stats[current_id][k] = v
				print(12*' ', f'FOUL on {name} ({v} fouls)')
				flag = True
				break
			elif check_diff(player_stats[current_id], ('steals', p['steals'])):
				k, v = check_diff(player_stats[current_id], ('steals', p['steals']))
				player_stats[current_id][k] = v
				print(12*' ', f'STEAL: {name} ({v} steals)')
				flag = True
				break
			elif check_diff(player_stats[current_id], ('turnovers', p['turnovers'])):
				k, v = check_diff(player_stats[current_id], ('turnovers', p['turnovers']))
				player_stats[current_id][k] = v
				print(12*' ', f'TURNOVER: {name} ({v} turnovers)')
				flag = True
				break
			





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






















