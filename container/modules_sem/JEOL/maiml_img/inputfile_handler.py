from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from defusedxml.ElementTree import parse
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import MetaType, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import read_from_json_file

from modules_sem.inputfile_handler import FileReader as maimlFileReader
from modules_sem.JEOL.maiml_img.mapping_csv import XmlExtractor
from modules_sem.mapping_handler import build_meta, load_mapping


class FileReader(maimlFileReader):
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

    def _check_unzip(
        self,
        resource_paths: RdeOutputResourcePath,
    ) -> tuple[dict, Path | None, Path | None]:
        """Check input files in raw and nonshared_raw directories."""
        search_dirs = [resource_paths.raw, resource_paths.nonshared_raw]

        maiml_file: Path | None = None
        image_file: Path | None = None

        image_extensions = [".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"]

        for d in search_dirs:
            if d is None:
                continue
            for file in Path(d).glob("*"):
                suffix = file.suffix.lower()
                if suffix == ".maiml":
                    maiml_file = file
                elif suffix in image_extensions:
                    image_file = file

        if maiml_file is None and image_file is None:
            err = "No .maiml or supported image files found in raw or nonshared_raw."
            raise StructuredError(err)

        invoice_obj = read_from_json_file(
            resource_paths.invoice / "invoice.json",
        )

        return invoice_obj, maiml_file, image_file

    def read(self, srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath) -> Any:
        """Read MAIML and image files, perform unzip and parsing internally.

        Returns:
            Any: A tuple containing invoice object, metadata dictionary

        """
        # ---- unzip & file detection ----
        invoice_obj, maiml_file, image_file = self._check_unzip(resource_paths)

        if maiml_file is None or not maiml_file.exists():
            err = ".maiml file not found."
            raise StructuredError(err)

        mapping_file = srcpaths.tasksupport / "mapping.csv"

        # ---- MAIML parsing ----
        meta, image_match = self._read_maiml(
            maiml_file,
            image_file,
            mapping_file,
        )

        return invoice_obj, meta, image_file, image_match

    def _read_maiml(
        self,
        maiml_file: Path,
        image_file: Path | None,
        mapping_file: Path,
    ) -> tuple[MetaType, bool]:

        mapping = load_mapping(mapping_file)

        # ---- XML parsing ----
        xml_root = parse(maiml_file).getroot()
        result = XmlExtractor(xml_root)

        dict_meta = build_meta(mapping, result)

        # ---- image matching ----
        data_path = result.get_meta_from_xml(str(maiml_file))
        image_match = False

        if (
            image_file
            and image_file.exists()
            and data_path
            and image_file.name == Path(data_path).name
        ):
            image_match = True

        return dict_meta, image_match

    def get_date_from_meta(self, meta: MetaType) -> str:
        """Get date from meta as YYYY-MM-DD."""
        return datetime.fromisoformat(str(meta["date"])).strftime("%Y-%m-%d")

    def overwrite_invoice_if_needed(
        self,
        invoice_obj: dict,
        meta_obj: MetaType,
        resource_paths: RdeOutputResourcePath,
    ) -> None:
        """Overwrite invoice dataName and measurement_measured_date if needed."""
        # custom.measurement_measured_date
        date_str = self.get_date_from_meta(meta_obj)
        dst_invoice_json = resource_paths.invoice.joinpath("invoice.json")
        if invoice_obj["custom"]["measurement_measured_date"] is None:
            self._overwrite_measured_date(invoice_obj, dst_invoice_json, date_str)
