from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from rdetoolkit.exceptions import StructuredError

from modules_sem.graph_handler import GraphPlotter
from modules_sem.inputfile_handler import FileReader
from modules_sem.JEOL.maiml_img.inputfile_handler import FileReader as maimlFileReader
from modules_sem.JEOL.txt_img.inputfile_handler import FileReader as txtFileReader
from modules_sem.meta_handler import MetaParser
from modules_sem.structured_handler import StructuredDataProcesser
from modules_sem.TIFF_EXIF.inputfile_handler import FileReader as tifFileReader

SEM_MANUFACTURER_CLASS_MAPPING: dict[str, type[FileReader]] = {
    "jeol_maiml": maimlFileReader,
    "jeol_fe": txtFileReader,
    "tiff_exif": tifFileReader,
}


class SemFactory:
    """Obtain a variety of data for use in the SEM's Structured processing."""

    def __init__(
        self,
        file_reader: FileReader,
        meta_parser: MetaParser,
        structured_processer: StructuredDataProcesser,
        graph_plotter: GraphPlotter,
    ):
        self.file_reader = file_reader
        self.meta_parser = meta_parser
        self.graph_plotter = graph_plotter
        self.structured_processer = structured_processer

    @staticmethod
    def get_config(path_tasksupport: Path) -> Any:
        """Obtain configuration data."""
        rdeconfig_file = path_tasksupport.joinpath("rdeconfig.yaml")
        if not rdeconfig_file.exists():
            msg = f"File not found: {rdeconfig_file}"
            raise StructuredError(msg)

        try:
            with open(rdeconfig_file, encoding="utf-8") as file:
                config = yaml.safe_load(file)
        except Exception:
            msg = f"Invalid configuration file: {rdeconfig_file}"
            raise StructuredError(msg) from None

        return config

    @staticmethod
    def get_objects(_path_tasksupport: Path, config: dict) -> SemFactory:
        """Obtain classes based on manufacturer only (extension ignored)."""
        manufacturer: str = config["sem"]["manufacturer"]

        try:
            file_reader_cls: type[FileReader] = SEM_MANUFACTURER_CLASS_MAPPING[manufacturer]
        except KeyError:
            msg = f"Unsupported manufacturer: {manufacturer}"
            raise StructuredError(msg) from None

        return SemFactory(
            file_reader_cls(),
            MetaParser(),
            StructuredDataProcesser(),
            GraphPlotter(),
        )
