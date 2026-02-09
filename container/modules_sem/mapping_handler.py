from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_mapping(csv_path: Path) -> pd.DataFrame:
    """Load a mapping CSV file used for XML and TXT parsing.

    Args:
        csv_path (Path): Path to the mapping CSV file.

    Returns:
        pd.DataFrame: The loaded mapping data.

    """
    return pd.read_csv(csv_path)


def build_meta(mapping_df: pd.DataFrame, extractor: Any) -> dict[str, Any]:
    """Build metadata using a mapping DataFrame and an extractor.

    This function constructs metadata by calling ``extract_all`` on the
    provided extractor. The calling code is the same for both XML and TXT
    extractors.

    Args:
        mapping_df (pd.DataFrame): Mapping definition DataFrame.
        extractor: Extractor instance that provides
            an ``extract_all`` method.

    Returns:
        dict[str, Any]: Constructed metadata dictionary.

    """
    return dict(extractor.extract_all(mapping_df))
