# nba-live-stats
Will find a live game and output stats in realtime. Can also check stats of any players or teams for past and current seasons.
Use ```bball_espn.py``` to get today's games and play by play data for live games. Uses [nba-py](https://pypi.org/project/nba-api/) to get play-by-play data for past games.




# bball_espn features
Shows current game play-by-play data, with detailed stats at the end of each line. Scores are only displayed when the score has changed. During timeouts, a boxscore of point progression throughout quarters is displayed as well as a full boxscore for the game.

### Example output:
```
128 - 126   1:12 - Donovan Mitchell makes 13-foot running pullup jump shot (17 points, 6-17 FG)
            58.6 - Brandon Ingram misses shot (12-25 FG)

128 - 126   54.1 - Royce O'Neale defensive rebound

128 - 126   39.9 - Royce O'Neale misses shot

128 - 126   37.0 - Derrick Favors defensive rebound
            37.0 - Pelicans Full timeout
+------+-----+-----+-----+-----+-----+
|      |   1 |   2 |   3 |   4 |   T |
|------+-----+-----+-----+-----+-----|
| UTAH |  35 |  33 |  27 |  33 | 128 |
| NO   |  36 |  28 |  33 |  29 | 126 |
+------+-----+-----+-----+-----+-----+

              MIN     FG    3PT     FT OREB DREB REB AST STL BLK TO  PF  +/-  PTS
B. Bogdanovic  32  11-20    3-8  10-10    0    0   0   0   0   0  3   3   -3   35
R. O'Neale     34    1-2    1-2    0-0    0    6   6   2   0   0  0   4   -3    3
J. Ingles      27   8-12    4-5    2-2    0    2   2   6   2   0  0   1  +12   22
R. Gobert      33   4-10    0-0    1-2    4   15  19   1   0   0  2   4   +1    9
D. Mitchell    33   7-18    2-6    3-3    0    4   4   6   1   0  0   5   +2   19
G. Niang       16    2-4    2-3    0-0    0    4   4   0   0   0  0   0   +0    6
T. Bradley     14    2-3    0-0    3-4    1    2   3   1   0   2  1   4   +1    7
E. Mudiay      16    4-8    0-1    0-0    0    2   2   2   0   0  1   2   -3    8
J. Clarkson    25   6-11    4-7    0-2    1    0   1   1   0   1  1   2   +0   16
R. Tucker       5    1-1    0-0    1-1    1    0   1   0   0   0  0   0   +3    3
J. Morgan       -      -      -      -    -    -   -   -   -   -  -   -    -    -
E. Davis        -      -      -      -    -    -   -   -   -   -  -   -    -    -
TEAM               46-89  16-32  20-24    7   35  42  19   3   3  8  25       128
                   51.7%  50.0%  83.3%

                MIN     FG    3PT     FT OREB DREB REB AST STL BLK TO  PF  +/-  PTS
D. Favors        28    4-7    0-0    1-1    3    6   9   2   0   3  0   2   -2    9
B. Ingram        38  12-25    3-6    8-8    3    4   7   5   1   1  3   3   +7   35
L. Ball          36   8-14    4-6    1-3    3    5   8   7   0   0  1   2   -9   21
J. Redick        30   7-11    2-4    7-7    0    3   3   1   0   0  1   1  +11   23
J. Hart          27    3-7    2-6    0-0    1    2   3   1   0   0  0   5  -14    8
J. Hayes         19    2-3    0-0    3-4    1    2   3   3   0   1  0   1   +0    7
F. Jackson        5    2-4    0-2    1-1    0    0   0   0   0   0  0   0   -9    5
N. Alexander...  15    2-5    1-2    0-2    0    5   5   2   0   0  1   2   +9    5
K. Williams       9    0-1    0-1    0-0    0    0   0   1   1   0  0   1   -9    0
E. Moore         27   5-14    0-4    3-4    0    7   7   1   2   0  0   3   +6   13
N. Melli          -      -      -      -    -    -   -   -   -   -  -   -    -    -
J. Okafor         -      -      -      -    -    -   -   -   -   -  -   -    -    -
J. Holiday        -      -      -      -    -    -   -   -   -   -  -   -    -    -
TEAM                 45-91  12-31  24-30   11   34  45  23   4   5  6  20       126
                     49.5%  38.7%  80.0%
```
