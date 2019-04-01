"""
Run all the tests without using unit test discovery.
"""
import unittest

from pi_fly.test.test_polling_loop import TestPollingLoop
from pi_fly.test.test_web_views import TestWebViews

if __name__ == "__main__":
    unittest.main()
