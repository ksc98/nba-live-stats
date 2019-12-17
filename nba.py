from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playbyplay, leaguegamefinder
from collections import defaultdict
from nba_api.stats.library.parameters import Season, SeasonType
import pandas, sys
import player
from bs4 import BeautifulSoup
import json, requests



def get_team_id(team_name):
	nba_teams = teams.get_teams()
	if(type(team_name) == int):
		for t in nba_teams:
			if t['id'] == team_name:
				return t['nickname']
	for t in nba_teams:
		if t['abbreviation'] == team_name.upper():
			return t['id']
		elif team_name in t['nickname'].lower():
			return t['id']



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
	url = 'https://data.nba.net/prod/v1/20191216/0021900396_boxscore.json'
	
	res = requests.get(url)
	data = res.json()
	print(data['stats'].keys())
	for d in data['stats']['vTeam'].items():
		print(d)
	for d in data['stats']['hTeam'].items():
		print(d)

	print('\n\n')

	for p in data['stats']['activePlayers']:
		print(p)
	print(data['stats']['hTeam']['totals']['points'], '-', data['stats']['vTeam']['totals']['points'])
	for p in data['stats']['activePlayers']:
		if(p['isOnCourt']):
			print(get_team_id(int(p['teamId'])), end=' ')
			print(p['jersey'], p['firstName'], p['lastName'], '(%s points)' % p['points'], '[%s]' % p['plusMinus'])

	exit(1)
	print('Game or stats')
	i = input()
	if i.lower() in ['game', 'g']:
		print('Enter team:')
		team = input()
		s = team.split()
		if len(s) == 1:
			team = s[0]
			if not get_team_id(team):
				main()
			else: get_pbp(get_team_id(team))
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






















