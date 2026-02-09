from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import MetaType, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import CharDecEncoding, read_from_json_file

from modules_sem.inputfile_handler import FileReader as txtFileReader
from modules_sem.JEOL.txt_img.mapping_csv import TxtExtractor
from modules_sem.mapping_handler import build_meta, load_mapping


class FileReader(txtFileReader):
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
        """Read txt/image files, perform unzip and parsing internally.

        Returns:
            dict[str, Any]:
                {
                    "invoice": dict,
                    "meta": MetaType,
                    "filename": str,
                    "txt_file": Path,
                }

        """
        invoice_obj, txt_file = self._prepare_files(resource_paths)

        if txt_file is None or not txt_file.exists():
            err = ".txt file not found."
            raise StructuredError(err)

        mapping_file = srcpaths.tasksupport / "mapping.csv"
        meta = self._read_txt(mapping_file, txt_file)

        return invoice_obj, meta

    def _prepare_files(
        self,
        resource_paths: RdeOutputResourcePath,
    ) -> tuple[dict, Path | None]:
        """Search raw/nonshared_raw, unzip if needed, extract images and txt."""
        search_dirs = list(filter(None, [resource_paths.raw, resource_paths.nonshared_raw]))

        all_files = self._collect_files(search_dirs)
        self._validate_file_count(all_files)

        txt_file, image_stems = self._process_files(all_files, resource_paths.main_image)
        self._validate_txt_and_image(txt_file, image_stems)

        invoice_obj = read_from_json_file(resource_paths.invoice / "invoice.json")
        return invoice_obj, txt_file

    def _collect_files(self, search_dirs: list[Path]) -> list[Path]:
        """Collect all files from search directories, unzip if needed."""
        all_files: list[Path] = []

        for dir_path in search_dirs:
            d = Path(dir_path)
            for zip_file in d.glob("*.zip"):
                with zipfile.ZipFile(zip_file, "r") as zip_ref:
                    zip_ref.extractall(d)
                zip_file.unlink()
            all_files.extend(d.glob("*"))

        if not all_files:
            err = "No data has been entered in raw or nonshared_raw."
            raise StructuredError(err)

        return all_files

    def _validate_file_count(self, all_files: list[Path]) -> None:
        """Validate number of input files."""
        max_allowed_files = 2
        if len(all_files) > max_allowed_files:
            err = ("This system expects exactly one pair of files (1 TXT file and 1 image file).")
            raise StructuredError(err)

    def _process_files(
        self,
        all_files: list[Path],
        main_image_dir: Path,
    ) -> tuple[Path | None, set[str]]:
        """Process image and txt files."""
        txt_file: Path | None = None
        image_stems: set[str] = set()

        for file in all_files:
            suffix = file.suffix.lower()

            if suffix in {".tif", ".jpg", ".jpeg"}:
                with Image.open(file) as img:
                    img.save(main_image_dir / f"{file.stem}.png", format="PNG")
                image_stems.add(file.stem)

            elif suffix == ".png":
                shutil.copy(file, main_image_dir / file.name)
                image_stems.add(file.stem)

            elif suffix == ".txt":
                txt_file = file

        return txt_file, image_stems

    def _validate_txt_and_image(
        self,
        txt_file: Path | None,
        image_stems: set[str],
    ) -> None:
        """Validate txt existence and filename match."""
        if txt_file is None:
            err = ".txt file not found."
            raise StructuredError(err)

        if txt_file.stem not in image_stems:
            err = (
                f"Filename mismatch: TXT file '{txt_file.name}' "
                "does not match any image file."
            )
            raise StructuredError(err)

    def _read_txt(
        self,
        mapping_file: Path,
        txt_file: Path,
    ) -> dict[str, Any]:
        """Parse txt file and build metadata."""
        try:
            mapping = load_mapping(mapping_file)
            extractor = TxtExtractor(txt_file)
            return build_meta(mapping, extractor)
        except Exception as e:
            err = f"Failed to parse txt file: {txt_file}"
            raise StructuredError(err) from e

    def _overwrite_data_name(
            self, invoice_obj: dict, filename: str, dst_invoice_json: Path) -> dict:
        """Overwrite the dataName.

        Args:
            invoice_obj (dict): invoice data
            filename (str) : filename.stem
            dst_invoice_json (Path): Path to the metadata list JSON file, which may include definitions or schema information.

        """
        enc = CharDecEncoding.detect_text_file_encoding(dst_invoice_json)
        invoice_obj["basic"]["dataName"] = filename
        with open(dst_invoice_json, "w", encoding=enc) as fout:
            json.dump(invoice_obj, fout, indent=4, ensure_ascii=False)
        return invoice_obj

    def get_date_from_meta(self, meta: MetaType) -> Any:
        """Get date from meta."""
        return meta["date"]

    def overwrite_invoice_if_needed(
        self,
        invoice_obj: dict,
        meta_obj: MetaType,
        resource_paths: RdeOutputResourcePath,
    ) -> None:
        """Overwrite invoice dataName and measurement_measured_date if needed."""
        matched_file = [f for f in resource_paths.rawfiles if f.match("fsmarttable*csv")]
        filename = next((f.stem for d in [resource_paths.nonshared_raw, resource_paths.raw] if d is not None for f in Path(d).glob("*.txt")), None)
        dst_invoice_json = resource_paths.invoice.joinpath("invoice.json")
        if not matched_file:
            invoice_obj = self._overwrite_data_name(invoice_obj, str(filename), dst_invoice_json)
        date_str = self.get_date_from_meta(meta_obj)
        if (
            meta_obj is not None
            and meta_obj.get("date") is not None
            and invoice_obj["custom"].get("measurement_measured_date") is None
        ):
            invoice_obj = self._overwrite_measured_date(invoice_obj, dst_invoice_json, date_str)
