import unittest
import threading
import tempfile
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer

import app


class APITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        app.DATA_FILE = Path(cls.temp_dir.name) / "messages.json"

        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), app.APIHandler
        )
        cls.port = cls.server.server_address[1]

        cls.thread = threading.Thread(
            target=cls.server.serve_forever
        )
        cls.thread.start()

        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp_dir.cleanup()

    def setUp(self):
        app.DATA_FILE.write_text("[]", encoding="utf-8")

    def test_health(self):
        response = urlopen(f"{self.base_url}/health")
        data = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(data["status"], "active")

    def test_get_messages(self):
        response = urlopen(f"{self.base_url}/messages")
        data = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(data["total"], 0)

    def test_post_message(self):
        payload = json.dumps({"message": "Pesan pengujian"}).encode()

        request = Request(
            f"{self.base_url}/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        response = urlopen(request)
        data = json.loads(response.read())

        self.assertEqual(response.status, 201)
        self.assertEqual(data["message"]["message"], "Pesan pengujian")

    def test_delete_message(self):
        app.DATA_FILE.write_text(
            json.dumps([{"message": "Pesan pengujian"}]),
            encoding="utf-8"
        )

        request = Request(
            f"{self.base_url}/messages?index=0",
            method="DELETE"
        )

        response = urlopen(request)
        data = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(data["status"], "deleted")

    def test_empty_message(self):
        payload = json.dumps({"message": ""}).encode()

        request = Request(
            f"{self.base_url}/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with self.assertRaises(HTTPError) as error:
            urlopen(request)

        self.assertEqual(error.exception.code, 400)


if __name__ == "__main__":
    unittest.main()