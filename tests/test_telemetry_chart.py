import ast
from pathlib import Path
import unittest
from unittest.mock import Mock

import altair as alt
import pandas as pd


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_plot_telemetry_metric(streamlit):
    module = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    function = next(
        node for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "plot_telemetry_metric"
    )
    namespace = {"alt": alt, "st": streamlit}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(APP_PATH), "exec"), namespace)
    return namespace["plot_telemetry_metric"]


class TelemetryChartTests(unittest.TestCase):
    def test_only_time_axis_is_interactive_and_y_range_is_fixed(self):
        for values, expected_domain in [([2.0, 8.0], [2.0, 8.0]), ([4.0, 4.0], [3.8, 4.2])]:
            with self.subTest(values=values):
                streamlit = Mock()
                plot_metric = load_plot_telemetry_metric(streamlit)
                frame = pd.DataFrame({
                    "timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                    "temperature": values,
                })

                plot_metric(frame, "temperature")

                chart = streamlit.altair_chart.call_args.args[0]
                spec = chart.to_dict()
                self.assertEqual(spec["params"][0]["select"]["encodings"], ["x"])
                self.assertEqual(spec["params"][0]["bind"], "scales")
                self.assertEqual(spec["encoding"]["y"]["scale"]["domain"], expected_domain)
                self.assertFalse(spec["encoding"]["y"]["scale"]["zero"])


if __name__ == "__main__":
    unittest.main()
