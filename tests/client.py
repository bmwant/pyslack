# coding: utf-8

import datetime
import unittest

from mock import Mock, patch

import pyslack


class ClientTest(unittest.TestCase):
    token = "my token"

    def setUp(self):
        self.client = pyslack.SlackClient(self.token)

    @patch('requests.post')
    def test_post_message(self, r_post):
        """A message can be posted to a channel"""
        reply = {'ok': True}
        r_post.return_value.json = Mock(return_value=reply)

        result = self.client.chat_post_message('#channel', 'message')
        self.assertEqual(reply, result)

    @patch('requests.post')
    def test_user_post_message(self, r_post):
        self.client.chat_post_message = Mock()

        reply = {
            'ok': True,
            'channel': {'id': 'C1234567890'},
        }
        r_post.return_value.json = Mock(return_value=reply)
        self.client.user_post_message('U1234567890', 'message')
        self.client.chat_post_message.assert_called_once_with('C1234567890', 'message')

    @patch('requests.post')
    def test_error_response(self, r_post):
        """Server error messages are handled gracefully"""

        reply = {"ok": False, "error": "There was an error"}
        r_post.return_value.json.return_value = reply

        with self.assertRaises(pyslack.SlackError) as context:
            self.client.chat_post_message('#channel', 'message')

        self.assertEqual(context.exception.message, reply["error"])

    @patch('requests.post')
    def test_rate_limit(self, r_post):
        """HTTP 429 Too Many Requests response is handled gracefully"""

        reply = {"ok": False, "error": "Too many requests"}
        r_post.return_value = Mock(status_code=429, headers={'retry-after': 10})
        r_post.return_value.json.return_value = reply

        with self.assertRaises(pyslack.SlackError) as context:
            self.client.chat_post_message('#channel', 'message')

        self.assertEqual(r_post.call_count, 1)
        self.assertGreater(self.client.blocked_until,
                datetime.datetime.utcnow() + datetime.timedelta(seconds=8))

        # A second send attempt should also throw, but without creating a request
        with self.assertRaises(pyslack.SlackError) as context:
            self.client.chat_post_message('#channel', 'message')

        self.assertEqual(r_post.call_count, 1)

        # After the time has expired, it should be business as usual
        self.client.blocked_until = datetime.datetime.utcnow() - \
                datetime.timedelta(seconds=5)

        r_post.return_value = Mock(status_code=200)
        r_post.return_value.json.return_value = {"ok": True}

        self.client.chat_post_message('#channel', 'message')
        self.assertEqual(r_post.call_count, 2)
