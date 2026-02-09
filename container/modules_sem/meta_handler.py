from __future__ import annotations

from pathlib import Path

from rdetoolkit.models.rde2types import MetaType, RepeatedMetaType
from rdetoolkit.rde2util import Meta

from modules_sem.interfaces import IMetaParser


class MetaParser(IMetaParser[MetaType]):
    """Template class for parsing and saving metadata.

    This class serves as a template for the development team to parse and save metadata. It implements
    the IMetaParser interface. Developers can use this template class as a foundation for adding
    specific parsing and saving logic for metadata based on the project's requirements.

    Args:
        data (MetaType): The metadata to be parsed and saved.

    Returns:
        tuple[MetaType, MetaType]: A tuple containing the parsed constant and repeated metadata.

    Example:
        meta_parser = MetaParser()
        parsed_const_meta, parsed_repeated_meta = meta_parser.parse(data)
        meta_obj = Meta(metaDefFilePath='meta_definition.json')
        saved_info = meta_parser.save_meta('saved_meta.json', meta_obj,
                                        const_meta_info=parsed_const_meta,
                                        repeated_meta_info=parsed_repeated_meta)

    """

    def __init__(self) -> None:
        self.const_meta_info: MetaType = {}
        self.repeated_meta_info: RepeatedMetaType = {}

    def parse(self, data: MetaType) -> tuple[MetaType, RepeatedMetaType]:
        """Parse and extract constant and repeated metadata from the provided data."""
        self.const_meta_info = dict(data.items())
        self.repeated_meta_info = {}
        return self.const_meta_info, self.repeated_meta_info

    def save_meta(
        self,
        save_path: Path,
        metaobj: Meta,
        *,
        const_meta_info: MetaType | None = None,
        repeated_meta_info: RepeatedMetaType | None = None,
    ) -> Meta:
        """Save parsed metadata to a file using the provided Meta object.

        Args:
            save_path (Path): The path where the metadata will be saved.
            metaobj (Meta): The Meta object used for saving metadata.
            const_meta_info (MetaType | None, optional): Constant metadata to save. Defaults to None.
            repeated_meta_info (RepeatedMetaType | None, optional): Repeated metadata to save. Defaults to None.

        Returns:
            Meta: The Meta object used for saving metadata.

        """
        if const_meta_info is None:
            const_meta_info = self.const_meta_info
        if repeated_meta_info is None:
            repeated_meta_info = self.repeated_meta_info

        for key, value in metaobj.metaDef.items():
            if key not in const_meta_info and "default" in value:
                const_meta_info[key] = value["default"]

        metaobj.assign_vals(const_meta_info)
        metaobj.assign_vals(repeated_meta_info)

        metaobj.writefile(str(save_path))
        return metaobj
