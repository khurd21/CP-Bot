from typing import Protocol

from playwright.sync_api import Page
import numpy as np

from club_penguin_bot.destinations import Destination
from club_penguin_bot.templates import Template
from club_penguin_bot.emote import Emote


class BotProtocol(Protocol):
    page: Page | None

    def click_template(self, template_name: Template, delay: int = 500) -> bool: ...

    def screenshot(self) -> np.ndarray: ...

    def find_template(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None: ...

    def find_template_in(self, screen: np.ndarray, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None: ...

    def find_template_retry(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None: ...

    def travel(self, destination: Destination) -> None: ...

    def emote(self, emote: Emote, delay: int = 500) -> None: ...
