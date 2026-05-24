import os

from club_penguin_bot.actions.throw_snowball_at_clock_action import (
    ThrowSnowballAtClockAction,
    ThrowSnowballAtClockSettings,
)
from club_penguin_bot.bot import Bot
from club_penguin_bot.destinations import Destination


def main():
    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(user, password, server)
        action = ThrowSnowballAtClockAction(
            bot,
            ThrowSnowballAtClockSettings(pre_throw_delay_ms=500, post_throw_delay_ms=500, num_throws=25),
        )
        action.run()
        for destination in Destination:
            bot.travel(destination)


if __name__ == "__main__":
    main()
