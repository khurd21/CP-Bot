from typing import Protocol

from playwright.sync_api import Page

from club_penguin_bot.destinations import Destination
from club_penguin_bot.templates import Template


class BotProtocol(Protocol):
    page: Page | None

    def click_template(self, template_name: Template, delay: int = 500) -> bool: ...

    def find_template(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None: ...

    def find_template_retry(self, template_name: Template, threshold: float = 0.85) -> tuple[int, int] | None: ...

    def travel(self, destination: Destination) -> None: ...
