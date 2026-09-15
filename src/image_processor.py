"""Slices a board screenshot into a rows x cols grid of Tile images."""

from PIL import Image, ImageOps

from src.tile import Tile


class ImageProcessor:
    def __init__(self, image_path: str, rows: int, cols: int):
        self.image = Image.open(image_path)
        self.rows = rows
        self.cols = cols

    def split_image(
        self,
        begin_position=(15, 15),
        delta=(10, 10, 40, 40),
        save_dir: str | None = None,
    ) -> list[Tile]:
        width, height = self.image.size
        height = height // (self.rows + 1) * self.rows
        tile_size = (width // self.cols - 3, height // self.rows - 1)

        tiles = []
        tile_id = 0
        for y in range(begin_position[0], height - 20, tile_size[1]):
            for x in range(begin_position[1], width - 20, tile_size[0]):
                cell = self.image.crop((x, y, x + tile_size[0], y + tile_size[1]))
                cell = cell.crop(delta)
                cell = ImageOps.invert(cell)
                tile = Tile(
                    image=cell,
                    position=(x + delta[0], y + delta[1], x + delta[2], y + delta[3]),
                    tile_id=tile_id,
                    name="tile_picture{:03d}".format(tile_id),
                )
                if save_dir:
                    tile.save_image(save_dir)
                tiles.append(tile)
                tile_id += 1
        return tiles
