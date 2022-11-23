"""
Created on 7 Jan 2021

@author: si
"""
from flask import current_app

from pi_fly.scoreboard import ScoreBoard
from pi_fly.test.test_base import BaseTest
from pi_fly.utils import load_from_file
from pi_fly.web_sessions import SESSION_COOKIE_NAME, session_token_create
from pi_fly.web_view import create_app


class TestWebSessions(BaseTest):
    def setUp(self):
        super().setUp()

        self.scoreboard = ScoreBoard()
        self.app = create_app(self.profile, self.scoreboard)
        self.test_client = self.app.test_client()

        # useful when using DB in memory
        self.request_context = self.app.test_request_context()
        self.request_context.push()

    def tearDown(self):
        super().tearDown()
        self.request_context.pop()

    def test_no_cookie_redirects(self):
        rv = self.test_client.get("/run_command/")
        self.assertEqual(302, rv.status_code)

    def test_login(self):

        d = {"password": "incorrectpassword"}
        rv = self.test_client.post("/login/", data=d, follow_redirects=False)
        self.assertEqual(401, rv.status_code)

        d = {"password": load_from_file("test/data/session_password")}
        rv = self.test_client.post("/login/", data=d, follow_redirects=False)
        self.assertEqual(302, rv.status_code)

        # Find auth session cookie
        session_id = ""
        for cookie in self.test_client.cookie_jar:
            if cookie.name == SESSION_COOKIE_NAME:
                session_id = cookie.value
                break
        self.assertTrue(session_id != "", "Session cookie not found")

    def test_restricted_page(self):

        secret_key = current_app.config["SESSION_PASSWORD"]
        valid_session_token = session_token_create(secret_key)
        self.test_client.set_cookie("localhost", SESSION_COOKIE_NAME, valid_session_token)

        rv = self.test_client.get("/run_command/")
        self.assertEqual(200, rv.status_code)

    def test_invalid_token(self):
        invalid_token = "xxxxx:a01e2608a63d6dc8c2b80118983a83172d13c7ec"
        self.test_client.set_cookie("localhost", SESSION_COOKIE_NAME, invalid_token)
        rv = self.test_client.get("/run_command/")
        self.assertEqual(302, rv.status_code)
