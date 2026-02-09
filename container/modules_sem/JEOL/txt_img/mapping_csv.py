from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class TxtExtractor:
    def __init__(self, txt_file: Path):
        self.lines = self._load_and_split(txt_file)

    def _load_and_split(self, txt_file: Path) -> list[list[str]]:
        """Load a TXT file and split each line into tokens.

        Each line in the file is split by whitespace into a list of strings.
        Empty lines are ignored.

        Example:
            A line like "$CM_MODE  SEI" becomes ["$CM_MODE", "SEI"].

        Args:
            txt_file (Path): Path to the TXT file to read.

        Returns:
            list[list[str]]: A list of lines, where each line is a list of tokens.

        """
        lines = []
        with open(txt_file, encoding="utf-8") as f:
            for line in f:
                tokens = line.strip().split()
                if tokens:
                    lines.append(tokens)
        return lines

    def extract_all(self, mapping_df: pd.DataFrame) -> dict[str, Any]:
        """Generate a dictionary of values based on instrument lines and a mapping DataFrame.

        This function iterates over `self.lines`, where each line is a list of strings.
        For each line, it matches the first element (instrument name) with the
        'instrument' column in `mapping_df` to determine the corresponding dictionary key(s).

        Special cases:
        - Certain instruments (e.g., "$CM_IMAGE_SIZE", "$CM_FULL_SIZE", "$CM_STAGE_POSITION",
          "$CM_STAGE_POS", "$CM_FIELD_OF_VIEW") will map two values from the line.
        - "$CM_DATE" lines are converted to "YYYY-MM-DD" string format.

        Args:
            mapping_df (pd.DataFrame): DataFrame containing mapping of instruments to dictionary keys.
                Expected columns: ["instrument", "dict_key"].

        Returns:
            dict[str, Any]: Dictionary where keys are from `dict_key` and values are extracted from `self.lines`.

        """
        result = {}

        for linelist in self.lines:
            instrument = linelist[0]
            matched = mapping_df.query("instrument == @instrument")
            if matched.empty:
                continue

            if instrument in (
                "$CM_IMAGE_SIZE", "$CM_FULL_SIZE",
                "$CM_STAGE_POSITION", "$CM_STAGE_POS",
                "$CM_FIELD_OF_VIEW",
            ):
                result[matched.iloc[0]["dict_key"]] = linelist[1]
                result[matched.iloc[1]["dict_key"]] = linelist[2]

            elif instrument == "$CM_DATE":
                result[matched.iloc[0]["dict_key"]] = (
                    pd.to_datetime(linelist[1]).strftime("%Y-%m-%d")
                )

            else:
                result[matched.iloc[0]["dict_key"]] = linelist[1]

        return result
