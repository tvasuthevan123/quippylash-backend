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
prompts_container = db_client.get_container_client(config.settings['prompts_container'])

request_url = config.settings['cloud_URI'] + 'prompt/delete/'

class TestFunction(unittest.TestCase):

     ## Setup test players
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.maxDiff=None
            players_container.create_item({'id': 'py_luis', 'password': 'pythonrulz'})
            players_container.create_item({'id': 'py_thanuj', 'password': 'javascriptrulz'})
        except Exception as e:
            # print(repr(e))
            raise unittest.SkipTest(repr(e))

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
            players_container.delete_item(item='py_thanuj', partition_key='py_thanuj')
            prompts_container.delete_item(item="0", partition_key="0")
            prompts_container.delete_item(item="1", partition_key="1")
        except Exception as e:
            # print(repr(e))
            pass

    def setUp(self) -> None:
        try:
            prompts_container.create_item({'id': '0', 'text': 'What is an Azure Function used for?', 'username': 'py_luis'})
            prompts_container.create_item({'id': '1', 'text': 'What is an Python Function used for?', 'username': 'py_thanuj'})
        except Exception as e:
            # print(repr(e))
            pass

    def test_delete_prompt__valid(self):
        payload = {"id": 0, "username" : "py_luis", "password": "pythonrulz"}

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        delete_response = wrapper.prompt_delete(payload, local=True)

        all_prompts = list(prompts_container.read_all_items())
        self.assertEqual(1, len(all_prompts))

        remaining_prompt = all_prompts[0]
        del remaining_prompt['_attachments']
        del remaining_prompt['_etag']
        del remaining_prompt['_rid']
        del remaining_prompt['_self']
        del remaining_prompt['_ts']
        del remaining_prompt['id']

        expected_prompt = {
            "username": "py_thanuj",
            "text": "What is an Python Function used for?"
        }

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_prompt, remaining_prompt)
        self.assertEqual(expected_req_resp, delete_response)

    def test_delete_prompt__nonexistent_id(self):
        payload = {"id": 2, "text": "What is an GoogleAppEngine function used for?", "username" : "py_luis", "password": "pythonrulz"}

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        edit_response = wrapper.prompt_delete(payload, local=True)

        expected_req_resp = {"result" : False, "msg": "prompt id does not exist" }

        self.assertEqual(expected_req_resp, edit_response)

    def test_delete_prompt__invalid_user(self):
        # Incorrect password
        payload = {"id": 0, "username" : "py_luis", "password": "pythonwrong"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        delete_response = wrapper.prompt_delete(payload, local=True)

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, delete_response)

        # Nonexistent username
        payload = {"id": 0, "username" : "py_nonexistent", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        delete_response = wrapper.prompt_delete(payload, local=True)

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, delete_response)

    def test_delete_prompt__wrong_prompt_user(self):
        # Incorrect password
        payload = {"id": 1, "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            headers={'x-functions-key' : config.settings['APP_KEY']},
            json=payload
        )

        delete_response = wrapper.prompt_delete(payload, local=True)

        expected_req_resp = {"result" : False, "msg": "access denied" }

        self.assertEqual(expected_req_resp, delete_response)

        