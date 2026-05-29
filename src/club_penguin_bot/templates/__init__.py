from enum import StrEnum

from club_penguin_bot.templates.login import LoginTemplate
from club_penguin_bot.templates.ui import UITemplate
from club_penguin_bot.templates.map import MapTemplate
from club_penguin_bot.templates.beach import BeachTemplate
from club_penguin_bot.templates.skii_lodge import SkiiLodgeTemplate
from club_penguin_bot.templates.spy_headquarters import SpyHeadquartersTemplate
from club_penguin_bot.templates.coffee_shop import CoffeeShopTemplate
from club_penguin_bot.templates.gift_shop import GiftShopTemplate
from club_penguin_bot.templates.night_club import NightClubTemplate
from club_penguin_bot.templates.tour_hq import TourHQTemplate
from club_penguin_bot.templates.pet_shop import PetShopTemplate
from club_penguin_bot.templates.stage import StageTemplate
from club_penguin_bot.templates.pizza_parlor import PizzaParlorTemplate
from club_penguin_bot.templates.pizza_oven import PizzaOvenTemplate
from club_penguin_bot.templates.dojo import DojoTemplate
from club_penguin_bot.templates.mine import MineTemplate
from club_penguin_bot.templates.snow_forts import SnowFortsTemplate


class Template(StrEnum):
    """Unified template namespace combining all template domains."""

    # Login templates
    LOGIN_BUTTON_UNHOVERED = LoginTemplate.LOGIN_BUTTON_UNHOVERED
    LOGIN_PENGUIN_NAME_INPUT_FIELD = LoginTemplate.LOGIN_PENGUIN_NAME_INPUT_FIELD
    LOGIN_BUTTON_USER_PASSWORD_PAGE = LoginTemplate.LOGIN_BUTTON_USER_PASSWORD_PAGE

    # UI templates
    MESSAGE_BOX = UITemplate.MESSAGE_BOX
    SEND_MESSAGE_BUTTON = UITemplate.SEND_MESSAGE_BUTTON
    YES_BUTTON = UITemplate.YES_BUTTON
    MAP_BUTTON = UITemplate.MAP_BUTTON

    # Map templates
    DOJO_COURTYARD_MAP = MapTemplate.DOJO_COURTYARD_MAP
    FOREST_MAP = MapTemplate.FOREST_MAP
    ICEBERG_MAP = MapTemplate.ICEBERG_MAP
    SKII_HILL_MAP = MapTemplate.SKII_HILL_MAP
    SKII_VILLAGE_MAP = MapTemplate.SKII_VILLAGE_MAP
    SNOW_FORTS_MAP = MapTemplate.SNOW_FORTS_MAP
    STADIUM_MAP = MapTemplate.STADIUM_MAP
    THE_BEACH_MAP = MapTemplate.THE_BEACH_MAP
    THE_COVE_MAP = MapTemplate.THE_COVE_MAP
    THE_DOCK_MAP = MapTemplate.THE_DOCK_MAP
    THE_PLAZA_MAP = MapTemplate.THE_PLAZA_MAP
    MINE_MAP = MapTemplate.MINE_MAP
    THE_TOWN_MAP = MapTemplate.THE_TOWN_MAP
    WELCOME_ROOM_MAP = MapTemplate.WELCOME_ROOM_MAP

    # Beach templates
    ROCK_THE_BEACH = BeachTemplate.ROCK_THE_BEACH
    LIGHT_ABOVE_DOOR_THE_BEACH = BeachTemplate.LIGHT_ABOVE_DOOR_THE_BEACH
    SEVEN_LIGHTHOUSE = BeachTemplate.SEVEN_LIGHTHOUSE
    TO_TOP_SIGN_LIGHTHOUSE = BeachTemplate.TO_TOP_SIGN_LIGHTHOUSE
    TELESCOPE_BEACON = BeachTemplate.TELESCOPE_BEACON

    # Skii Lodge templates
    SKII_LODGE_FRONT_DOOR = SkiiLodgeTemplate.SKII_LODGE_FRONT_DOOR
    SKII_VILLAGE_TREE = SkiiLodgeTemplate.SKII_VILLAGE_TREE
    WINTER_SPORT_DOOR_SKII_VILLAGE = SkiiLodgeTemplate.WINTER_SPORT_DOOR_SKII_VILLAGE
    MULLET_HEAD_SKII_LODGE = SkiiLodgeTemplate.MULLET_HEAD_SKII_LODGE
    SKII_LODGE_STAIRS = SkiiLodgeTemplate.SKII_LODGE_STAIRS
    SKII_LODGE_ATTIC_HORSE_HEAD = SkiiLodgeTemplate.SKII_LODGE_ATTIC_HORSE_HEAD
    SPORT_SHOP_SURF_IMAGE = SkiiLodgeTemplate.SPORT_SHOP_SURF_IMAGE

    # Spy Headquarters templates
    SPY_PHONE = SpyHeadquartersTemplate.SPY_PHONE
    SPY_PHONE_VISIT_HQ_BUTTON = SpyHeadquartersTemplate.SPY_PHONE_VISIT_HQ_BUTTON
    SPY_HEADQUARTERS_KEYBOARD = SpyHeadquartersTemplate.SPY_HEADQUARTERS_KEYBOARD

    # Coffee Shop templates
    COFFEE_SHOP_DOOR = CoffeeShopTemplate.COFFEE_SHOP_DOOR
    COFFEE_SHOP_EXIT_SIGN = CoffeeShopTemplate.COFFEE_SHOP_EXIT_SIGN
    COFFEE_SHOP_BOTTOM_LEFT_SEGMENT = CoffeeShopTemplate.COFFEE_SHOP_BOTTOM_LEFT_SEGMENT
    COFFEE_SHOP_STAIRS_TO_BOOK_ROOM = CoffeeShopTemplate.COFFEE_SHOP_STAIRS_TO_BOOK_ROOM
    BOOK_ROOM_TOP_SHELF = CoffeeShopTemplate.BOOK_ROOM_TOP_SHELF

    # Gift Shop templates
    GIFT_SHOP_FRONT_DOOR = GiftShopTemplate.GIFT_SHOP_FRONT_DOOR
    GIFT_SHOP_POSTER = GiftShopTemplate.GIFT_SHOP_POSTER
    GIFT_SHOP_TO_OFFICE_DOOR = GiftShopTemplate.GIFT_SHOP_TO_OFFICE_DOOR
    GIFT_SHOP_OFFICE_ROOF_SIGN = GiftShopTemplate.GIFT_SHOP_OFFICE_ROOF_SIGN

    # Night Club templates
    NIGHT_CLUB_FRONT_DOOR = NightClubTemplate.NIGHT_CLUB_FRONT_DOOR
    NIGHT_CLUB_SPEAKER = NightClubTemplate.NIGHT_CLUB_SPEAKER
    NIGHT_CLUB_BOTTOM_LEFT_SEGMENT = NightClubTemplate.NIGHT_CLUB_BOTTOM_LEFT_SEGMENT
    NIGHT_CLUB_STAIRS_TO_LOUNGE = NightClubTemplate.NIGHT_CLUB_STAIRS_TO_LOUNGE
    LOUNGE_OVERHEAD_TV_CABLES = NightClubTemplate.LOUNGE_OVERHEAD_TV_CABLES

    # Tour HQ templates
    TOUR_HQ_FRONT_DOOR = TourHQTemplate.TOUR_HQ_FRONT_DOOR
    TOUR_HQ_CALENDAR = TourHQTemplate.TOUR_HQ_CALENDAR
    TOUR_HQ_STAIRS_TO_ROOF = TourHQTemplate.TOUR_HQ_STAIRS_TO_ROOF
    TOUR_HQ_LOOKOUT_WALL_ART = TourHQTemplate.TOUR_HQ_LOOKOUT_WALL_ART

    # Pet Shop templates
    PET_SHOP_FRONT_DOOR = PetShopTemplate.PET_SHOP_FRONT_DOOR
    PET_SHOP_EXIT_SIGN = PetShopTemplate.PET_SHOP_EXIT_SIGN
    PET_SHOP_DOOR_TO_PUFFLE_PARK = PetShopTemplate.PET_SHOP_DOOR_TO_PUFFLE_PARK
    PUFFLE_PARK_BUSH_O = PetShopTemplate.PUFFLE_PARK_BUSH_O

    # Stage templates
    THE_STAGE_FRONT_DOOR = StageTemplate.THE_STAGE_FRONT_DOOR
    THE_STAGE_CEILING_ART = StageTemplate.THE_STAGE_CEILING_ART

    # Pizza Parlor templates
    PIZZA_PARLOR_FRONT_DOOR = PizzaParlorTemplate.PIZZA_PARLOR_FRONT_DOOR
    PIZZA_PARLOR_FRONT_DOOR_PUFFLE_PARTY = PizzaParlorTemplate.PIZZA_PARLOR_FRONT_DOOR_PUFFLE_PARTY
    PIZZA_PARLOR_PIZZA_OVEN = PizzaParlorTemplate.PIZZA_PARLOR_PIZZA_OVEN
    PIZZA_PARLOR_FISH_DISH_MENU = PizzaParlorTemplate.PIZZA_PARLOR_FISH_DISH_MENU

    # Pizza Oven templates
    PIZZA_OVEN_START_BUTTON = PizzaOvenTemplate.PIZZA_OVEN_START_BUTTON
    PIZZA_OVEN_REPLAY_ORDER_BUTTON = PizzaOvenTemplate.PIZZA_OVEN_REPLAY_ORDER_BUTTON
    PIZZA_OVEN_GAME_COLLECT_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_GAME_COLLECT_PIZZA

    PIZZA_OVEN_YELLOW_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_YELLOW_PENGUIN_ASKING_FOR_PIZZA
    PIZZA_OVEN_GREEN_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_GREEN_PENGUIN_ASKING_FOR_PIZZA
    PIZZA_OVEN_PURPLE_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_PURPLE_PENGUIN_ASKING_FOR_PIZZA
    PIZZA_OVEN_RED_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_RED_PENGUIN_ASKING_FOR_PIZZA
    PIZZA_OVEN_BLUE_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_BLUE_PENGUIN_ASKING_FOR_PIZZA
    PIZZA_OVEN_PINK_PENGUIN_ASKING_FOR_PIZZA = PizzaOvenTemplate.PIZZA_OVEN_PINK_PENGUIN_ASKING_FOR_PIZZA

    PIZZA_OVEN_YELLOW_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_YELLOW_PENGUIN
    PIZZA_OVEN_GREEN_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_GREEN_PENGUIN
    PIZZA_OVEN_PURPLE_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_PURPLE_PENGUIN
    PIZZA_OVEN_RED_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_RED_PENGUIN
    PIZZA_OVEN_BLUE_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_BLUE_PENGUIN
    PIZZA_OVEN_PINK_PENGUIN = PizzaOvenTemplate.PIZZA_OVEN_PINK_PENGUIN

    PIZZA_OVEN_EXIT_GAME_BUTTON = PizzaOvenTemplate.PIZZA_OVEN_EXIT_GAME_BUTTON
    PIZZA_OVEN_SECOND_EXIT_GAME_BUTTON = PizzaOvenTemplate.PIZZA_OVEN_SECOND_EXIT_GAME_BUTTON

    # Dojo templates
    DOJO_CARD_JITSU_SIGN = DojoTemplate.DOJO_CARD_JITSU_SIGN
    DOJO_COURTYARD_ABOVE_DOOR = DojoTemplate.DOJO_COURTYARD_ABOVE_DOOR

    # Mine templates
    MINE_SHACK_TO_MINE = MineTemplate.MINE_SHACK_TO_MINE
    MINE_SHACK_TO_RECYCLING_PLANT = MineTemplate.MINE_SHACK_TO_RECYCLING_PLANT
    MINE_SIGN = MineTemplate.MINE_SIGN
    RECYCLING_PLANT_FIRE_ALARM = MineTemplate.RECYCLING_PLANT_FIRE_ALARM
    MINE_TO_CAVE_MINE = MineTemplate.MINE_TO_CAVE_MINE
    CAVE_MINE_HARD_HAT = MineTemplate.CAVE_MINE_HARD_HAT

    # Snow Forts templates
    SNOW_FORTS_CLOCK_TARGET = SnowFortsTemplate.SNOW_FORTS_CLOCK_TARGET


__all__ = [
    "Template",
    "LoginTemplate",
    "UITemplate",
    "MapTemplate",
    "BeachTemplate",
    "SkiiLodgeTemplate",
    "SpyHeadquartersTemplate",
    "CoffeeShopTemplate",
    "GiftShopTemplate",
    "NightClubTemplate",
    "TourHQTemplate",
    "PetShopTemplate",
    "StageTemplate",
    "PizzaParlorTemplate",
    "PizzaOvenTemplate",
    "DojoTemplate",
    "MineTemplate",
    "SnowFortsTemplate",
]
