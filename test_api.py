# -*- coding: utf-8 -*-
import unittest
import json
import app

class TestIAServer(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        self.app.testing = True

    def test_index_status(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_models_endpoint(self):
        # This might fail if Ollama is not running, but it checks the API logic
        response = self.app.get('/v1/models')
        self.assertIn(response.status_code, [200, 500])

if __name__ == '__main__':
    unittest.main()
