from typing import Literal
from dataclasses import dataclass, field
import time
import os

from club_penguin_bot.actions.base_action import BaseAction
from club_penguin_bot.protocols import BotProtocol
from club_penguin_bot.emote import Emote
from club_penguin_bot.destinations import Destination


@dataclass
class OrderSettings:
    request_delay_ms: int = 5000
    order_duration_minutes: int = 15
    order_type: Literal["pizza", "coffee"] = "pizza"


@dataclass
class OrderAction(BaseAction):
    bot: BotProtocol
    settings: OrderSettings = field(default_factory=OrderSettings)

    def run(self) -> None:
        start_time = time.perf_counter()
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        if self.settings.order_type == "pizza":
            destination = Destination.PIZZA_PARLOR
            emote = Emote.PIZZA
        elif self.settings.order_type == "coffee":
            destination = Destination.COFFEE_SHOP
            emote = Emote.COFFEE_CUP
        else:
            raise ValueError("Order types can only be pizza or coffee.")

        self.bot.travel(destination)
        self.bot.emote(Emote.SIT_FORWARD)

        while True:
            current_time = time.perf_counter()
            elapsed_s = current_time - start_time
            if elapsed_s >= self.settings.order_duration_minutes * 60:
                break

            self.bot.page.wait_for_timeout(self.settings.request_delay_ms)
            self.bot.emote(emote)


def main():
    from club_penguin_bot.bot import Bot  # pylint: disable=C0415

    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(username=user, password=password, server=server)
        OrderAction(bot).run()


if __name__ == "__main__":
    main()
