from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Sequence
from typing import Any
from xml.etree.ElementTree import Element

import pandas as pd
from defusedxml.ElementTree import parse

NS = {'ns': 'http://www.maiml.org/schemas'}


class XmlExtractor:
    def __init__(self, xml_root: Element | None = None):
        self.root = xml_root

    def _match(self, elements: Sequence[ET.Element], part: str) -> list[ET.Element]:
        """Match child elements according to tag and optional filters."""
        if not elements:
            return []

        # フィルタなし
        if '[' not in part:
            return self._match_simple(elements, part)

        # フィルタあり
        return self._match_with_filters(elements, part)

    def _match_simple(self, elements: Sequence[ET.Element], tag: str) -> list[ET.Element]:
        matched = []
        for el in elements:
            child = el.find(f'ns:{tag}', NS)
            if child is not None:
                matched.append(child)
        return matched

    def _match_with_filters(self, elements: Sequence[ET.Element], part: str) -> list[ET.Element]:
        tag, *filters = part.split('[')
        tag = tag.strip()
        filters = [f.strip("]") for f in filters]

        matched = []
        for el in elements:
            for child in el.findall(f'ns:{tag}', NS):
                if self._check_filters(child, filters):
                    matched.append(child)
        return matched

    def _check_filters(self, element: ET.Element, filters: list[str]) -> bool:
        for flt in filters:
            if flt.startswith("@"):
                k, v = flt[1:].split("=")
                v = v.strip("'\"")
                if element.attrib.get(k) != v:
                    return False
        return True

    def extract_all(self, mapping_df: pd.DataFrame) -> dict[str, str | list[str]]:
        """Generate a dictionary mapping dict_key to value according to xml_path in mapping.csv."""
        result: dict[str, str | list[str]] = {}

        for _, row in mapping_df.iterrows():
            xml_path = row["xml_path"]
            dict_key = row["dict_key"]

            elements: list[ET.Element] = [self.root] if self.root is not None else []

            for part in xml_path.strip("/").split("/"):
                elements = self._match(elements, part)
                if not elements:
                    result[dict_key] = ""
                    break
            else:
                values = [el.text.strip() for el in elements if el.text]
                if not values:
                    result[dict_key] = ""
                elif len(values) == 1:
                    result[dict_key] = values[0]
                else:
                    result[dict_key] = values

        return result

    def find_element_by_path(self, root: Element, path: str) -> str | list[str] | None:
        """Traverse an XML tree to find an element by its path.

        This function navigates through an XML tree structure to locate an element
        or elements based on the provided path. The path can include tags and optional
        filters (e.g., "/root/child[@attr='value']").

        Args:
            root (Element): The root element of the XML tree.
            path (str): The path to the desired element, specified as a string.
                Example: "/root/child[@attr='value']".

        Returns:
                Union[str, list[str], None]: The text content of the matched element(s).
                - If a single element is matched, its text content is returned as a string.
                - If multiple elements are matched, their text contents are returned as a list of strings.
                - If no elements are matched, `None` is returned.

        """
        parts = path.strip('/').split('/')
        current_elements = [root]

        for part in parts:
            current_elements = self._match(current_elements, part)
            if not current_elements:
                return None

        # Extract text from the matched elements
        if len(current_elements) == 1:
            text = current_elements[0].text
            return text.strip() if text else None
        return [el.text.strip() for el in current_elements if el.text]

    # XMLを辞書化
    def parse_xml_to_dict(self, xml_file: str, mapping: dict[str, str]) -> dict[str, Any]:
        """Parse an XML file into a dictionary using a mapping.

        Args:
            xml_file (str): Path to the XML file to parse.
            mapping (dict): A dictionary mapping XML paths to dictionary keys.

        Returns:
            dict: A dictionary containing the parsed data.

        """
        tree = parse(xml_file)
        root = tree.getroot()

        result: dict[str, Any] = {}

        if root is None:
            for dict_key in mapping.values():
                result[dict_key] = ""
            return result
        for xml_path, dict_key in mapping.items():
            value = self.find_element_by_path(root, xml_path)
            result[dict_key] = value if value is not None else ""

        return result

    def get_meta_from_xml(self, xml_file: str) -> str | None:
        """Retrieve metadata values from the specified XML paths.

        This function extracts the values of the following elements:
        - `uri` element located at the path: `data/results/result[@ref="resultTemplate_semResultImage"]/insertion/uri`

        Args:
            xml_file (str): Path to the XML file.

        Returns:
            str | None: content of the `uri`, or `None` if not found.

        """
        tree = parse(xml_file)
        root = tree.getroot()

        # Define the XPath
        xml_path = 'data/results/result[@ref="resultTemplate_semResultImage"]/insertion/uri'
        if root is not None:
            uri_element = self.find_element_by_path(root, xml_path)
            return uri_element[0] if isinstance(uri_element, list) else uri_element
        return None
