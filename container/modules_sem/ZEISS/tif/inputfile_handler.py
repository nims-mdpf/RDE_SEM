from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import MetaType, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import read_from_json_file

from modules_sem.inputfile_handler import FileReader as tifFileReader
from modules_sem.mapping_handler import build_meta, load_mapping
from modules_sem.tif_exif_handler import TifExifProcessor
from modules_sem.ZEISS.tif.mapping_csv import DictExtractor
from modules_sem.ZEISS.tif.tif_exif_handler import FibicsParser, HeliosParser, PrefixedTextParser


class FileReader(tifFileReader):
    """Template class for reading and parsing input data.

    This class serves as a template for the development team to read and parse input data.
    It implements the IInputFileParser interface. Developers can use this template class
    as a foundation for adding specific file reading and parsing logic based on the project's
    requirements.

    Args:
        raw_file_paths (tuple[Path, ...]): Paths to input source files.

    Returns:
        Any: The loaded data from the input file(s).

    Example:
        file_reader = FileReader()
        loaded_data = file_reader.read(('file1.txt', 'file2.txt'))
        file_reader.to_csv('output.csv')

    """

    def read(self, srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath) -> Any:
        """Read tif file, extract EXIF and metadata internally.

        Returns:
            Any: tuple containing invoice object, EXIF data, metadata, and tif file path.

        """
        invoice_obj, tif_file = self._prepare_files(resource_paths)

        mapping_file = srcpaths.tasksupport / "mapping.csv"

        exif, meta = self._read_tif(mapping_file, tif_file)

        return invoice_obj, exif, meta, tif_file

    def _prepare_files(
        self,
        resource_paths: RdeOutputResourcePath,
    ) -> tuple[dict, Path]:
        """Search raw/nonshared_raw and get a single tif file."""
        search_dirs = [resource_paths.raw, resource_paths.nonshared_raw]
        tif_file: Path | None = None

        for d in search_dirs:
            if d is None:
                continue
            files = list(Path(d).glob("*"))
            if files:
                tif_file = files[0]
                break

        if tif_file is None:
            err = ".tif file not found."
            raise StructuredError(err)

        if tif_file.suffix.lower() != ".tif":
            err = f"Unsupported file format: {tif_file.suffix}. Only .tif is supported."
            raise StructuredError(err)

        invoice_obj = read_from_json_file(resource_paths.invoice / "invoice.json")

        return invoice_obj, tif_file

    def _read_tif(
        self,
        mapping_file: Path,
        tif_file: Path,
    ) -> tuple[dict, MetaType]:
        """Extract EXIF from tif and build metadata."""
        processor = TifExifProcessor(
            parsers=[
                FibicsParser(),
                HeliosParser(),
                PrefixedTextParser(),
            ],
        )

        exif = processor.process_file(tif_file)
        mapping = load_mapping(mapping_file)
        extractor = DictExtractor(exif)
        meta = build_meta(mapping, extractor)
        return exif, meta

    def get_date_from_meta(self, meta: MetaType) -> str | None:
        """Get date from meta as YYYY-MM-DD."""
        s = meta["date"]
        if not isinstance(s, str) or not s.strip():
            return None
        try:
            return datetime.fromisoformat(s).date().isoformat()
        except ValueError:
            return datetime.strptime(s, "%m/%d/%Y").replace(tzinfo=timezone.utc).date().isoformat()

    def overwrite_invoice_if_needed(
        self,
        invoice_obj: dict,
        meta_obj: MetaType,
        resource_paths: RdeOutputResourcePath,
    ) -> None:
        """Overwrite invoice dataName and measurement_measured_date if needed."""
        date_str = self.get_date_from_meta(meta_obj)
        if date_str is None:
            return
        dst_invoice_json = resource_paths.invoice.joinpath("invoice.json")
        if invoice_obj["custom"]["measurement_measured_date"] is None:
            self._overwrite_measured_date(invoice_obj, dst_invoice_json, date_str)
