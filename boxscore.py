import bs4 as bs
import urllib.request
import nba, time, re, sys
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
 

def print_dict(d):
    for p in d.items():
        print(p)
        print()

def get_boxscore_dict(gameid):
    url = f'https://www.espn.com/nba/boxscore?gameId={gameid}'
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source, 'lxml')
    with open('boxscores.txt', 'w') as f:
        f.write(str(soup.prettify))

    boxscores = {}
    for div in soup.find_all('div', class_='col-b'):
        x = div.find('article').find_all('tr')
        for i in x:
            temp = i.find('a')
            name = None
            if temp:
                name = ' '.join(temp['href'].split('/')[-1].split('-')).strip()
                if len(name.split()) == 3:
                    if name.split()[2] == 'jr':
                        name = name.split()
                        name = name[0] + ' ' + name[1] + ' ' + name[2] +'.'
                    elif len(name.split()[2]) < 3:
                        name = name.split()
                        name = name[0] + ' ' + name[1] + ' ' + name[2]
                    else:
                        name = name.split()
                        name = name[0] + ' ' + name[1] + '-' + name[2]
                if players.find_players_by_full_name(name):
                    player_id = players.find_players_by_full_name(name)[0]['id']
            current_name = None
            for thing in i.findChildren():
                if thing.has_attr('class'):
                    if thing.attrs['class'][0] == 'abbr':
                        current_name = thing.text
                        if name: current_name = name
                        if current_name not in boxscores:
                            boxscores[current_name] = {}
                    elif thing.attrs['class'][0] == 'name':
                        None
                        
                    elif thing.attrs['class'][0] != 'name' and current_name:
                        boxscores[current_name][thing.attrs['class'][0]] = thing.text

    return boxscores

def print_boxscore(gameid):
    url = f'https://www.espn.com/nba/boxscore?gameId={gameid}'
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source, 'lxml')

    for div in soup.find_all('div', class_='table-caption'):
        print()
        print(f'[{div.text}]')
        for table in soup.find_all('table', class_='mod-data'):
            for thing in table.find_all('th'):
                print(thing.text, end='\t')
            print()
            for p in table.find_all('td'):
                if p['class'][0] == 'name':
                    if p.find(class_='abbr'):
                        print(p.find(class_='abbr').text, end='\t')
                else:
                    print(p.text, end='\t')
                if p['class'][0] == 'pts' or p['class'][0] == 'dnp':
                    print()
            print()
        print()











def main():
    #print_dict(get_boxscore_dict(401161060))
    print_boxscore(401161093)



if __name__ == '__main__':
    main()