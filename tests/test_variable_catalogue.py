import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_stations import load_files  # noqa: E402

CAMEL_CASE = re.compile(r"^[a-z][a-zA-Z0-9]*$")

CATALOGUE = json.loads((ROOT / "variables" / "station_variables.json").read_text(encoding="utf-8"))


class VariableCatalogueTest(unittest.TestCase):
    def test_every_entry_has_a_name_a_unit_and_a_consistent_range(self):
        for key, entry in CATALOGUE.items():
            with self.subTest(variable=key):
                self.assertTrue(entry.get("name"))
                self.assertTrue(entry.get("unit"))
                self.assertLessEqual(entry["minValue"], entry["maxValue"])

    def test_keys_are_camel_case_like_the_station_files(self):
        for key in CATALOGUE:
            with self.subTest(variable=key):
                self.assertRegex(key, CAMEL_CASE)

    def test_every_variable_used_by_a_station_is_in_the_catalogue(self):
        contents, _ = load_files(ROOT / "stations")
        used = {key for stations in contents.values() for station in stations for key in station["variables"]}
        self.assertEqual(sorted(used - set(CATALOGUE)), [])

    def test_plausible_limits_do_not_cut_off_real_observations(self):
        # Seen on the IWOOS buoys on 2026-11-12: wave period 15 s, wave height 0.14 m.
        self.assertGreaterEqual(CATALOGUE["wavePeriodLow"]["maxValue"], 20)
        self.assertGreaterEqual(CATALOGUE["wavePeriodHigh"]["maxValue"], 20)
        # Seawater freezes at about -1.9 degC; readings of -14 degC are a sensor fault.
        self.assertGreaterEqual(CATALOGUE["seaTemperature"]["minValue"], -3)
        self.assertLessEqual(CATALOGUE["seaTemperature"]["maxValue"], 40)


if __name__ == "__main__":
    unittest.main()
