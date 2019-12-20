import bs4 as bs
import urllib.request
import nba, time, re

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

def print_str(timer, deets, score):
	for i, j, k in zip(reversed(timer), reversed(deets), reversed(score)):
		print(f'[{k.string}] ({i.string} seconds) {j.string}')


def get_pbp(url):
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
			print_str(timer, deets, score)
		else:
			timer, deets, score = parse_string(x)
			if len(timer) != oldlen:
				newlen = len(timer)
				timer = timer[:-oldlen]
				deets = deets[:-oldlen]
				score = score[:-oldlen]
				print_str(timer, deets, score)
				oldlen = newlen
		time.sleep(1)

def main():
	game_list = create_game_list()
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
		#print(url)
	get_pbp(url)



if __name__ == '__main__':
	main()