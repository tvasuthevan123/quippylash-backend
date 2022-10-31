import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from RegisterPlayer import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

players_container = db_client.get_container_client(config.settings['players_container'])

request_url = 'http://localhost:7071/api/player/register/'

class TestFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        try:
            all_users = list(players_container.read_all_items())
            if len(all_users)>0:
                raise Exception('Setup Failed - Empty user container before test')
            else: 
                print('Setup Successful - No users in container')
        except Exception as e:
            print(repr(e))
            raise unittest.SkipTest(repr(e))

    def tearDown(self):
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
        except Exception as e:
            print(repr(e))

    def test_register_player__valid(self):
        payload = {"username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

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
        expected_user['games_played']=0
        expected_user['total_score']=0

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_user, user)
        self.assertEqual(expected_req_resp, create_response)

    def test_register_player__existing_user(self):
        payload = {"username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "Username already exists" }

        self.assertEqual(expected_req_resp, create_response)

    def test_register_player__username_incorrect_length(self):
        # Long Username
        payload = {"username" : "py_luis1234567891234", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "Username less than 4 characters or more than 16 characters" }

        self.assertEqual(expected_req_resp, create_response)

        ## Short Username
        payload = {"username" : "py", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "Username less than 4 characters or more than 16 characters" }

        self.assertEqual(expected_req_resp, create_response)

    def test_register_player__pwd_incorrect_length(self):
        # Long Username
        payload = {"username" : "py_luis", "password": "pythonrulzandalsoabunchofothercharacters"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "Password less than 8 characters or more than 24 characters" }

        self.assertEqual(expected_req_resp, create_response)

        ## Short Username
        payload = {"username" : "py_luiz", "password": "python"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "Password less than 8 characters or more than 24 characters" }

        self.assertEqual(expected_req_resp, create_response)


        
