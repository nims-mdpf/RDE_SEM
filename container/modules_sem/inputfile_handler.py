from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rdetoolkit.rde2util import CharDecEncoding

from modules_sem.interfaces import IInputFileParser


class FileReader(IInputFileParser):
    """Template class for reading and parsing input data.

    This class serves as a template for the development team to read and parse input data.
    It implements the IInputFileParser interface. Developers can use this template class
    as a foundation for adding specific file reading and parsing logic based on the project's
    requirements.

    Args:
        srcpaths (tuple[Path, ...]): Paths to input source files.

    Returns:
        Any: The loaded data from the input file(s).

    Example:
        file_reader = FileReader()
        loaded_data = file_reader.read(('file1.txt', 'file2.txt'))
        file_reader.to_csv('output.csv')

    """

    def read_invoice(self, raw_file_path: Path) -> Any:
        """Read invoice file.

        Args:
            raw_file_path (Path): invoice file path

        Returns:
            type[JSONDecoder] : invoice data

        """
        enc = CharDecEncoding.detect_text_file_encoding(raw_file_path)
        with open(raw_file_path, encoding=enc) as f:
            return json.load(f)

    def _overwrite_measured_date(self, invoice_obj: dict, dst_invoice_json: Path, date_str: str) -> dict:
        enc = CharDecEncoding.detect_text_file_encoding(dst_invoice_json)

        invoice_obj["custom"]["measurement_measured_date"] = date_str
        with open(dst_invoice_json, "w", encoding=enc) as f:
            json.dump(invoice_obj, f, indent=4, ensure_ascii=False)

        return invoice_obj
