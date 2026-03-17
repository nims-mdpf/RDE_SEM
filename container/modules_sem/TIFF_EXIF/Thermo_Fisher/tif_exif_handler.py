from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


def convert_value(v: Any) -> float | int | str | bool:
    """Convert a value to an appropriate Python type.

    This function processes the input `v` as follows:
    - If `v` is None or an empty string (after stripping), returns an empty string.
    - If `v` represents a float or scientific notation, returns a float.
    - If `v` represents an integer, returns an int.
    - If `v` is a boolean-like string ("true", "yes", "on", "false", "no", "off"),
      returns the corresponding boolean value.
    - Otherwise, returns `v` as a stripped string.

    Args:
        v (Any): The value to convert.

    Returns:
        int | float | bool | str: The converted value based on its content.

    """
    if v is None:
        result: float | int | str | bool = ""
    else:
        v_str = str(v).strip()
        if v_str == "":
            result = ""
        else:
            try:
                result = float(v_str) if "." in v_str or "e" in v_str.lower() else int(v_str)
            except ValueError:
                low = v_str.lower()
                if low in ("true", "yes", "on"):
                    result = True
                elif low in ("false", "no", "off"):
                    result = False
                else:
                    result = v_str
    return result


def normalize_key(key: Any) -> str:
    """Normalize a string to a lowercase snake_case key.

    Spaces are replaced with underscores, camelCase is converted to snake_case,
    and all letters are lowercased.

    Args:
        key (Any): The input string to normalize.

    Returns:
        str: The normalized key in lowercase snake_case.

    """
    key = str(key).strip().replace(" ", "_")
    key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return key.lower()


class BaseExifParser(ABC):
    """Base class for EXIF format parsers."""

    @abstractmethod
    def can_parse(self, exif_data: dict[str, Any]) -> bool:
        """Check if this parser can handle the given EXIF data.

        Args:
            exif_data (dict): The EXIF data to check.

        Returns:
            bool: True if this parser can handle the data, False otherwise.

        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, exif_data: dict[str, Any]) -> dict[str, Any]:
        """Parse EXIF data into a structured format.

        Args:
            exif_data (dict): The EXIF data to parse.

        Returns:
            dict: Parsed and structured EXIF data.

        """
        raise NotImplementedError


class HeliosParser(BaseExifParser):
    """Parser for Helios INI format EXIF data."""

    def can_parse(self, exif_data: dict) -> bool:
        """Check if EXIF data is in Helios INI format.

        Args:
            exif_data (dict): The EXIF data to check.

        Returns:
            bool: True if Helios INI format is detected.

        """
        pattern = re.compile(r"^\[.*\]", re.MULTILINE)
        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value
            if isinstance(value_str, str) and pattern.search(value_str):
                return True
        return False

    def parse(self, exif_data: dict) -> dict:
        """Parse Helios INI format EXIF data.

        Args:
            exif_data (dict): The EXIF data to parse.

        Returns:
            dict: Parsed EXIF data, or empty dict if not found.

        """
        pattern = re.compile(r"^\[.*\]", re.MULTILINE)

        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value
            if isinstance(value_str, str) and pattern.search(value_str):
                return self._parse_ini(value_str)
        return {}

    def _parse_ini(self, text: str) -> dict:
        """Parse INI format text.

        Args:
            text (str): INI format text.

        Returns:
            dict: Parsed INI data.

        """
        text = (
            text.replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip("\x00")
        )
        data: dict[str, Any] = {}
        current_section: str | None = None

        for line_raw in text.split("\n"):
            line = line_raw.strip()
            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                current_section = normalize_key(line[1:-1])
                data[current_section] = {}

            elif "=" in line:
                key, value = line.split("=", 1)
                key = normalize_key(key)
                value_converted = convert_value(value)
                if current_section:
                    data[current_section][key] = value_converted
                else:
                    data[key] = value_converted

        return data
