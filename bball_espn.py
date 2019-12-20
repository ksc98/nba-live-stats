import bs4 as bs
import urllib.request
import nba, time, re, sys, boxscore

first_parse = False


def create_game_list():
	url = 'https://www.espn.com/nba/scoreboard'
	source = urllib.request.urlopen(url).read()
	soup = bs.BeautifulSoup(source, 'lxml')
	game_ids = set(re.findall(r'(?<=http://www.espn.com/nba/game\?gameId=)\d*(?=")', str(soup)))
	game_list = []
	for game in game_ids:
		url = f'https://www.espn.com/nba/playbyplay?gameId={game}'
		source = urllib.request.urlopen(url).read()
		soup = bs.BeautifulSoup(source, 'lxml')
		game_title = soup.title.text.split('-')[0].strip()
		game_list.append((game_title, url))
	return game_list


def parse_string(source):
	soup = bs.BeautifulSoup(source, 'lxml')
	timer = soup.find_all('td', {'class':'time-stamp'})
	deets = soup.find_all('td', {'class':'game-details'})
	score = soup.find_all('td', {'class':'combined-score'})
	return timer, deets, score



"""

('R. Westbrook', {'position': 'PG', 'min': '35', 'fg': '12-30',
'3pt': '2-6', 'ft': '11-12', 'oreb': '1',
'dreb': '8', 'reb': '9', 'ast': '5', 'stl': '1', 'blk': '0',
'to': '7', 'pf': '4', 'plusminus': '+4', 'pts': '37'})

"""


def process_deets(s, url):
	gameid = re.findall(r'(?<=gameId=).*', url)[0]
	boxscore_dict = boxscore.get_boxscore_dict(gameid)
	player_name = re.findall(r'^(?:[A-Z]+[^A-Z]*?)+(?= [a-z]|$)', s)
	if not player_name:
		#print(f'no player found in string: "{s}"')
		return s
	#print(s)
	player_name = player_name[0].lower()
	if player_name not in boxscore_dict:
		#print(f'no player found in string: "{s}"')
		return s
	s = s.replace(' \'', '\'')
	if 'free throw 1 of 1' in s:
		if 'AND1' not in boxscore_dict[player_name]:
			boxscore_dict[player_name]['AND1'] = 1
		else:
			boxscore_dict[player_name]['AND1'] += 1
		numFT = boxscore_dict[player_name]['ft']
		numAND1 = boxscore_dict[player_name]['AND1']
		s += f' ({numFT} FT, {numAND1} AND1\'s)'
	if 'shooting foul' in s or 'personal foul' in s or 'charge' in s or 'offensive foul' in s or 'foul' in s:
		#print(player_name)
		numFouls = boxscore_dict[player_name]['pf']
		s += f' ({numFouls} fouls)'
	elif 'block' in s:
		numBlocks = boxscore_dict[player_name]['blk']
		blocks = 'blocks' if int(numBlocks) > 1 else 'block'
		s += f' ({numBlocks} {blocks})'
	elif 'free throw' in s:
		numFT = boxscore_dict[player_name]['ft']
		s += f' ({numFT} FT)'
	elif 'makes' in s:
		numPoints = boxscore_dict[player_name]['pts']
		if 'three point' in s:
			numThrees = boxscore_dict[player_name]['3pt']
			s += f' ({numPoints} points, {numThrees} 3PT)'
		elif re.search(r'\d+(?=-foot)', s):
			if int(re.findall(r'\d+(?=-foot)', s)[0]) >= 22:
				numThrees = boxscore_dict[player_name]['3pt']
				s += f' ({numPoints} points, {numThrees} 3PT)'
			else:
				numFG = boxscore_dict[player_name]['fg']
				s += f' ({numPoints} points, {numFG} FG)'
		else:
			numFG = boxscore_dict[player_name]['fg']
			s += f' ({numPoints} points, {numFG} FG)'
	elif 'misses' in s:
		if 'three point' in s:
			numThrees = boxscore_dict[player_name]['3pt']
			s += f' ({numThrees} 3PT)'
		elif re.search(r'\d+(?=-foot)', s):
			feet = re.findall(r'\d+(?=-foot)', s)[0]
			feet = int(feet)
			if feet < 22:
				numFG = boxscore_dict[player_name]['fg']
				s += f' ({numFG} FG)'
			else:
				numThrees = boxscore_dict[player_name]['3pt']
				s += f' ({numThrees} 3PT)'
		else:
			numFG = boxscore_dict[player_name]['fg']
			s += f' ({numFG} FG)'
	elif 'offensive rebound' in s:
		numOffReb = boxscore_dict[player_name]['oreb']
		s += f' (offReb: {numOffReb})'
	elif 'turnover' in s or 'traveling' in s:
		numTO = boxscore_dict[player_name]['to']
		to = 'turnover' if numTO == 1 else 'turnovers'
		s += f' ({numTO} {to})'
	return s

	"""
	TODO:   bad pass -> steal
			timeouts

	"""



def print_str(timer, deets, score, url):
	last_score = None
	global first_parse
	for i, j, k in zip(reversed(timer), reversed(deets), reversed(score)):
		j = j.string
		if first_parse:
			j = process_deets(j, url)
		if last_score == None or k != last_score:
			print()
			print(f'{k.string}'.ljust(12) + f'{i.string} - {j}')
		else:
			print(12*' ' + f'{i.string} - {j}')
		last_score = k


def get_pbp(url):
	global first_parse
	oldstr = None
	source = urllib.request.urlopen(url).read()
	x = re.findall(r'(?<=<div id="gamepackage-qtrs-wrap">)(.*)(?=<div id="gamepackage-sponsoredcontent")', str(source))[0]
	with open('out1.txt', 'w') as f:
		f.write(str(x))
	timer, deets, score = parse_string(str(x).replace('\\', ''))
	oldlen = len(timer)
	while True:
		source = urllib.request.urlopen(url).read()
		x = re.findall(r'(?<=<div id="gamepackage-qtrs-wrap">)(.*)(?=<div id="gamepackage-sponsoredcontent")', str(source))[0]
		x = x.replace('\\', '')
		if oldstr == None:
			oldstr = x
			print_str(timer, deets, score, url)
			first_parse = True
		else:
			timer, deets, score = parse_string(x)
			if len(timer) != oldlen:
				newlen = len(timer)
				timer = timer[:-oldlen]
				deets = deets[:-oldlen]
				score = score[:-oldlen]
				print_str(timer, deets, score, url)
				oldlen = newlen
		time.sleep(1)

def main():
	game_list = create_game_list()
	game_list = sorted(game_list)
	if len(sys.argv) > 1:
		url = [item[1] for item in game_list if sys.argv[1] in item[0].lower()]
		if len(url) != 0:
			get_pbp(url[0])
	print('Games today:')
	for i, x in enumerate(game_list):
		print(f'{i+1}: {x[0]}')
	print('\nWhich game?')
	which = input()
	url = None
	if which.isnumeric():
		which = int(which)
		which -= 1
		url = game_list[which][1]
		print(url)
	else:
		url = [item[1] for item in game_list if which in item[0].lower()]
		while len(url) == 0:
			print('\nCould not find game')
			which = input()
			url = [item[1] for item in game_list if which in item[0].lower()]
		url = url[0]
	gameid = re.findall(r'(?<=gameId=).*', url)[0]
	get_pbp(url)



if __name__ == '__main__':
	main()