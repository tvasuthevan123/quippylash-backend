import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from PlayerLeaderboard import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

players_container = db_client.get_container_client(config.settings['players_container'])

request_url = 'http://localhost:7071/api/player/leaderboard/'

class TestFunction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        try:
            players_container.create_item({'id': 'd', 'password': 'pythonrulz', "total_score": 1, "games_played":0})
            players_container.create_item({'id': 'c', 'password': 'pythonrulz', "total_score": 3, "games_played":0})
            players_container.create_item({'id': 'a', 'password': 'pythonrulz', "total_score": 3, "games_played":0})
            players_container.create_item({'id': 'b', 'password': 'pythonrulz', "total_score": 4, "games_played":0})
            players_container.create_item({'id': 'e', 'password': 'pythonrulz', "total_score": 5, "games_played":0})
        except Exception as e:
            print(repr(e))

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            players_container.delete_item(item='a', partition_key='a')
            players_container.delete_item(item='b', partition_key='b')
            players_container.delete_item(item='c', partition_key='c')
            players_container.delete_item(item='d', partition_key='d')
            players_container.delete_item(item='e', partition_key='e')
        except Exception as e:
            print(repr(e))

    def test_player_leaderboard__simple(self):
        payload = {"top": 2}

        resp = requests.get(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = [
            {"username": "e" , "total_score": 5, "games_played":0},
            {"username": "b" , "total_score": 4, "games_played":0}
        ]

        print(create_response)
        print(expected_response)
        self.assertEqual(expected_response, create_response)

    def test_player_leaderboard__tiebreak(self):
        payload = {"top": 3}

        resp = requests.get(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = [
            {"username": "e" , "total_score": 5, "games_played":0},
            {"username": "b" , "total_score": 4, "games_played":0},
            {"username": "a" , "total_score": 3, "games_played":0},
        ]

        print(create_response)
        print(expected_response)
        self.assertEqual(expected_response, create_response)
