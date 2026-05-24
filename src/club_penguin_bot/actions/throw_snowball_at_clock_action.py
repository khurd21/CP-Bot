from dataclasses import dataclass, field
import os

from club_penguin_bot.actions.base_action import BaseAction
from club_penguin_bot.destinations import Destination
from club_penguin_bot.protocols import BotProtocol
from club_penguin_bot.templates import Template


@dataclass
class ThrowSnowballAtClockSettings:
    pre_throw_delay_ms: int = 500
    post_throw_delay_ms: int = 500
    num_throws: int = 25


@dataclass
class ThrowSnowballAtClockAction(BaseAction):
    bot: BotProtocol
    settings: ThrowSnowballAtClockSettings = field(default_factory=ThrowSnowballAtClockSettings)

    def run(self) -> None:
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        self.bot.travel(Destination.SNOW_FORTS)

        for _ in range(self.settings.num_throws):
            self.bot.page.wait_for_timeout(self.settings.pre_throw_delay_ms)
            self.bot.page.keyboard.press("T", delay=40)
            if not self.bot.click_template(Template.SNOW_FORTS_CLOCK_TARGET, delay=0):
                raise ValueError("Could not locate target in Snow Forts.")
            self.bot.page.wait_for_timeout(self.settings.post_throw_delay_ms)


def main():
    from club_penguin_bot.bot import Bot  # pylint: disable=C0415

    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(username=user, password=password, server=server)
        ThrowSnowballAtClockAction(bot).run()


if __name__ == "__main__":
    main()
