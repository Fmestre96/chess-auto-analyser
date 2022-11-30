import chessdotcom 
import requests 
import json
import websockets
import asyncio
import sys


year = 2022
month = 11



def printProgressMatch(matchID, percentage):
    if percentage == 100:
        print("Analysing match " + matchID + " | " + str(percentage) + "%\r")
    else:
        sys.stdout.write("Analysing match " + matchID + " | " + str(percentage) + "%\r")
        sys.stdout.flush()


def getInitialWSSPost(gameID, token):
    #open postWSS.json
    with open('postWSS.json', 'r') as f:
        data = json.load(f)
    data['options']['gameId'] = gameID
    data['options']['token'] = token
    data['game']['pgn'] = data['game']['pgn'].replace('GAMEID', gameID)
    return data


def getPlayerMatches(username):
    matches = chessdotcom.get_player_game_archives(username)
    return matches.json['archives']


def getPlayerMonthMatches(username, year, month):
    api_url = f'https://api.chess.com/pub/player/{username}/games/{year}/{month}'	
    response = requests.get(api_url)
    return response.json()['games']


async def analyseMatch(matchID, token, pgn=None):
    async with websockets.connect('wss://analysis-va.chess.com/') as websocket:

        #send initial post
        post = getInitialWSSPost(matchID, token)
        await websocket.send(json.dumps(post))

        print(f"> {json.dumps(getInitialWSSPost(matchID, token))}")
        action = "progress"
        while action != "done":
            message = await websocket.recv()
            decoded = json.loads(message)
            action = decoded["action"]
            progress = decoded.get('progress')
            if progress:
                #multiply by 100 and round to 2 decimal places
                progress = round(progress * 100, 2)
                printProgressMatch(matchID, progress)
            print(f"< {message}")
        #printProgressMatch(matchID, 100)

#main
if __name__ == "__main__":
    #archive = getPlayerMatches("f1lipmeister")
    # monthlyMatches = getPlayerMonthMatches("f1lipmeister", year, month)
    # matchID = monthlyMatches[0]['url'].split('/')[-1]

    matchID = 63223614799
    matchID = str(matchID)
    asyncio.run(analyseMatch(matchID, ""))

    #TODO Understand how to get token
    #TODO Understand how to get pgn
    #TODO Understand what is required for initial send
