"""Step 2: read the digit off every Tile via Baidu Cloud's OCR API."""

import base64
import concurrent.futures
import io
import json
import urllib.parse

import requests
from PIL import Image

from src.pipeline.capture import Tile


class OCRClient:
    def __init__(self, api_key: str, secret_key: str):
        if not api_key or not secret_key:
            raise ValueError("Baidu OCR API key/secret key are not configured")
        self.api_key = api_key
        self.secret_key = secret_key
        self.url = (
            "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers?access_token="
            + self._get_access_token()
        )
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

    def _get_access_token(self) -> str:
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        return str(requests.post(url, params=params).json().get("access_token"))

    @staticmethod
    def _image_to_base64(image: Image.Image, urlencoded: bool = False, fmt: str = "PNG") -> str:
        buffer = io.BytesIO()
        image.save(buffer, format=fmt)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf8")
        return urllib.parse.quote_plus(encoded) if urlencoded else encoded

    def recognize_digit(self, image: Image.Image) -> int:
        payload = (
            "image=" + self._image_to_base64(image, urlencoded=True)
            + "&recognize_granularity=big&detect_direction=false"
        )
        response = requests.post(self.url, data=payload, headers=self.headers)
        data = json.loads(response.text)
        return int(data["words_result"][0]["words"])


def recognize_all(tiles: list[Tile], ocr: OCRClient, thread_count: int) -> list:
    digits = [0] * len(tiles)

    def recognize(tile: Tile) -> None:
        digits[tile.tile_id] = ocr.recognize_digit(tile.image)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = {executor.submit(recognize, tile): tile for tile in tiles}
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return digits
