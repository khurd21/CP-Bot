from club_penguin_bot import Destination
import time
from club_penguin_bot.bot import Bot
import os


def travel(bot: Bot, destination: Destination):
    bot.travel(destination)
    bot.send_message(f"{destination}")


def main():
    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(user, password, server)
        travel(bot, Destination.DOJO_COURTYARD)
        travel(bot, Destination.FOREST)
        travel(bot, Destination.ICEBERG)
        travel(bot, Destination.MINE)
        travel(bot, Destination.SKII_HILL)
        travel(bot, Destination.SKII_VILLAGE)
        travel(bot, Destination.SNOW_FORTS)
        travel(bot, Destination.STADIUM)
        travel(bot, Destination.THE_BEACH)
        travel(bot, Destination.THE_COVE)
        travel(bot, Destination.THE_DOCK)
        travel(bot, Destination.THE_PLAZA)
        travel(bot, Destination.NIGHTCLUB)
        travel(bot, Destination.WELCOME_ROOM)


if __name__ == "__main__":
    main()
