from __future__ import annotations

from pathlib import Path

from rdetoolkit.errors import catch_exception_with_message
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import Meta

from modules_sem.factory import SemFactory


def jeol_maiml(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
    config: dict,
) -> None:
    """Execute structured processing in SEM.

    Execute structured text processing, metadata extraction, and visualization.
    It handles structured text processing, metadata extraction, and graphing.
    Other processing required for structuring may be implemented as needed.

    Args:
        srcpaths (RdeInputDirPaths): Paths to input resources for processing.
        resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.
        config (dict): Configuration dictionary for SEM processing.

    Returns:
        None

    Note:
        The actual function names and processing details may vary depending on the project.

    """
    module = SemFactory.get_objects(srcpaths.tasksupport, config)
    invoice_obj, meta, image_file, image_match = module.file_reader.read(srcpaths, resource_paths)
    if image_match is True:
        module.graph_plotter.save_image(image_file, resource_paths.main_image.joinpath(f"{Path(image_file).stem}.png"))
    module.meta_parser.parse(meta)
    module.meta_parser.save_meta(
        resource_paths.meta.joinpath("metadata.json"),
        Meta(srcpaths.tasksupport.joinpath("metadata-def.json")),
        const_meta_info=meta,
        repeated_meta_info={},
    )
    module.file_reader.overwrite_invoice_if_needed(
        invoice_obj,
        meta,
        resource_paths,
    )


def jeol_fe(
    srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, config: dict,
) -> None:
    """Not execute structured text processing, metadata extraction, and visualization.

    Simply copy and generate the image files.

    Args:
        srcpaths (RdeInputDirPaths): Paths to input resources for processing.
        resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.
        config (dict): Configuration dictionary for SEM processing.

    Returns:
        None

    """
    module = SemFactory.get_objects(srcpaths.tasksupport, config)
    invoice_obj, meta = module.file_reader.read(srcpaths, resource_paths)
    module.meta_parser.save_meta(
        resource_paths.meta.joinpath("metadata.json"),
        Meta(srcpaths.tasksupport.joinpath("metadata-def.json")),
        const_meta_info=meta,
        repeated_meta_info={},
    )
    module.file_reader.overwrite_invoice_if_needed(
        invoice_obj, meta, resource_paths,
    )


def tiff_exif(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, config: dict) -> None:
    """Execute structured processing for TIFF EXIF data.

    This function handles the structured processing of data obtained from TIFF files
    with EXIF metadata. It includes tasks such as reading input files,
    extracting metadata, processing structured data, and generating visualizations.

    Args:
        srcpaths (RdeInputDirPaths): Paths to input resources for processing.
        resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.
        config (dict): Configuration dictionary for SEM processing.

    Returns:
        None

    Note:
        The actual function names and processing details may vary depending on the project.

    """
    module = SemFactory.get_objects(srcpaths.tasksupport, config)
    invoice_obj, exif_obj, meta, tif_file = module.file_reader.read(srcpaths, resource_paths)
    module.structured_processer.to_json(exif_obj, resource_paths.struct.joinpath("tif_info.json"))
    module.meta_parser.save_meta(
        resource_paths.meta.joinpath("metadata.json"),
        Meta(srcpaths.tasksupport.joinpath("metadata-def.json")),
        const_meta_info=meta,
        repeated_meta_info={},
    )
    module.graph_plotter.save_image(tif_file, resource_paths.main_image.joinpath(f"{Path(tif_file).stem}.png"))
    module.file_reader.overwrite_invoice_if_needed(
        invoice_obj,
        meta,
        resource_paths,
    )


@catch_exception_with_message(
    error_message="ERROR: failed in data processing", error_code=50,
)
def dataset(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
) -> None:
    """Execute structured processing based on SEM manufacturer."""
    config = SemFactory.get_config(srcpaths.tasksupport)

    try:
        manufacturer = config["sem"]["manufacturer"].lower()
    except Exception as exc:
        err = "Invalid config: 'sem.manufacturer' is missing."
        raise StructuredError(err) from exc

    dispatch_table = {
        "jeol_fe": jeol_fe,
        "jeol_maiml": jeol_maiml,
        "tiff_exif": tiff_exif,
    }

    if manufacturer not in dispatch_table:
        err = f"Unsupported manufacturer: {manufacturer}"
        raise StructuredError(err)

    handler = dispatch_table[manufacturer]

    return handler(srcpaths, resource_paths, config)
