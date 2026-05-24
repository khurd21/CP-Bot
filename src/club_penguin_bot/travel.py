from collections.abc import Callable

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from club_penguin_bot.destinations import Destination
from club_penguin_bot.protocols import BotProtocol
from club_penguin_bot.templates import Template


class Travel:
    def __init__(self, bot: BotProtocol):
        self._bot = bot

    def _wait(self, timeout_ms: int) -> None:
        if self._bot.page is None:
            raise ValueError("Page cannot be None.")
        self._bot.page.wait_for_timeout(timeout_ms)

    def to(self, destination: Destination) -> None:
        route_handlers: dict[Destination, Callable[[], None]] = {
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
            Destination.MINE_SHACK: self._travel_to_mine_shack,
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
            Destination.DOJO: self._travel_to_dojo,
            Destination.CAVE_MINE: self._travel_to_cave_mine,
            Destination.MINE: self._travel_to_mine,
            Destination.RECYCLING_PLANT: self._travel_to_recycling_plant,
        }

        handler = route_handlers.get(destination)
        if handler is None:
            raise ValueError(f"Unsupported destination: {destination}")
        handler()
        self._validate_loaded()

    def validate_loaded(self) -> None:
        self._validate_loaded()

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
    )
    def _open_map(self) -> None:
        opened = self._bot.click_template(Template.MAP_BUTTON, delay=700)
        if not opened:
            raise ValueError("Could not find map button.")
        coordinates = self._bot.find_template_retry(Template.DOJO_COURTYARD_MAP)
        if coordinates is None:
            raise ValueError("Could not confirm map opened.")

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        reraise=True,
    )
    def _validate_loaded(self) -> None:
        coordinates = self._bot.find_template(Template.SEND_MESSAGE_BUTTON)
        if coordinates is None:
            raise ValueError("Page did not load: message button not found.")

    @retry(
        retry=retry_if_exception_type(ValueError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
    )
    def _travel_via_map(self, destination_template: Template) -> None:
        clicked = self._bot.click_template(destination_template, delay=1600)
        if not clicked:
            raise ValueError(f"Could not find destination template: {destination_template}")

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

    def _travel_to_mine_shack(self) -> None:
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
        self._bot.click_template(Template.ROCK_THE_BEACH)
        self._wait(3000)
        self._bot.click_template(Template.LIGHT_ABOVE_DOOR_THE_BEACH)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.SEVEN_LIGHTHOUSE)
        if coordinates is None:
            raise ValueError("Could not confirm lighthouse room loaded.")

    def _travel_to_beacon(self) -> None:
        self._travel_to_lighthouse()
        self._bot.click_template(Template.TO_TOP_SIGN_LIGHTHOUSE)
        coordinates = self._bot.find_template_retry(Template.TELESCOPE_BEACON)
        if coordinates is None:
            raise ValueError("Could not confirm beacon room loaded.")

    def _travel_to_skii_lodge(self) -> None:
        self._travel_to_skii_village()
        self._bot.click_template(Template.SKII_VILLAGE_TREE)
        self._wait(3000)
        self._bot.click_template(Template.SKII_LODGE_FRONT_DOOR)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.MULLET_HEAD_SKII_LODGE)
        if coordinates is None:
            raise ValueError("Could not confirm skii lodge room loaded.")

    def _travel_to_skii_lodge_attic(self) -> None:
        self._travel_to_skii_lodge()
        self._bot.click_template(Template.SKII_LODGE_STAIRS)
        self._wait(5000)
        coordinates = self._bot.find_template_retry(Template.SKII_LODGE_ATTIC_HORSE_HEAD)
        if coordinates is None:
            raise ValueError("Could not confirm skii lodge attic room loaded.")

    def _travel_to_sports_shop(self) -> None:
        self._travel_to_skii_village()
        self._bot.click_template(Template.SKII_VILLAGE_TREE)
        self._wait(3000)
        self._bot.click_template(Template.WINTER_SPORT_DOOR_SKII_VILLAGE)
        self._wait(5000)
        coordinates = self._bot.find_template_retry(Template.SPORT_SHOP_SURF_IMAGE)
        if coordinates is None:
            raise ValueError("Could not confirm sport shop room loaded.")

    def _travel_to_spy_headquarters(self) -> None:
        self._bot.click_template(Template.SPY_PHONE)
        self._bot.click_template(Template.SPY_PHONE_VISIT_HQ_BUTTON)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.SPY_HEADQUARTERS_KEYBOARD)
        if coordinates is None:
            raise ValueError("Could not confirm spy headquarters room loaded.")

    def _travel_to_nightclub(self) -> None:
        self.to(Destination.THE_TOWN)
        self._bot.click_template(Template.NIGHT_CLUB_FRONT_DOOR)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.NIGHT_CLUB_SPEAKER)
        if coordinates is None:
            raise ValueError("Could not confirm nightclub room loaded.")

    def _travel_to_lounge(self) -> None:
        self.to(Destination.NIGHTCLUB)
        self._bot.click_template(Template.NIGHT_CLUB_BOTTOM_LEFT_SEGMENT)
        self._wait(3000)
        self._bot.click_template(Template.NIGHT_CLUB_STAIRS_TO_LOUNGE)
        self._wait(5000)
        coordinates = self._bot.find_template_retry(Template.LOUNGE_OVERHEAD_TV_CABLES)
        if coordinates is None:
            raise ValueError("Could not confirm lounge room loaded.")

    def _travel_to_coffee_shop(self) -> None:
        self.to(Destination.THE_TOWN)
        self._bot.click_template(Template.COFFEE_SHOP_DOOR)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.COFFEE_SHOP_EXIT_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm coffee shop room loaded.")

    def _travel_to_book_room(self) -> None:
        self.to(Destination.COFFEE_SHOP)
        self._bot.click_template(Template.COFFEE_SHOP_BOTTOM_LEFT_SEGMENT)
        self._wait(3500)
        self._bot.click_template(Template.COFFEE_SHOP_STAIRS_TO_BOOK_ROOM)
        self._wait(5000)
        coordinates = self._bot.find_template_retry(Template.BOOK_ROOM_TOP_SHELF)
        if coordinates is None:
            raise ValueError("Could not confirm book room loaded.")

    def _travel_to_gift_shop(self) -> None:
        self.to(Destination.THE_TOWN)
        self._bot.click_template(Template.GIFT_SHOP_FRONT_DOOR)
        self._wait(3000)
        coordinates = self._bot.find_template_retry(Template.GIFT_SHOP_POSTER)
        if coordinates is None:
            raise ValueError("Could not confirm gift shop room loaded.")

    def _travel_to_gift_shop_office(self) -> None:
        self.to(Destination.GIFT_SHOP)
        self._bot.click_template(Template.GIFT_SHOP_TO_OFFICE_DOOR)
        self._wait(5000)
        coordinates = self._bot.find_template_retry(Template.GIFT_SHOP_OFFICE_ROOF_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm gift shop office room loaded.")

    def _travel_to_tour_hq(self) -> None:
        self.to(Destination.WELCOME_ROOM)
        self._bot.click_template(Template.TOUR_HQ_FRONT_DOOR)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.TOUR_HQ_CALENDAR)
        if coordinates is None:
            raise ValueError("Could not confirm tour hq room loaded.")

    def _travel_to_tour_hq_lookout(self) -> None:
        self.to(Destination.TOUR_HQ)
        self._bot.click_template(Template.TOUR_HQ_STAIRS_TO_ROOF)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.TOUR_HQ_LOOKOUT_WALL_ART)
        if coordinates is None:
            raise ValueError("Could not confirm tour hq lookout room loaded.")

    def _travel_to_pet_shop(self) -> None:
        self.to(Destination.THE_PLAZA)
        self._bot.click_template(Template.PET_SHOP_FRONT_DOOR)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.PET_SHOP_EXIT_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm pet shop room loaded.")

    def _travel_to_puffle_park(self) -> None:
        self.to(Destination.PET_SHOP)
        self._bot.click_template(Template.PET_SHOP_DOOR_TO_PUFFLE_PARK)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.PUFFLE_PARK_BUSH_O)
        if coordinates is None:
            raise ValueError("Could not confirm pet shop room loaded.")

    def _travel_to_the_stage(self) -> None:
        self.to(Destination.THE_PLAZA)
        self._bot.click_template(Template.THE_STAGE_FRONT_DOOR)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.THE_STAGE_CEILING_ART)
        if coordinates is None:
            raise ValueError("Could not confirm the stage room loaded.")

    def _travel_to_pizza_parlor(self) -> None:
        self.to(Destination.THE_PLAZA)
        self._bot.click_template(Template.PIZZA_PARLOR_FRONT_DOOR)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.PIZZA_PARLOR_FISH_DISH_MENU)
        if coordinates is None:
            raise ValueError("Could not confirm pizza parlor room loaded.")

    def _travel_to_dojo(self) -> None:
        self.to(Destination.DOJO_COURTYARD)
        self._bot.click_template(Template.DOJO_COURTYARD_ABOVE_DOOR)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.DOJO_CARD_JITSU_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm dojo room loaded.")

    def _travel_to_mine(self) -> None:
        self.to(Destination.MINE_SHACK)
        self._bot.click_template(Template.MINE_SHACK_TO_MINE)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.MINE_SIGN)
        if coordinates is None:
            raise ValueError("Could not confirm mine room loaded.")

    def _travel_to_recycling_plant(self) -> None:
        self.to(Destination.MINE_SHACK)
        self._bot.click_template(Template.MINE_SHACK_TO_RECYCLING_PLANT)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.RECYCLING_PLANT_FIRE_ALARM)
        if coordinates is None:
            raise ValueError("Could not confirm recycling plant room loaded.")

    def _travel_to_cave_mine(self) -> None:
        self.to(Destination.MINE)
        self._bot.click_template(Template.MINE_TO_CAVE_MINE)
        self._wait(3500)
        coordinates = self._bot.find_template_retry(Template.CAVE_MINE_HARD_HAT)
        if coordinates is None:
            raise ValueError("Could not confirm cave mine room loaded.")
