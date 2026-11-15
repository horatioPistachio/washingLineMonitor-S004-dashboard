import os
from pathlib import Path
import unittest
from unittest.mock import Mock, PropertyMock, patch

import streamlit as st
from streamlit.runtime.context import ContextProxy
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class GlancesLinkTests(unittest.TestCase):
    def test_browser_link_and_internal_api_endpoint(self):
        cases = [
            ("192.168.1.25:8501", "", "http://192.168.1.25:61208"),
            ("localhost:8501", "", "http://localhost:61208"),
            ("[2001:db8::1]:8501", "", "http://[2001:db8::1]:61208"),
            ("192.168.1.25:8501", "https://monitor.example/glances", "https://monitor.example/glances"),
            ("", "", None),
            ("[invalid", "", None),
        ]
        for host, public_url, expected in cases:
            with self.subTest(host=host, public_url=public_url):
                st.cache_data.clear()
                env = {
                    "API_ENDPOINT": "http://app:8000",
                    "GLANCES_ENDPOINT": "http://glances:61208",
                    "GLANCES_PUBLIC_URL": public_url,
                }
                with patch.dict(os.environ, env), \
                     patch.object(ContextProxy, "headers", new_callable=PropertyMock, return_value={"host": host}), \
                     patch("requests.get", return_value=Mock(status_code=503)) as get:
                    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()

                self.assertFalse(app.exception)
                links = [item.value for item in app.markdown if "View Detailed System Stats" in item.value]
                if expected:
                    self.assertEqual(len(links), 1)
                    self.assertIn(f"]({expected})", links[0])
                else:
                    self.assertFalse(links)
                    self.assertTrue(any("GLANCES_PUBLIC_URL" in item.value for item in app.warning))
                self.assertTrue(any(call.args[0] == "http://glances:61208/api/4/all" for call in get.call_args_list))


if __name__ == "__main__":
    unittest.main()
