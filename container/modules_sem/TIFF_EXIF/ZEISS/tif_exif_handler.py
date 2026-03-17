from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

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


class CrossBeam550Auto:
    """Parser for CrossBeam 550 Auto SEM XML data."""

    def __init__(self, data: dict | None = None):
        """Initialize the CrossBeam550Auto instance.

        Args:
            data (dict | None): Optional initial data. Defaults to an empty dictionary if None.

        """
        self.data: dict = data or {}

    def from_xml(self, xml_str: str) -> CrossBeam550Auto:
        """Parse an XML string and populate the instance data.

        Args:
            xml_str (str): XML content as a string.

        Returns:
            CrossBeam550Auto: The instance itself with updated data.

        """
        root = fromstring(xml_str)
        self.data = self._xml_to_dict(root)
        self.data = self._post_process(self.data)
        return self

    def _split_value_unit(self, text: Any) -> tuple[Any, str | None]:
        """Split a string into a value and a unit.

        If the input contains multiple space-separated parts, the first part
        is treated as the value and the rest as the unit. Non-string inputs
        are returned as-is with unit None.

        Args:
            text (Any): The input to split.

        Returns:
            tuple[Any, str | None]: A tuple of (value, unit). If there is no unit,
            the second element is None.

        """
        if not isinstance(text, str):
            return text, None
        parts = text.strip().split()
        if len(parts) == 1:
            return parts[0], None
        return parts[0], " ".join(parts[1:])

    def to_dict(self) -> dict:
        """Return the internal data as a dictionary.

        Returns:
            dict: The internal data stored in the instance.

        """
        return self.data

    def _xml_to_dict(self, elem: Element) -> dict[str, Any]:
        """Recursively convert an XML element and its children into a dictionary.

        Special handling is done for `<item name="...">` elements by splitting
        their text into value and unit and storing them under an "items" key.

        Args:
            elem (Element): The XML element to convert.

        Returns:
            dict[str, Any]: A dictionary representation of the XML element and its children.

        """
        d: dict[str, Any] = {}

        for child in elem:
            tag = child.tag.lower()

            if tag == "item" and "name" in child.attrib:
                name = child.attrib["name"]

                raw = (child.text or "").strip()
                value, unit = self._split_value_unit(raw)

                if "items" not in d:
                    d["items"] = {}

                d["items"][name] = {
                    "value": value,
                    "unit": unit,
                }
                continue

            value = self._xml_to_dict(child) if len(child) else child.text

            if tag in d:
                if not isinstance(d[tag], list):
                    d[tag] = [d[tag]]
                d[tag].append(value)
            else:
                d[tag] = value

        return d

    def _post_process(self, data: Any) -> Any:
        """Recursively process input data.

        Normalize numeric values and handle image aperture
        information. If input is a list, recursively process
        each element. If input is a dictionary, convert
        'value' fields under 'items' key to numeric values
        using PrefixedTextParser.extract_numeric. If an
        'image' key exists, parse and normalize aperture
        information. For other data types, return unchanged.

        Args:
            data (Any): The input data to process.

        Returns:
            Any: Processed data with numeric values converted.

        """
        if isinstance(data, list):
            return [self._post_process(v) for v in data]

        if isinstance(data, dict):
            new = {}
            for k, v in data.items():
                if k == "items" and isinstance(v, dict):
                    new[k] = self._process_items(v)
                else:
                    new[k] = self._post_process(v)

            if "image" in new:
                self._process_image_aperture(new["image"])

            return new

        return data

    def _process_items(self, items: dict) -> dict:
        fixed = {}
        for name, item in items.items():
            val = item.get("value")
            unit = item.get("unit")
            num = PrefixedTextParser.extract_numeric(str(val))
            fixed[name] = {
                "value": num,
                "unit": unit,
            }
        return fixed

    def _process_image_aperture(self, image: dict) -> None:
        aperture_key = "aperture" if "aperture" in image else "Aperture"
        if aperture_key not in image:
            return

        value = image[aperture_key]
        if not isinstance(value, str):
            return

        parsed_aperture = self._parse_aperture(value)
        image.update(parsed_aperture)

        if aperture_key != "aperture":
            del image[aperture_key]

    def _parse_aperture(self, aperture_str: str) -> dict:
        """Parse aperture string into components."""
        result: dict[str, Any] = {
            "acc_voltage": None,
            "acc_voltage_unit": None,
            "aperture_size_value": None,
            "aperture_size_unit": None,
            "aperture_unit": None,
        }
        try:
            parts = [p.strip() for p in aperture_str.split("|")]
            if len(parts) >= 1:
                val, unit = self._split_value_unit(parts[0])
                result["acc_voltage"] = (
                    PrefixedTextParser.extract_numeric(val)
                )
                result["acc_voltage_unit"] = unit
            min_parts = 2
            if len(parts) >= min_parts:
                pattern = r"([\d\.]+)\s*(\w+)\s*(?:\[(\w+)\])?"
                match = re.match(pattern, parts[1])
                if match:
                    result["aperture_size_value"] = (
                        PrefixedTextParser.extract_numeric(
                            match.group(1),
                        )
                    )
                    result["aperture_size_unit"] = match.group(2)
                    if match.group(3):
                        result["aperture_unit"] = match.group(3)
        except (ValueError, AttributeError, IndexError) as exc:
            logger.exception("Error parsing aperture: %s", exc)
        return result


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


class FibicsParser(BaseExifParser):
    """Parser for Fibics XML format EXIF data."""

    DATE_TIME_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    )

    def can_parse(self, exif_data: dict) -> bool:
        """Check if EXIF data is in Fibics XML format.

        Args:
            exif_data (dict): The EXIF data to check.

        Returns:
            bool: True if Fibics XML format is detected.

        """
        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value

            if (
                isinstance(value_str, str)
                and "<Fibics" in value_str
                and "xml version" in value_str
            ):
                return True
        return False

    def parse(self, exif_data: dict) -> dict:
        """Parse Fibics XML format EXIF data.

        Args:
            exif_data (dict): The EXIF data to parse.

        Returns:
            dict: Parsed EXIF data, or empty dict on error.

        """
        xml_str = ""
        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value

            if isinstance(value_str, str) and "xml version" in value_str:
                start_idx = value_str.find("<Fibics")
                end_idx = value_str.find("Fibics>") + len("Fibics>")
                if start_idx != -1 and end_idx != -1:
                    xml_str = value_str[start_idx:end_idx]
                    break

        if not xml_str:
            return {}

        try:
            model = CrossBeam550Auto().from_xml(xml_str)
            data = model.to_dict()
            return self._convert_all_values(data)
        except (ValueError, TypeError) as exc:
            logger.exception("Error parsing Fibics XML: %s", exc)
            return {}

    def _convert_all_values(
        self,
        data: dict[str, Any],
        parent_key: str | None = None,
    ) -> dict[str, Any]:
        """Convert all values in data structure recursively.

        Args:
            data (Any): The data to convert.
            parent_key (str | None): The parent key for context.

        Returns:
            Any: Converted data.

        """
        return self._convert_all_values_impl(data, parent_key)

    def _convert_all_values_impl(
        self,
        data: dict[str, Any],
        parent_key: str | None = None,
    ) -> dict[str, Any]:
        """Convert values.

        Args:
            data (Any): The data to convert.
            parent_key (str | None): The parent key for context.

        Returns:
            Any: Converted data.

        """
        if isinstance(data, dict):
            return {
                k: self._convert_all_values_impl(v, parent_key=k)
                for k, v in data.items()
            }

        if isinstance(data, list):
            return [
                self._convert_all_values_impl(v, parent_key=parent_key)
                for v in data
            ]

        if isinstance(data, str):
            if parent_key == "aperture":
                return data
            if self.DATE_TIME_PATTERN.match(data.strip()):
                return data
            numeric = self._extract_numeric(data)
            return numeric if isinstance(numeric, (int, float)) else convert_value(data)

        return data

    @staticmethod
    def _extract_numeric(raw_value: str) -> float | int | str:
        """Extract numeric value from raw string.

        Args:
            raw_value (str): Raw value string.

        Returns:
            float | int | str: Extracted numeric value or original string.

        """
        if not isinstance(raw_value, str):
            return raw_value

        raw_value = raw_value.strip()

        match = re.match(
            r"^\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)",
            raw_value,
            re.IGNORECASE,
        )
        if match:
            n = match.group(1)
            try:
                v = float(n)
                if v.is_integer():
                    return int(v)
                return v
            except ValueError as exc:
                logger.debug("Error converting to float: %s", exc)
                return raw_value

        return raw_value


class PrefixedTextParser(BaseExifParser):
    """Parser for prefixed text format EXIF data."""

    PREFIX_PATTERN = re.compile(
        r"^(AP_|SV_|DP_)",
        re.MULTILINE,
    )

    KEY_VALUE_PATTERN = re.compile(
        r"""
        (?P<key>(?:AP_|SV_|DP_)\w+)\b
        (?:[\s\n]+
            (?P<title>[^:=\n]+?)\s*[:=]\s*
            (?P<value>.*?)
        )?
        (?=\s+(?:AP_|SV_|DP_)\w+|$)
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )

    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}:\d{2}$")

    @staticmethod
    def extract_numeric(raw_value: str) -> float | int | str:
        """Extract numeric value from raw string.

        Example: '2.32 A' -> 2.32

        Args:
            raw_value (str): Raw value string.

        Returns:
            float | int | str: Extracted numeric or original string.

        """
        if not isinstance(raw_value, str):
            return raw_value

        raw_value = raw_value.strip()

        match = re.match(
            r"^\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)",
            raw_value,
            re.IGNORECASE,
        )

        if match:
            n = match.group(1)
            try:
                v = float(n)
                if v.is_integer():
                    return int(v)
                return v
            except ValueError as exc:
                logger.debug("Error converting to float: %s", exc)
                return raw_value
        return raw_value

    def can_parse(self, exif_data: dict) -> bool:
        """Check if EXIF data is in prefixed text format.

        Args:
            exif_data (dict): The EXIF data to check.

        Returns:
            bool: True if prefixed text format is detected.

        """
        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value

            if (
                isinstance(value_str, str)
                and self.PREFIX_PATTERN.search(value_str)
            ):
                return True
        return False

    def parse(self, exif_data: dict) -> dict:
        """Parse prefixed text format EXIF data.

        Args:
            exif_data (dict): The EXIF data to parse.

        Returns:
            dict: Parsed EXIF data, or empty dict if not found.

        """
        for value in exif_data.values():
            if isinstance(value, bytes):
                try:
                    value_str = value.decode(errors="ignore")
                except UnicodeDecodeError as exc:
                    logger.debug("Decode error: %s", exc)
                    continue
            else:
                value_str = value

            if (
                isinstance(value_str, str)
                and self.PREFIX_PATTERN.search(value_str)
            ):
                flat = self._parse_prefixed_text(value_str)
                return self._classify(flat)

        return {}

    def _classify(self, flat: dict) -> dict:
        structured: dict[str, dict] = {
            "systemval": {},
            "aperture": {},
            "detection": {},
        }

        for key, val in flat.items():
            if key.startswith("sv_"):
                structured["systemval"][key.replace("sv_", "")] = val
            elif key.startswith("ap_"):
                structured["aperture"][key.replace("ap_", "")] = val
            elif key.startswith("dp_"):
                structured["detection"][key.replace("dp_", "")] = val
            else:
                structured["systemval"][key] = val

        return structured

    @staticmethod
    def _parse_date_string(s: str) -> str | None:
        """Convert date string to ISO format.

        Args:
            s (str): Date string to parse.

        Returns:
            str | None: ISO format date or None.

        """
        if not s or not isinstance(s, str):
            return None
        for fmt in ("%d %b %Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s.strip(), fmt).replace(tzinfo=timezone.utc)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def _is_date_or_time(self, s: str) -> bool:
        """Check if string is a date or time.

        Args:
            s (str): String to check.

        Returns:
            bool: True if string is a date or time.

        """
        if not isinstance(s, str):
            return False
        s = s.strip()
        if self.DATE_PATTERN.match(s) or self._parse_date_string(s):
            return True
        return bool(self.TIME_PATTERN.match(s))

    def _parse_prefixed_text(self, text: str) -> dict:
        """Parse prefixed text format.

        Args:
            text (str): Prefixed text to parse.

        Returns:
            dict: Parsed key-value pairs.

        """
        text = (
            text.replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip("\x00")
        )
        data: dict[str, Any] = {}

        for match in self.KEY_VALUE_PATTERN.finditer(text):
            key = normalize_key(match.group("key"))
            raw_value = match.group("value")

            if raw_value is None:
                data[key] = ""
                continue

            raw_value = raw_value.strip()

            if key.startswith("ap_"):
                iso_date = self._parse_date_string(raw_value)
                if iso_date:
                    data[key] = iso_date
                elif self.TIME_PATTERN.match(raw_value):
                    data[key] = raw_value
                else:
                    data[key] = self.extract_numeric(raw_value)
                continue

            data[key] = convert_value(raw_value)

        return data
