from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

from rdetoolkit.models.rde2types import MetaType, RdeInputDirPaths, RdeOutputResourcePath, RepeatedMetaType
from rdetoolkit.rde2util import Meta

T = TypeVar("T")


class IInputFileParser(ABC):
    """Abstract base class (interface) for input file parsers.

    This interface defines the contract that input file parser
    implementations must follow. The parsers are expected to read files
    from a specified path, parse the contents of the files, and provide
    options for saving the parsed data.

    Methods:
        read: A method expecting a file path and responsible for reading a file.

    Example implementations of this interface could be for parsing files
    of different formats like CSV, Excel, JSON, etc.

    """

    @abstractmethod
    def read(self, srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath) -> Any:
        """Read and parse input files from given resource paths."""
        raise NotImplementedError

    @abstractmethod
    def overwrite_invoice_if_needed(
        self,
        invoice_obj: dict,
        meta_obj: MetaType,
        resource_paths: RdeOutputResourcePath,
    ) -> None:
        """Overwrite invoice file if needed."""
        raise NotImplementedError


class IStructuredDataProcesser(ABC):
    """Abstract base class (interface) for structured data parsers.

    This interface defines the contract that structured data parser
    implementations must follow. The parsers are expected to transform
    structured data, such as DataFrame, into various desired output formats.

    Methods:
        to_csv: A method that saves the given data to a CSV file.

    Implementers of this interface could transform data into various
    formats like CSV, Excel, JSON, etc.

    """

    @abstractmethod
    def to_json(self, exif_obj: dict, save_path: Path) -> dict[str, Any]:
        """Convert the given EXIF data to JSON and save it to the specified file.

        Args:
            exif_obj (dict): EXIF data to be serialized.
            save_path (Path): Path where the JSON file will be written.

        Returns:
            dict[str, Any]: The JSON-serializable EXIF data.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        """
        raise NotImplementedError


class IMetaParser(ABC, Generic[T]):
    """Abstract base class (interface) for meta information parsers.

    This interface defines the contract that meta information parser
    implementations must follow. The parsers are expected to save the
    constant and repeated meta information to a specified path.

    Method:
        save_meta: Saves the constant and repeated meta information to a specified path.
        parse: This method returns two types of metadata: const_meta_info and repeated_meta_info.

    """

    @abstractmethod
    def parse(self, data: T) -> Any:
        """Parse."""
        raise NotImplementedError

    @abstractmethod
    def save_meta(
        self,
        save_path: Path,
        metaobj: Meta,
        *,
        const_meta_info: MetaType | None = None,
        repeated_meta_info: RepeatedMetaType | None = None,
    ) -> Meta:
        """Save the constant and repeated meta information to a specified path.

        Args:
            save_path (Path): The path where the meta information will be saved.
            metaobj (Meta): The meta information to be saved.
            const_meta_info (MetaType): Constant meta information. Defaults to None.
            repeated_meta_info (RepeatedMetaType): Repeated meta information. Defaults to None.

        """
        raise NotImplementedError


class IGraphPlotter(ABC, Generic[T]):
    """Abstract base class (interface) for graph plotting implementations.

    This interface defines the contract that graph plotting
    implementations must follow. The implementations are expected
    to be capable of plotting a simple graph using a given pandas DataFrame.

    Methods:
        simple_plot: Plots a simple graph using the provided pandas DataFrame.

    """

    @abstractmethod
    def save_image(self, image_path: Path, save_path: Path) -> None:
        """Save the given image as a PNG file at the specified save path.

        Args:
            image_path (Path): Path to the source image file.
            save_path (Path): Path where the PNG image will be saved.

        Returns:
            None

        """
        raise NotImplementedError
