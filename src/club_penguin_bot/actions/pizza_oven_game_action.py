import time
import os
from dataclasses import dataclass, field
from enum import Enum

from club_penguin_bot.actions.base_action import BaseAction
from club_penguin_bot.destinations import Destination
from club_penguin_bot.protocols import BotProtocol
from club_penguin_bot.templates import Template


class Penguin(Enum):
    YELLOW = 1
    GREEN = 2
    PURPLE = 3
    RED = 4
    BLUE = 5
    PINK = 6


PENGUIN_TEMPLATES: dict[Penguin, Template] = {
    Penguin.YELLOW: Template.PIZZA_OVEN_YELLOW_PENGUIN_ASKING_FOR_PIZZA,
    Penguin.GREEN: Template.PIZZA_OVEN_GREEN_PENGUIN_ASKING_FOR_PIZZA,
    Penguin.PURPLE: Template.PIZZA_OVEN_PURPLE_PENGUIN_ASKING_FOR_PIZZA,
    Penguin.RED: Template.PIZZA_OVEN_RED_PENGUIN_ASKING_FOR_PIZZA,
    Penguin.BLUE: Template.PIZZA_OVEN_BLUE_PENGUIN_ASKING_FOR_PIZZA,
    Penguin.PINK: Template.PIZZA_OVEN_PINK_PENGUIN_ASKING_FOR_PIZZA,
}


@dataclass
class PizzaOvenGameSettings:
    max_orders: int = 20
    slot_duration_s: float = 1.0


@dataclass
class PizzaOvenGameAction(BaseAction):
    bot: BotProtocol
    settings: PizzaOvenGameSettings = field(default_factory=PizzaOvenGameSettings)

    def run(self) -> None:
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        self.bot.travel(Destination.PIZZA_PARLOR)
        self.bot.click_template(Template.PIZZA_PARLOR_PIZZA_OVEN)
        self.bot.page.wait_for_timeout(5000)
        coordinates = self.bot.find_template_retry(Template.YES_BUTTON)
        if coordinates is None:
            raise ValueError("Could not begin pizza oven game.")

        self.bot.page.mouse.click(*coordinates)
        self.bot.page.wait_for_timeout(5000)
        self.bot.click_template(Template.PIZZA_OVEN_START_BUTTON)
        self.bot.page.wait_for_timeout(5000)

        collect_pizza_coordinates = self.bot.find_template_retry(Template.PIZZA_OVEN_GAME_COLLECT_PIZZA)
        if collect_pizza_coordinates is None:
            raise ValueError("Could not find pizza oven.")

        self.bot.page.mouse.click(*collect_pizza_coordinates)
        screenshot = self.bot.screenshot()
        penguin_coordinates_map: dict[Penguin, tuple[int, int] | None] = {
            Penguin.BLUE: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_BLUE_PENGUIN),
            Penguin.GREEN: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_GREEN_PENGUIN),
            Penguin.PINK: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_PINK_PENGUIN),
            Penguin.RED: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_RED_PENGUIN),
            Penguin.YELLOW: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_YELLOW_PENGUIN),
            Penguin.PURPLE: self.bot.find_template_in(screenshot, Template.PIZZA_OVEN_PURPLE_PENGUIN),
        }

        for penguin, penguin_coordinates in penguin_coordinates_map.items():
            if penguin_coordinates is None:
                raise ValueError(f"Could not find coordinates for {penguin.name} penguin.")

        key_order: list[Penguin] = []
        for i in range(self.settings.max_orders):
            captured_order_list: list[Penguin] = []

            # Wait until replay button appears before initiating next round
            self.bot.page.wait_for_timeout(1000 * (i + 1))
            replay_button_coordinates = self.bot.find_template_retry(Template.PIZZA_OVEN_REPLAY_ORDER_BUTTON)
            if replay_button_coordinates is None:
                raise ValueError("Could not find replay button.")

            self.bot.page.mouse.click(*collect_pizza_coordinates, delay=40)
            self.bot.page.wait_for_timeout(400)

            # It is important that time begins immediately after clicking the replay button
            self.bot.page.mouse.click(*replay_button_coordinates, delay=40)
            sequence_start = time.time()
            self.bot.page.mouse.move(*collect_pizza_coordinates)

            ## Mass screenshot, searching for penguin raising hand
            # For each of the (i + 1) slots in this order, sample at the midpoint
            # of each slot's expected time window to detect which penguin is raising hand.
            for n in range(i + 1):
                target = sequence_start + (n + 0.4) * self.settings.slot_duration_s
                wait = target - time.time()
                time.sleep(max(wait, 0))
                screenshot = self.bot.screenshot()
                detected_penguin: Penguin | None = None
                for penguin, template in PENGUIN_TEMPLATES.items():
                    if self.bot.find_template_in(screenshot, template) is not None:
                        detected_penguin = penguin
                        break
                if detected_penguin is None:
                    raise ValueError(f"Could not detect penguin for slot {n + 1} in round {i + 1}.")
                captured_order_list.append(detected_penguin)

            expected_count = i + 1
            if len(captured_order_list) != expected_count:
                raise ValueError(f"Expected {expected_count} penguins in round {i + 1}, got {len(captured_order_list)}.")

            if i == 0:
                key_order = captured_order_list.copy()
            elif captured_order_list[:-1] != key_order:
                raise ValueError(f"Order prefix mismatch in round {i + 1}. Key: {[penguin.name for penguin in key_order]}, Current: {[penguin.name for penguin in captured_order_list]}")
            else:
                key_order.append(captured_order_list[-1])

            self.bot.page.mouse.click(*collect_pizza_coordinates, delay=40)
            for penguin in key_order:
                penguin_coordinates = penguin_coordinates_map[penguin]
                if penguin_coordinates is None:
                    raise ValueError(f"Missing coordinates for {penguin.name} penguin.")
                self.bot.page.mouse.click(*penguin_coordinates, delay=40)
                self.bot.page.wait_for_timeout(500)

        self.bot.click_template(Template.PIZZA_OVEN_EXIT_GAME_BUTTON)
        self.bot.page.wait_for_timeout(1000)
        self.bot.click_template(Template.PIZZA_OVEN_SECOND_EXIT_GAME_BUTTON)
        self.bot.page.wait_for_timeout(3000)


def main():
    from club_penguin_bot.bot import Bot  # pylint: disable=C0415

    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(username=user, password=password, server=server)
        while True:
            PizzaOvenGameAction(bot).run()
            play_again = input("Play again? (y/N): ").strip().lower()
            if play_again != "y":
                break


if __name__ == "__main__":
    main()
