"""A single board cell: its cropped image plus its on-screen pixel bounding box."""

import os
from dataclasses import dataclass
from PIL.Image import Image


@dataclass
class Tile:
    image: Image
    position: tuple  # (x1, y1, x2, y2) pixel bbox within the captured screenshot
    tile_id: int
    name: str = "tile_picture"

    def save_image(self, folder_path: str) -> None:
        os.makedirs(folder_path, exist_ok=True)
        self.image.save(os.path.join(folder_path, f"{self.name}.png"), format="PNG")
