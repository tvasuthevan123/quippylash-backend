import unittest
import json
import requests
import wrapper 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from UpdatePlayer import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

players_container = db_client.get_container_client(config.settings['players_container'])

request_url = config.settings['cloud_URI'] + 'player/update/'

class TestFunction(unittest.TestCase):

    def setUp(self) -> None:
        try:
            players_container.create_item({"id" : "py_luis", "password": "pythonrulz" , "games_played" : 542 , "total_score" : 3744})
        except Exception as e:
            print(repr(e))

    def tearDown(self) -> None:
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
        except Exception as e:
            print(repr(e))

    def test_update_player__valid(self):
        # Test for adding to ONLY games_played
        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_games_played": 2}

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        update_response = wrapper.player_update(payload, local=True)

        all_users = list(players_container.read_all_items())
        user = all_users[0]

        del user['_attachments']
        del user['_etag']
        del user['_rid']
        del user['_self']
        del user['_ts']

        expected_user = payload
        expected_user['id'] = 'py_luis'
        del expected_user['username']
        del expected_user['add_to_games_played']
        expected_user['games_played']=544
        expected_user['total_score']=3744

        expected_req_resp = {"result" : True, "msg": "OK" }

        print(user)
        print(expected_user)
        self.assertEqual(expected_user, user)
        self.assertEqual(expected_req_resp, update_response)

        # Test for adding to ONLY total_score
        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_score": 2}

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        update_response = wrapper.player_update(payload, local=True)

        all_users = list(players_container.read_all_items())
        user = all_users[0]

        del user['_attachments']
        del user['_etag']
        del user['_rid']
        del user['_self']
        del user['_ts']

        expected_user = payload
        expected_user['id'] = 'py_luis'
        del expected_user['username']
        del expected_user['add_to_score']
        expected_user['games_played']=544
        expected_user['total_score']=3746

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_user, user)
        self.assertEqual(expected_req_resp, update_response)

        # Test for adding to both total_score and games_played
        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_score": 10, "add_to_games_played": 32}

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        update_response = wrapper.player_update(payload, local=True)

        all_users = list(players_container.read_all_items())
        user = all_users[0]

        del user['_attachments']
        del user['_etag']
        del user['_rid']
        del user['_self']
        del user['_ts']

        expected_user = payload
        expected_user['id'] = 'py_luis'
        del expected_user['username']
        del expected_user['add_to_score']
        del expected_user['add_to_games_played']
        expected_user['games_played']=576
        expected_user['total_score']=3756

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_user, user)
        self.assertEqual(expected_req_resp, update_response)

    def test_update_player__non_existent_user(self):
        payload = {"username": "py_luis123" , "password": "pythonrulz", "add_to_score": 10, "add_to_games_played": 32}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        update_response = wrapper.player_update(payload, local=True)

        expected_req_resp = {"result": False, "msg": "user does not exist" }

        self.assertEqual(expected_req_resp, update_response)

    def test_update_player__wrong_password(self):
        payload = {"username": "py_luis" , "password": "pythonwrong", "add_to_score": 10, "add_to_games_played": 32}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        update_response = wrapper.player_update(payload, local=True)

        expected_req_resp = {"result": False, "msg": "wrong password" }

        self.assertEqual(expected_req_resp, update_response)

    def test_update_player__invalid_update(self):
        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_score": -5, "add_to_games_played": 32}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        update_response = wrapper.player_update(payload, local=True)

        expected_req_resp = {"result": False, "msg": "Value to add is <=0" }

        self.assertEqual(expected_req_resp, update_response)

        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_score": 22, "add_to_games_played": -4}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        update_response = wrapper.player_update(payload, local=True)

        expected_req_resp = {"result": False, "msg": "Value to add is <=0" }

        self.assertEqual(expected_req_resp, update_response)

        payload = {"username": "py_luis" , "password": "pythonrulz", "add_to_score": -1, "add_to_games_played": 0}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        update_response = wrapper.player_update(payload, local=True)

        expected_req_resp = {"result": False, "msg": "Value to add is <=0" }

        self.assertEqual(expected_req_resp, update_response)
