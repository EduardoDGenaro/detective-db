from pathlib import Path
import sys
import unittest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from components.investigation import camera_matches


class ComparisonTests(unittest.TestCase):
    def test_camera_comparison_uses_suspect_location_and_dbt_minute_window(self):
        statement = {"suspect_id": "S001", "claimed_location_id": "L001", "claimed_event_time": "2026-10-14 22:15:59"}
        cameras = pd.DataFrame([
            {"camera_event_id": "C1", "suspect_id": "S001", "location_id": "L002", "seen_at": "2026-10-14 22:10:01"},
            {"camera_event_id": "C2", "suspect_id": "S001", "location_id": "L001", "seen_at": "2026-10-14 22:15:00"},
            {"camera_event_id": "C3", "suspect_id": "S002", "location_id": "L002", "seen_at": "2026-10-14 22:15:00"},
            {"camera_event_id": "C4", "suspect_id": "S001", "location_id": "L002", "seen_at": "2026-10-14 22:21:00"},
        ])
        self.assertEqual(camera_matches(statement, cameras).camera_event_id.tolist(), ["C1", "C2"])
        self.assertEqual(camera_matches(statement, cameras, conflicts_only=True).camera_event_id.tolist(), ["C1"])


if __name__ == "__main__":
    unittest.main()
