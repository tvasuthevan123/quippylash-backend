import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from LoginPlayer import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

players_container = db_client.get_container_client(config.settings['players_container'])

request_url = 'http://localhost:7071/api/player/login/'

class TestFunction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        try:
            players_container.create_item({'id': 'py_luis', 'password': 'pythonrulz'})
        except Exception as e:
            print(repr(e))

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
        except Exception as e:
            print(repr(e))

    def test_login_player__valid(self):
        payload = {"username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": True , "msg" : "OK"}

        self.assertEqual(expected_response, create_response)

    def test_login_player__incorrect_username(self):
        payload = {"username" : "incorrect", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

    def test_login_player__incorrect_password(self):
        payload = {"username" : "py_luis", "password": "wrongpassword"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

    def test_login_player__impossible_values(self):
        payload = {"username" : "impossibleusernameinsertedhere---------", "password": "ValidPasswordLength"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

        payload = {"username" : "123", "password": "ValidPasswordLength"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

        payload = {"username" : "ValidUserLength", "password": "qwoidjqwoidjqdjqoiwdjqoiwdj"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

        payload = {"username" : "ValidUserLength", "password": "qwe"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()
        expected_response = {"result": False , "msg": "Username or password incorrect"}

        self.assertEqual(expected_response, create_response)

