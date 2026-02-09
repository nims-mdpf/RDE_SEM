import json
from pathlib import Path
from typing import Any

from modules_sem.interfaces import IStructuredDataProcesser


class StructuredDataProcesser(IStructuredDataProcesser):
    """Provides methods to convert structured data into machine-readable formats."""

    def to_json(self, exif_obj: dict, save_path: Path) -> dict[str, Any]:
        """Convert EXIF data to JSON and save it to a file.

        If the input object is a dictionary, it is directly written to the
        specified JSON file. Otherwise, the object's ``to_json`` method
        is called.

        Args:
            exif_obj (dict): EXIF data to be serialized.
            save_path (Path): Destination path for the JSON file.

        Returns:
            dict[str, Any]: The JSON-serializable EXIF data.

        """
        if isinstance(exif_obj, dict):
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(exif_obj, f, indent=4, ensure_ascii=False)
            return exif_obj

        return exif_obj.to_json(path=str(save_path))
