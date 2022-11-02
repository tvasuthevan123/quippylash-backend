import unittest
import json
import requests 

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
prompts_container = db_client.get_container_client(config.settings['prompts_container'])

request_url = 'http://localhost:7071/api/prompt/edit/'

class TestFunction(unittest.TestCase):

     ## Setup test players
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.maxDiff=None
            players_container.create_item({'id': 'py_luis', 'password': 'pythonrulz'})
            prompts_container.create_item({'id': '0', 'text': 'What is an Azure Function used for?', 'username': 'py_luis'})
            prompts_container.create_item({'id': '1', 'text': 'What is an Python Function used for?', 'username': 'py_luis'})
        except Exception as e:
            print(repr(e))
            raise unittest.SkipTest(repr(e))

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
            prompts_container.delete_item(item="0", partition_key="0")
            prompts_container.delete_item(item="1", partition_key="1")
        except Exception as e:
            print(repr(e))

    # def setUp(self) -> None:
    #     try:
    #         players_container.create_item({"id" : "py_luis", "password": "pythonrulz" , "games_played" : 542 , "total_score" : 3744})
    #     except Exception as e:
    #         print(repr(e))

    # def tearDown(self) -> None:
    #     try:
    #         players_container.delete_item(item='py_luis', partition_key='py_luis')
    #     except Exception as e:
    #         print(repr(e))

    def test_edit_prompt__valid(self):
        payload = {"id": 0, "text": "What is an GoogleAppEngine function used for?", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        all_prompts = list(prompts_container.read_all_items())
        test_prompt = all_prompts[0]

        del test_prompt['_attachments']
        del test_prompt['_etag']
        del test_prompt['_rid']
        del test_prompt['_self']
        del test_prompt['_ts']
        del test_prompt['id']

        expected_prompt = {
            "username": "py_luis",
            "text": "What is an GoogleAppEngine function used for?"
        }

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_prompt, test_prompt)
        self.assertEqual(expected_req_resp, edit_response)

    def test_edit_prompt__nonexistent_id(self):
        payload = {"id": 2, "text": "What is an GoogleAppEngine function used for?", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "prompt id does not exist" }

        self.assertEqual(expected_req_resp, edit_response)

    def test_edit_prompt__invalid_prompt_length(self):
        # Long prompt
        payload = {"id": 1, "text": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean ma", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "prompt length is <20 or >100 characters" }

        self.assertEqual(expected_req_resp, edit_response)

        # Short prompt
        payload = {"id": 1, "text": "Short prompt", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "prompt length is <20 or >100 characters" }

        self.assertEqual(expected_req_resp, edit_response)

    def test_edit_prompt__invalid_user(self):
        # Incorrect password
        payload = {"id": 0, "text": "Good question to be inserted here?", "username" : "py_luis", "password": "pythonwrong"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, edit_response)

        # Nonexistent username
        payload = {"id": 0, "text": "Good question to be inserted here?", "username" : "py_nonexistent", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        edit_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, edit_response)

    def test_edit_prompt__duplicate(self):
        payload={
            "id": "0",
            "text": "What is an Python Function used for?",
            "username": "py_luis",
            "password": "pythonrulz"
        }

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "This user already has a prompt with the same text" }

        self.assertEqual(expected_req_resp, create_response)
