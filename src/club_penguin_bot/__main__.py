from club_penguin_bot import Destination
from club_penguin_bot.bot import Bot
import os


def main():
    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(user, password, server)
        for destination in Destination:
            bot.travel(destination)


if __name__ == "__main__":
    main()
