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

prompts_container = db_client.get_container_client(config.settings['prompts_container'])

request_url = 'http://localhost:7071/api/prompts/get/'

class TestFunction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        try:
            prompts_container.create_item({'id': '0', 'text': 'Q1', 'username': 'py_luis'})
            prompts_container.create_item({'id': '1', 'text': 'Q2', 'username': 'py_thanuj'})
            prompts_container.create_item({'id': '2', 'text': 'Q3', 'username': 'py_thanuj'})
            prompts_container.create_item({'id': '3', 'text': 'Q4', 'username': 'py_luis'})
            prompts_container.create_item({'id': '4', 'text': 'Q5', 'username': 'py_luis'})
        except Exception as e:
            # print(repr(e))
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            prompts_container.delete_item(item="0", partition_key="0")
            prompts_container.delete_item(item="1", partition_key="1")
            prompts_container.delete_item(item="2", partition_key="2")
            prompts_container.delete_item(item="3", partition_key="3")
            prompts_container.delete_item(item="4", partition_key="4")
        except Exception as e:
            # print(repr(e))
            pass

    def test_get_prompts__prompt_num(self):
        payload = {"prompts": 3}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        
        expected_list_size = 3
        self.assertEqual(expected_list_size, len(actual_list))

    def test_get_prompts__prompts_all(self):
        payload = {"prompts": 5}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '2', 'text': 'Q3', 'username': 'py_thanuj'},
            {'id': '3', 'text': 'Q4', 'username': 'py_luis'},
            {'id': '4', 'text': 'Q5', 'username': 'py_luis'},
            {'id': '0', 'text': 'Q1', 'username': 'py_luis'},
            {'id': '1', 'text': 'Q2', 'username': 'py_thanuj'}
        ]
        self.assertEqual(expected_list, actual_list)

        payload = {"prompts": 6}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '2', 'text': 'Q3', 'username': 'py_thanuj'},
            {'id': '3', 'text': 'Q4', 'username': 'py_luis'},
            {'id': '4', 'text': 'Q5', 'username': 'py_luis'},
            {'id': '0', 'text': 'Q1', 'username': 'py_luis'},
            {'id': '1', 'text': 'Q2', 'username': 'py_thanuj'}
        ]
        self.assertEqual(expected_list, actual_list)

    def test_get_prompts__players_valid(self):
        payload = {"players": ['py_luis']}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '3', 'text': 'Q4', 'username': 'py_luis'},
            {'id': '4', 'text': 'Q5', 'username': 'py_luis'},
            {'id': '0', 'text': 'Q1', 'username': 'py_luis'}
        ]
        self.assertEqual(expected_list, actual_list)

        payload = {"players": ['py_thanuj']}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '2', 'text': 'Q3', 'username': 'py_thanuj'},
            {'id': '1', 'text': 'Q2', 'username': 'py_thanuj'}
        ]
        self.assertEqual(expected_list, actual_list)

    def test_get_prompts__players_invalid(self):
        payload = {"players": ['py_luis', 'py_nothere']}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '3', 'text': 'Q4', 'username': 'py_luis'},
            {'id': '4', 'text': 'Q5', 'username': 'py_luis'},
            {'id': '0', 'text': 'Q1', 'username': 'py_luis'}
        ]
        self.assertEqual(expected_list, actual_list)

        payload = {"players": ['py_thanuj', 'py_nothere']}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        expected_list = [
            {'id': '2', 'text': 'Q3', 'username': 'py_thanuj'},
            {'id': '1', 'text': 'Q2', 'username': 'py_thanuj'}
        ]
        self.assertEqual(expected_list, actual_list)

        payload = {"players": ['py_nothere']}

        resp = requests.post(
            # Request URL (Use config)
            request_url,
            json=payload
        )

        actual_list = list(resp.json())
        self.assertEqual(0, len(actual_list))
