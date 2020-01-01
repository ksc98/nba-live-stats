import bs4 as bs
import urllib.request
import nba, time, re, sys


def parse_string(source):
	soup = bs.BeautifulSoup(source, 'lxml')
	timer = soup.find_all('td', {'class':'time-stamp'})
	deets = soup.find_all('td', {'class':'game-details'})
	score = soup.find_all('td', {'class':'combined-score'})
	return timer, deets, score

def print_str(timer, deets, score):
	for i, j, k in zip(reversed(timer), reversed(deets), reversed(score)):
		print(f'[{k.string}] ({i.string} seconds) {j.string}')


def main():
	print('Enter team name')
	url = 'https://www.espn.com/nba/playbyplay?gameId=401161058'
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



if __name__ == '__main__':
	main()

