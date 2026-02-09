from __future__ import annotations

from typing import Any

import pandas as pd


class DictExtractor:
    def __init__(self, data: dict):
        self.data = data

    def extract_all(self, mapping_df: pd.DataFrame) -> dict[str, Any]:
        """Generate a dictionary by extracting values from nested data according to a mapping DataFrame.

        For each row in `mapping_df`, the function retrieves a value from `self.data` based on the
        specified `path`. If the retrieved value is `None` or an empty string, the existing key in
        the result dictionary is not overwritten. Only non-empty values will overwrite previous entries.

        Args:
            mapping_df (pd.DataFrame): DataFrame containing the mapping of data paths to dictionary keys.
                Expected columns: ["path", "dict_key"].

        Returns:
            dict[str, Any]: Dictionary where keys are taken from `dict_key` and values are extracted
            from `self.data` according to the specified paths. Empty or None values are preserved
            unless the key does not yet exist.

        """
        result = {}

        for _, row in mapping_df.iterrows():
            path = row["path"]
            key = row["dict_key"]

            value = self._get_nested_value(self.data, path)

            if value is None or value == "":
                if key not in result:
                    result[key] = ""
                continue

            result[key] = value

        return result

    def _get_nested_value(self, d: dict, path: str) -> Any | None:
        """Retrieve a nested value from a dictionary given a dot-separated path.

        Args:
            d (dict): The dictionary to traverse.
            path (str): Dot-separated path string, e.g., "key1.key2.key3".

        Returns:
            Any | None: The value found at the path, or None if any key is missing.

        """
        keys = path.split(".")
        cur = d
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return None
            cur = cur[k]
        return cur
