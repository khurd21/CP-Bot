from pathlib import Path
import weakref

import cv2
import numpy as np
import pytesseract
from playwright.sync_api import Page
from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed

from club_penguin_bot.templates import Template


class Vision:
    """Image/OCR utility service for bot UI state detection.

    `Vision` is designed to be shared per Playwright `Page`. Use
    `Vision.get_shared(page)` to reuse one instance and its caches.
    """

    _instances: "weakref.WeakKeyDictionary[Page, Vision]" = weakref.WeakKeyDictionary()

    def __init__(self, page: Page, templates_dir: Path | None = None):
        self.page = page
        self.templates_dir = templates_dir or (Path(__file__).parent / "templates")
        self._template_cache: dict[Template, np.ndarray] = {}

    @classmethod
    def get_shared(cls, page: Page) -> "Vision":
        instance = cls._instances.get(page)
        if instance is None:
            instance = cls(page=page)
            cls._instances[page] = instance
        return instance

    @retry(
        retry=retry_if_result(lambda result: result is None),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        retry_error_callback=lambda state: None,
    )
    def find_text_retry(self, target_name: str) -> tuple[int, int] | None:
        screenshot = self.page.screenshot()
        image = cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data["text"]):
            if text and target_name.lower() in text.lower():
                x = data["left"][i]
                y = data["top"][i]
                w = data["width"][i]
                h = data["height"][i]
                return (x + w // 2, y + h // 2)

        return None

    def screenshot(self) -> np.ndarray:
        data = self.page.screenshot()
        array = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if array is None:
            raise ValueError("Screenshot failed.")
        return array

    def find_template(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None:
        return self.find_template_in(self.screenshot(), template_name, threshold=threshold)

    def find_template_in(self, screen: np.ndarray, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None:
        template = self._read_template(template_name)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < threshold:
            return None

        height, width = template.shape[:2]
        return (max_loc[0] + width // 2, max_loc[1] + height // 2)

    @retry(
        retry=retry_if_result(lambda result: result is None),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry_error_callback=lambda state: None,
    )
    def find_template_retry(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None:
        return self.find_template(template_name, threshold=threshold)

    def _read_template(self, template_name: Template) -> np.ndarray:
        cached = self._template_cache.get(template_name)
        if cached is not None:
            return cached

        template_path = self.templates_dir / template_name.value
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"Template not found: {template_name}")

        self._template_cache[template_name] = template
        return template
