import pandas as pd
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

 




def print_quarter_breakdowns(url):
	pd.set_option('display.max_columns', None)
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', None)
	pd.set_option('display.max_colwidth', 15)




	#res = requests.get('https://www.espn.com/nba/boxscore?gameId=401161133')
	res = requests.get(url)
	#res = requests.get('https://stats.nba.com/game/0021900496/')
	soup = BeautifulSoup(res.content,'lxml')


	table = soup.find_all('table')[0]
	df = pd.read_html(str(table), index_col=0, keep_default_na=False)
	for d in df:
		print(tabulate(d, headers='keys', tablefmt='psql') )

	print()

	soup = BeautifulSoup(str(soup).replace('DNP-COACH\'S DECISION', '-'), 'lxml')
	for match in soup.find_all('span', class_=['abbr', 'position']):
		match.replaceWith('')
	table = soup.find_all(class_='mod-data')
	#print(table)
	df = pd.read_html(str(table), index_col=0, keep_default_na=False)
	team1 = df[0]
	team2 = df[1]
	team1.columns = [col[1] for col in team1.columns]
	print(team1)
	print()
	team2.columns = [col[1] for col in team2.columns]
	print(team2)






def main():
	None




if __name__ == '__main__':
	main()