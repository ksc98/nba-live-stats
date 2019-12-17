from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from nba_api.stats.static import players, teams
from collections import defaultdict
import sys


def get_id(player_name):
	if not players.find_players_by_full_name(player_name):
		return None
	return players.find_players_by_full_name(player_name)[0]['id']


def print_stats(playerid):
	career = playercareerstats.PlayerCareerStats(player_id=playerid)

	c_h = career.get_dict()['resultSets'][0]['headers']
	c_r = career.get_dict()['resultSets'][0]['rowSet']
	c_r = sorted(c_r, reverse=True)

	print(players.find_player_by_id(playerid)['full_name'], '(%s Seasons)' % len(c_r))

	agg = defaultdict(list)

	for item in c_r:
		z = zip(c_h, item)
		for header, value in z:
			if header == 'TEAM_ABBREVIATION':
				header = 'TEAM'
			if header == 'PLAYER_AGE':
				agg['AGE'].append(value)
			elif header not in ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID']:
				agg[header].append(value)
	l = defaultdict(list)

	for item in agg.values():
		for i, v in enumerate(item):
			l[i].append(v)



	for k in agg.keys():
		print(k, end='\t')

	print()
	for v in l.values():
		print('\t'.join([str(i) for i in v]))

	print()



def main():
	for p in sys.argv[1:]:
		print_stats(get_id(p))


if __name__ == '__main__':
	main()





