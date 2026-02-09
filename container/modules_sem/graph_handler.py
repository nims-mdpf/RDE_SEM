from __future__ import annotations

from pathlib import Path

from PIL import Image


class GraphPlotter:
    """A class for plotting and saving images.

    Methods:
        plot(data: pd.DataFrame, save_path: Path, *, title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = None) -> None:
            Plots the given data and saves the plot as an image.

        save_image(image: TifImage, save_path: Path) -> None:
            Saves the given image as a PNG file.

    """

    def save_image(self, image_path: Path, save_path: Path) -> None:
        """Save the given image as a PNG file at the specified save path.

        Args:
            image_path (Path): Path to the source image file.
            save_path (Path): Path where the PNG image will be saved.

        Returns:
            None

        """
        with Image.open(image_path) as img:
            img.save(save_path, format="PNG")
