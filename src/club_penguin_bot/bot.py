from ssl import ALERT_DESCRIPTION_NO_RENEGOTIATION
from multiprocessing import Value
import pytesseract
from tenacity import (
    retry,
    retry_if_result,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from collections.abc import Callable
from pathlib import Path
from club_penguin_bot.destinations import Destination
from club_penguin_bot.templates import Template
import cv2
from typing import Optional
import validators
import numpy as np

from playwright.sync_api import sync_playwright, Playwright, Browser, Page

TEMPLATES_DIR = Path(__file__).parent / "templates"


class Bot:
    def __init__(self, url: str):
        self.url: str = url
        if not validators.url(self.url):
            raise ValueError(f"URL: {self.url} is not valid.")

        self._pw: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self) -> "Bot":
        self.open_game()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    @retry(
        retry=retry_if_result(lambda result: result is None),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        retry_error_callback=lambda state: None,
    )
    def _find_text(self, target_name: str) -> Optional[tuple[int, int]]:
        if self.page is None:
            raise ValueError("Page cannot be None.")

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
        if self.page is None:
            raise ValueError("Page cannot be None.")
        data = self.page.screenshot()
        array = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if array is None:
            raise ValueError("Screenshot failed.")
        return array

    def find_template(
        self, template_name: Template, threshold: float = 0.85
    ) -> Optional[tuple[int, int]]:
        template_path = TEMPLATES_DIR / template_name.value
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"Template not found: {template_name}")

        screen = self.screenshot()
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
    def find_template_retry(
        self, template_name: Template, threshold: float = 0.85
    ) -> Optional[tuple[int, int]]:
        return self.find_template(template_name, threshold=threshold)

    def click_template(self, template_name: Template, delay: int = 500) -> bool:
        if self.page is None:
            raise ValueError("Page is None.")

        coordinates = self.find_template(template_name)
        if coordinates is None:
            return False

        self.page.mouse.click(*coordinates)
        self.page.wait_for_timeout(delay)
        return True

    def send_message(self, message: str) -> None:
        if self.page is None:
            raise ValueError("Page cannot be None.")

        self.click_template(Template.MESSAGE_BOX)
        self.page.keyboard.type(message, delay=40)
        self.click_template(Template.SEND_MESSAGE_BUTTON)

    def travel(self, destination: Destination) -> None:
        route_handlers: dict[Destination, Callable] = {
            Destination.DOJO_COURTYARD: self._travel_to_dojo_courtyard,
            Destination.FOREST: self._travel_to_forest,
            Destination.ICEBERG: self._travel_to_iceberg,
            Destination.SKII_HILL: self._travel_to_skii_hill,
            Destination.SKII_VILLAGE: self._travel_to_skii_village,
            Destination.SNOW_FORTS: self._travel_to_snow_forts,
            Destination.STADIUM: self._travel_to_stadium,
            Destination.THE_BEACH: self._travel_to_the_beach,
            Destination.THE_COVE: self._travel_to_the_cove,
            Destination.THE_DOCK: self._travel_to_the_dock,
            Destination.THE_PLAZA: self._travel_to_the_plaza,
            Destination.MINE: self._travel_to_mine,
            Destination.THE_TOWN: self._travel_to_the_town,
            Destination.WELCOME_ROOM: self._travel_to_welcome_room,
            Destination.LIGHTHOUSE: self._travel_to_lighthouse,
            Destination.BEACON: self._travel_to_beacon,
            Destination.SKII_LODGE: self._travel_to_skii_lodge,
            Destination.SKII_LODGE_ATTIC: self._travel_to_skii_lodge_attic,
            Destination.NIGHTCLUB: self._travel_to_nightclub,
            Destination.LOUNGE: self._travel_to_lounge,
            Destination.SPY_HEADQUARTERS: self._travel_to_spy_headquarters,
            Destination.GIFT_SHOP: self._travel_to_gift_shop,
            Destination.GIFT_SHOP_OFFICE: self._travel_to_gift_shop_office,
            Destination.COFFEE_SHOP: self._travel_to_coffee_shop,
            Destination.BOOK_ROOM: self._travel_to_book_room,
            Destination.TOUR_HQ: self._travel_to_tour_hq,
            Destination.TOUR_HQ_LOOKOUT: self._travel_to_tour_hq_lookout,
            Destination.PET_SHOP: self._travel_to_pet_shop,
            Destination.PET_SHOP_PUFFLE_PARK: self._travel_to_puffle_park,
            Destination.THE_STAGE: self._travel_to_the_stage,
            Destination.PIZZA_PARLOR: self._travel_to_pizza_parlor,
            Destination.SPORTS_SHOP: self._travel_to_sports_shop,
        }

        handler = route_handlers.get(destination)
        if handler is None:
            raise ValueError(f"Unsupported destination: {destination}")
        handler()
        self._validate_loaded()

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
    )
    def _open_map(self) -> None:
        opened = self.click_template(Template.MAP_BUTTON, delay=700)
        if not opened:
            raise ValueError("Could not find map button.")
        coordinates = self.find_template_retry(Template.DOJO_COURTYARD_MAP)
        if coordinates is None:
            raise ValueError("Could not confirm map opened.")

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        reraise=True,
    )
    def _validate_loaded(self) -> None:
        coordinates = self.find_template(Template.SEND_MESSAGE_BUTTON)
        if coordinates is None:
            raise ValueError("Page did not load: message button not found.")

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
    )
    def _travel_via_map(self, destination_template: Template) -> None:
        clicked = self.click_template(destination_template, delay=1600)
        if not clicked:
            raise ValueError(
                f"Could not find destination template: {destination_template}"
            )

    def _travel_to_dojo_courtyard(self) -> None:
        self._open_map()
        self._travel_via_map(Template.DOJO_COURTYARD_MAP)

    def _travel_to_forest(self) -> None:
        self._open_map()
        self._travel_via_map(Template.FOREST_MAP)

    def _travel_to_iceberg(self) -> None:
        self._open_map()
        self._travel_via_map(Template.ICEBERG_MAP)

    def _travel_to_skii_hill(self) -> None:
        self._open_map()
        self._travel_via_map(Template.SKII_HILL_MAP)

    def _travel_to_skii_village(self) -> None:
        self._open_map()
        self._travel_via_map(Template.SKII_VILLAGE_MAP)

    def _travel_to_snow_forts(self) -> None:
        self._open_map()
        self._travel_via_map(Template.SNOW_FORTS_MAP)

    def _travel_to_stadium(self) -> None:
        self._open_map()
        self._travel_via_map(Template.STADIUM_MAP)

    def _travel_to_the_beach(self) -> None:
        self._open_map()
        self._travel_via_map(Template.THE_BEACH_MAP)

    def _travel_to_the_cove(self) -> None:
        self._open_map()
        self._travel_via_map(Template.THE_COVE_MAP)

    def _travel_to_the_dock(self) -> None:
        self._open_map()
        self._travel_via_map(Template.THE_DOCK_MAP)

    def _travel_to_the_plaza(self) -> None:
        self._open_map()
        self._travel_via_map(Template.THE_PLAZA_MAP)

    def _travel_to_mine(self) -> None:
        self._open_map()
        self._travel_via_map(Template.MINE_MAP)

    def _travel_to_the_town(self) -> None:
        self._open_map()
        self._travel_via_map(Template.THE_TOWN_MAP)

    def _travel_to_welcome_room(self) -> None:
        self._open_map()
        self._travel_via_map(Template.WELCOME_ROOM_MAP)

    def _travel_to_lighthouse(self) -> None:
        self._travel_to_the_beach()
        self.click_template(Template.ROCK_THE_BEACH)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        self.click_template(Template.LIGHT_ABOVE_DOOR_THE_BEACH)
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.SEVEN_LIGHTHOUSE)
        if coordinates is None:
            raise ValueError("Could not confirm lighthouse room loaded.")

    def _travel_to_beacon(self) -> None:
        self._travel_to_lighthouse()
        self.click_template(Template.TO_TOP_SIGN_LIGHTHOUSE)
        coordinates = self.find_template_retry(Template.TELESCOPE_BEACON)
        if coordinates is None:
            raise ValueError("Could not confirm beacon room loaded.")

    def _travel_to_skii_lodge(self) -> None:
        self._travel_to_skii_village()
        self.click_template(Template.SKII_VILLAGE_TREE)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        self.click_template(Template.SKII_LODGE_FRONT_DOOR)
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.MULLET_HEAD_SKII_LODGE)
        if coordinates is None:
            raise ValueError("Could not confirm skii lodge room loaded.")

    def _travel_to_skii_lodge_attic(self) -> None:
        self._travel_to_skii_lodge()
        self.click_template(Template.SKII_LODGE_STAIRS)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(5000)
        coordinates = self.find_template_retry(Template.SKII_LODGE_ATTIC_HORSE_HEAD)
        if coordinates is None:
            raise ValueError("Could not confirm skii lodge attic room loaded.")

    def _travel_to_sports_shop(self) -> None:
        self._travel_to_skii_village()
        self.click_template(Template.SKII_VILLAGE_TREE)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        self.click_template(Template.WINTER_SPORT_DOOR_SKII_VILLAGE)
        self.page.wait_for_timeout(5000)
        coordinates = self.find_template_retry(Template.SPORT_SHOP_SURF_IMAGE)
        if coordinates is None:
            raise ValueError("Could not confirm sport shop room loaded.")

    def _travel_to_spy_headquarters(self) -> None:
        self.click_template(Template.SPY_PHONE)
        self.click_template(Template.SPY_PHONE_VISIT_HQ_BUTTON)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.SPY_HEADQUARTERS_KEYBOARD)
        if coordinates is None:
            raise ValueError("Could not confirm spy headquarters room loaded.")

    def _travel_to_nightclub(self) -> None:
        self.travel(Destination.THE_TOWN)
        self.click_template(Template.NIGHT_CLUB_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.NIGHT_CLUB_SPEAKER)
        if coordinates is None:
            raise ValueError("Could not confirm nightclub room loaded.")

    def _travel_to_lounge(self) -> None:
        self.travel(Destination.NIGHTCLUB)
        self.click_template(Template.NIGHT_CLUB_BOTTOM_LEFT_SEGMENT)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        self.click_template(Template.NIGHT_CLUB_STAIRS_TO_LOUNGE)
        self.page.wait_for_timeout(5000)
        coordinates = self.find_template_retry(Template.LOUNGE_OVERHEAD_TV_CABLES)
        if coordinates is None:
            raise ValueError("Could not confirm lounge room loaded.")

    def _travel_to_coffee_shop(self) -> None:
        self.travel(Destination.THE_TOWN)
        self.click_template(Template.COFFEE_SHOP_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.COFFEE_SHOP_EXIT_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm coffee shop room loaded.")

    def _travel_to_book_room(self) -> None:
        self.travel(Destination.COFFEE_SHOP)
        self.click_template(Template.COFFEE_SHOP_BOTTOM_LEFT_SEGMENT)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        self.click_template(Template.COFFEE_SHOP_STAIRS_TO_BOOK_ROOM)
        self.page.wait_for_timeout(5000)
        coordinates = self.find_template_retry(Template.BOOK_ROOM_TOP_SHELF)
        if coordinates is None:
            raise ValueError("Could not confirm book room loaded.")

    def _travel_to_gift_shop(self) -> None:
        self.travel(Destination.THE_TOWN)
        self.click_template(Template.GIFT_SHOP_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3000)
        coordinates = self.find_template_retry(Template.GIFT_SHOP_POSTER)
        if coordinates is None:
            raise ValueError("Could not confirm gift shop room loaded.")

    def _travel_to_gift_shop_office(self) -> None:
        self.travel(Destination.GIFT_SHOP)
        self.click_template(Template.GIFT_SHOP_TO_OFFICE_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(5000)
        coordinates = self.find_template_retry(Template.GIFT_SHOP_OFFICE_ROOF_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm gift shop office room loaded.")

    def _travel_to_tour_hq(self) -> None:
        self.travel(Destination.WELCOME_ROOM)
        self.click_template(Template.TOUR_HQ_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.TOUR_HQ_CALENDAR)
        if coordinates is None:
            raise ValueError("Could not confirm tour hq room loaded.")

    def _travel_to_tour_hq_lookout(self) -> None:
        self.travel(Destination.TOUR_HQ)
        self.click_template(Template.TOUR_HQ_STAIRS_TO_ROOF)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.TOUR_HQ_LOOKOUT_WALL_ART)
        if coordinates is None:
            raise ValueError("Could not confirm tour hq lookout room loaded.")

    def _travel_to_pet_shop(self) -> None:
        self.travel(Destination.THE_PLAZA)
        self.click_template(Template.PET_SHOP_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.PET_SHOP_EXIT_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm pet shop room loaded.")

    def _travel_to_puffle_park(self) -> None:
        self.travel(Destination.PET_SHOP)
        self.click_template(Template.PET_SHOP_DOOR_TO_PUFFLE_PARK)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.PUFFLE_PARK_BUSH_O)
        if coordinates is None:
            raise ValueError("Could not confirm pet shop room loaded.")

    def _travel_to_the_stage(self) -> None:
        self.travel(Destination.THE_PLAZA)
        self.click_template(Template.THE_STAGE_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.THE_STAGE_CEILING_ART)
        if coordinates is None:
            raise ValueError("Could not confirm the stage room loaded.")

    def _travel_to_pizza_parlor(self) -> None:
        self.travel(Destination.THE_PLAZA)
        self.click_template(Template.PIZZA_PARLOR_FRONT_DOOR)
        if self.page is None:
            raise ValueError("Page cannot be None.")
        self.page.wait_for_timeout(3500)
        coordinates = self.find_template_retry(Template.PIZZA_PARLOR_FISH_DISH_MENU)
        if coordinates is None:
            raise ValueError("Could not confirm pizza parlor room loaded.")

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
        self._validate_loaded()

    def open_game(self) -> None:
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=False)
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 900})
        self.page.goto(self.url, wait_until="networkidle", timeout=60000)

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()
