import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from CreatePrompt import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

players_container = db_client.get_container_client(config.settings['players_container'])
prompts_container = db_client.get_container_client(config.settings['prompts_container'])

request_url = 'http://localhost:7071/api/prompt/create/'

class TestFunction(unittest.TestCase):

    ## Setup test players
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.maxDiff=None
            players_container.create_item({'id': 'py_luis', 'password': 'pythonrulz'})
            players_container.create_item({'id': 'py_thanuj', 'password': 'javascriptrulz'})
            # if len(list(prompts_container.read_all_items()))>0:
            #     raise Exception('Setup Failed - Empty propmts container before test')
        except Exception as e:
            print(repr(e))
            raise unittest.SkipTest(repr(e))

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            players_container.delete_item(item='py_luis', partition_key='py_luis')
            players_container.delete_item(item='py_thanuj', partition_key='py_thanuj')
        except Exception as e:
            print(repr(e))

    # Remove test prompt from container after each test
    def tearDown(self):
        try:
            all_prompts = list(prompts_container.query_items(
                query="SELECT c.id FROM c",
                enable_cross_partition_query=True
            ))
            for prompt in all_prompts:
                prompts_container.delete_item(item=prompt['id'], partition_key=prompt['id'])
        except Exception as e:
            print(repr(e))

    def test_create_prompt__valid(self):
        # Test adding same prompt by 2 different users to check it gets added to both.
        payload = {"text": "What is an Azure function used for?", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

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
            "text": "What is an Azure function used for?"
        }

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_prompt, test_prompt)
        self.assertEqual(expected_req_resp, create_response)

        # Same text, different user
        payload = {"text": "What is an Azure function used for?", "username" : "py_thanuj", "password": "javascriptrulz"}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        all_prompts = list(prompts_container.read_all_items())
        test_prompt = all_prompts[1]

        del test_prompt['_attachments']
        del test_prompt['_etag']
        del test_prompt['_rid']
        del test_prompt['_self']
        del test_prompt['_ts']
        del test_prompt['id']

        expected_prompt = {
            "username": "py_thanuj",
            "text": "What is an Azure function used for?"
        }

        expected_req_resp = {"result" : True, "msg": "OK" }

        self.assertEqual(expected_prompt, test_prompt)
        self.assertEqual(expected_req_resp, create_response)

    def test_create_prompt__duplicate(self):
        existing_prompt = {
            "id": "0",
            "text": "What is an Azure function used for?",
            "username": "py_luis"
        }

        prompts_container.create_item(existing_prompt)

        payload={
            "text": "What is an Azure function used for?",
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

    def test_create_prompt__invalid_prompt(self):
        # Long prompt
        payload = {"text": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean ma", "username" : "py_luis", "password": "pythonrulz"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "prompt length is <20 or > 100 characters" }

        self.assertEqual(expected_req_resp, create_response)

        ## Short prompt
        payload = {"text": "Short prompt", "username" : "py_luis", "password": "pythonrulz"}

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

        expected_req_resp = {"result" : False, "msg": "prompt length is <20 or > 100 characters" }

        self.assertEqual(expected_req_resp, create_response)

    def test_create_prompt__invalid_user(self):
        # Incorrect password
        payload = {"text": "Good question to be inserted here?", "username" : "py_luis", "password": "pythonwrong"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, create_response)

        # Nonexistent username
        payload = {"text": "Good question to be inserted here?", "username" : "py_nonexistent", "password": "pythonwrong"}

        resp = requests.post(
            # Request URL ((Use config)
            request_url,
            json=payload
        )

        create_response = resp.json()

        expected_req_resp = {"result" : False, "msg": "bad username or password" }

        self.assertEqual(expected_req_resp, create_response)

        
