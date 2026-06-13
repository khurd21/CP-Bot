from typing import Optional

from tenacity import retry_if_result, stop_after_attempt, wait_fixed, retry
import numpy as np
import validators
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from club_penguin_bot.destinations import Destination
from club_penguin_bot.templates import Template
from club_penguin_bot.travel import Travel
from club_penguin_bot.vision import Vision
from club_penguin_bot.emote import Emote


class Bot:
    def __init__(self, url: str):
        self.url: str = url
        if not validators.url(self.url):
            raise ValueError(f"URL: {self.url} is not valid.")

        self._pw: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._vision: Optional[Vision] = None
        self.navigator = Travel(self)

    def __enter__(self) -> "Bot":
        self.open_game()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def _find_text(self, target_name: str) -> Optional[tuple[int, int]]:
        return self._require_vision().find_text_retry(target_name)

    def screenshot(self) -> np.ndarray:
        return self._require_vision().screenshot()

    def find_template(self, template_name: Template, threshold: float = 0.85) -> Optional[tuple[int, int]]:
        return self._require_vision().find_template(template_name, threshold=threshold)

    def find_template_in(self, screen: np.ndarray, template_name: Template, threshold: float = 0.85) -> Optional[tuple[int, int]]:
        return self._require_vision().find_template_in(screen, template_name, threshold=threshold)

    def find_template_matches_in(
        self,
        screen: np.ndarray,
        template_name: Template,
        threshold: float = 0.85,
        grayscale: bool = False,
    ) -> list[tuple[int, int, int, int, float]]:
        return self._require_vision().find_template_matches_in(
            screen,
            template_name,
            threshold=threshold,
            grayscale=grayscale,
        )

    def find_template_retry(self, template_name: Template, threshold: float = 0.85) -> Optional[tuple[int, int]]:
        return self._require_vision().find_template_retry(template_name, threshold=threshold)

    def find_text_retry(self, target_name: str) -> Optional[tuple[int, int]]:
        return self._require_vision().find_text_retry(target_name)

    def click_template(self, template_name: Template, delay: int = 500) -> bool:
        if self.page is None:
            raise ValueError("Page is None.")

        coordinates = self.find_template(template_name)
        if coordinates is None:
            return False

        self.page.mouse.click(*coordinates)
        self.page.wait_for_timeout(delay)
        return True

    @retry(
        retry=retry_if_result(lambda result: not result),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry_error_callback=lambda state: False,
    )
    def click_template_retry(self, template_name: Template, delay: int = 500):
        return self.click_template(template_name, delay)

    def send_message(self, message: str) -> None:
        if self.page is None:
            raise ValueError("Page cannot be None.")

        self.click_template(Template.MESSAGE_BOX)
        self.page.keyboard.type(message, delay=40)
        self.click_template(Template.SEND_MESSAGE_BUTTON)

    def emote(self, emote: Emote, delay: int = 500) -> None:
        if self.page is None:
            raise ValueError("Page cannot be None.")

        for key in emote.value:
            self.page.keyboard.down(key)

        for key in emote.value:
            self.page.keyboard.up(key)

        self.page.wait_for_timeout(delay)

    def travel(self, destination: Destination) -> None:
        self.navigator.to(destination)

    def login(self, username: str, password: str, server: str) -> None:
        if self.page is None:
            raise ValueError("Page cannot be None.")

        self.click_template(Template.LOGIN_BUTTON_UNHOVERED)
        self.click_template(Template.LOGIN_PENGUIN_NAME_INPUT_FIELD)
        self.page.keyboard.type(username, delay=40)
        self.page.keyboard.press("Tab")
        self.page.keyboard.type(password, delay=40)
        self.click_template(Template.LOGIN_BUTTON_USER_PASSWORD_PAGE, delay=1000)
        server_coordinates = self._find_text(server)
        if server_coordinates is None:
            raise ValueError(f"Could not find server {server}")
        self.page.mouse.click(*server_coordinates)
        self.navigator.validate_loaded()

    def open_game(self) -> None:
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=False)
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 900})
        self.page.goto(self.url, wait_until="networkidle", timeout=60000)
        self._vision = Vision.get_shared(self.page)

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()
        self._vision = None

    def _require_vision(self) -> Vision:
        if self._vision is not None:
            return self._vision
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self._vision = Vision.get_shared(self.page)
        return self._vision
