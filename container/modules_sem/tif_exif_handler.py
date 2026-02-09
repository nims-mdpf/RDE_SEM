from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from PIL import Image


class TifExifProcessor:
    """Processor for extracting and parsing EXIF metadata from TIFF images."""

    def __init__(self, parsers: Iterable[Any] | None = None):
        """Initialize the processor with optional parsers.

        Args:
            parsers (Iterable[Any] | None):
                Iterable of parser objects implementing
                ``can_parse(exif_data)`` and ``parse(exif_data)``.
                Defaults to None.

        """
        self.parsers = parsers or []

    def extract_exif(self, tif_path: str | Path) -> dict[str, object]:
        """Extract EXIF metadata from a TIFF file.

        Args:
            tif_path (str | Path): Path to the TIFF file.

        Returns:
            dict[str, object]: Dictionary containing EXIF tags and values.

        """
        with Image.open(tif_path) as img:
            exif_data: dict[str, object] = {}
            if hasattr(img, "tag_v2"):
                for tag, value in img.tag_v2.items():
                    exif_data[str(tag)] = value
        return exif_data

    def parse_exif(self, exif_data: dict[str, object]) -> dict[str, object]:
        """Parse EXIF data using the injected parsers.

        Args:
            exif_data (dict[str, object]): Raw EXIF data.

        Returns:
            dict[str, object]: Parsed EXIF data.
                Returns empty dict if no parser matches.

        """
        for parser in self.parsers:
            if parser.can_parse(exif_data):
                return dict(parser.parse(exif_data))

        return {}

    def process_file(self, file_path: str | Path) -> dict[str, object]:
        """Process a TIFF file to extract and parse EXIF metadata.

        Args:
            file_path (str | Path): Path to the TIFF file.

        Returns:
            dict[str, object]: Parsed EXIF data with 'raw_file_name' added.

        """
        file_path = Path(file_path)
        fname = file_path.name

        exif_data = self.extract_exif(file_path)
        parsed = self.parse_exif(exif_data)
        parsed["raw_file_name"] = fname
        return parsed
