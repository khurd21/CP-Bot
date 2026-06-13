from typing import Optional
from dataclasses import dataclass, field
from enum import Enum, StrEnum
import os
import re
import time
from collections import Counter

import cv2
import numpy as np
import pytesseract
from playwright.sync_api import Response

from club_penguin_bot.actions.base_action import BaseAction
from club_penguin_bot.destinations import Destination
from club_penguin_bot.templates import Template
from club_penguin_bot.protocols import BotProtocol


class CardJitsuSide(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    UNKNOWN = "unknown"


@dataclass
class CardJitsuSettings:
    player_name: str = field(default_factory=lambda: os.environ["CPJ_USERNAME"])
    game_start_timeout_ms: int = 60000 * 2
    side_detection_timeout_ms: int = 60000 * 2
    side_detection_interval_ms: int = 750


class Type(StrEnum):
    ICE = "ice"
    FIRE = "fire"
    WATER = "water"


class Color(Enum):
    PURPLE = (163, 106, 186, 255)
    RED = (226, 74, 62, 255)
    GREEN = (97, 160, 78, 255)
    ORANGE = (247, 176, 75, 255)
    YELLOW = (250, 232, 53, 255)
    BLUE = (17, 72, 161, 255)


@dataclass
class Card:
    type: Type
    color: Color
    value: Optional[int] = None


@dataclass
class Player:
    cards: list[Card] = field(default_factory=list)
    score: list[Card] = field(default_factory=list)
    side: CardJitsuSide = CardJitsuSide.UNKNOWN


@dataclass
class CardJitsuGameState:
    started: bool = False
    player: Player = field(default_factory=Player)
    enemy: Player = field(default_factory=Player)


@dataclass
class CardJitsuAction(BaseAction):
    bot: BotProtocol
    settings: CardJitsuSettings = field(default_factory=CardJitsuSettings)
    state: CardJitsuGameState = field(default_factory=CardJitsuGameState, init=False)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return "".join(value.split()).lower()

    @staticmethod
    def _is_number_png_response(response: Response) -> bool:
        return re.search(r"/\d+\.png(?:\?.*)?$", response.url.lower()) is not None

    def _wait_for_game_ready(self) -> None:
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        deck_card_count = 0

        def is_deck_card_response(response: Response) -> bool:
            return re.search(r"/\d+\.png(?:\?.*)?$", response.url.lower()) is not None

        def on_response(response: Response) -> None:
            nonlocal deck_card_count
            if not is_deck_card_response(response):
                return
            deck_card_count += 1

        self.bot.page.on("response", on_response)

        try:
            deadline = time.perf_counter() + (self.settings.game_start_timeout_ms / 1000)
            while time.perf_counter() < deadline:
                if deck_card_count >= 5:
                    return
                self.bot.page.wait_for_timeout(100)
        finally:
            self.bot.page.remove_listener("response", on_response)

        raise TimeoutError("Timed out waiting for five deck card png responses.")

    @staticmethod
    def _contains_player_name(screen: np.ndarray, player_name: str) -> bool:
        upscaled = cv2.resize(screen, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # data = pytesseract.image_to_data(screen, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(binary, config="--psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ")
        normalized_player_name = CardJitsuAction._normalize_text(player_name)
        normalized_text = CardJitsuAction._normalize_text(text)
        return normalized_player_name in normalized_text

    def detect_side_from_screenshot(self, screen: np.ndarray) -> CardJitsuSide:
        half_width = screen.shape[1] // 2
        left_half = screen[:, :half_width]
        right_half = screen[:, half_width:]

        left_found = self._contains_player_name(left_half, self.settings.player_name)
        right_found = self._contains_player_name(right_half, self.settings.player_name)

        if left_found and not right_found:
            return CardJitsuSide.LEFT
        if right_found and not left_found:
            return CardJitsuSide.RIGHT
        if left_found and right_found:
            raise ValueError(f"Found player name {self.settings.player_name} on both sides of the screen.")

        return CardJitsuSide.UNKNOWN

    def detect_side(self) -> CardJitsuSide:
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        deadline = time.perf_counter() + (self.settings.side_detection_timeout_ms / 1000)
        last_side = CardJitsuSide.UNKNOWN
        while time.perf_counter() < deadline:
            last_side = self.detect_side_from_screenshot(self.bot.screenshot())
            if last_side is not CardJitsuSide.UNKNOWN:
                return last_side
            self.bot.page.wait_for_timeout(self.settings.side_detection_interval_ms)

        return last_side

    @staticmethod
    def _color_from_bgr(pixel: tuple[int, int, int], tolerance: float = 55.0) -> Optional[Color]:
        b, g, r = pixel
        best: Optional[Color] = None
        best_distance = float("inf")
        for color in Color:
            cr, cg, cb, _ = color.value
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best = color
        if best is None or best_distance > tolerance:
            return None
        return best

    @staticmethod
    def _nearest_color_from_bgr(pixel: tuple[int, int, int]) -> Color:
        b, g, r = pixel
        best = Color.BLUE
        best_distance = float("inf")
        for color in Color:
            cr, cg, cb, _ = color.value
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best = color
        return best

    @staticmethod
    def _read_card_value(screen_column: np.ndarray) -> tuple[Optional[int], Optional[int]]:
        # OCR robustness aligned with name detection: upscale + denoise + contrast + threshold
        scale = 2
        upscaled = cv2.resize(screen_column, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        variants = [
            cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1],
            enhanced,
        ]
        psm_modes = (6, 7, 8, 10, 13)

        best: tuple[Optional[int], Optional[int], float] = (None, None, -1.0)
        for img in variants:
            for psm in psm_modes:
                data = pytesseract.image_to_data(
                    img,
                    config=f"--psm {psm} -c tessedit_char_whitelist=0123456789",
                    output_type=pytesseract.Output.DICT,
                )
                for i, text in enumerate(data["text"]):
                    token = re.sub(r"\D", "", text or "")
                    if not token:
                        continue
                    value = int(token)
                    if value < 1 or value > 10:
                        continue
                    conf_raw = data["conf"][i]
                    conf = float(conf_raw) if str(conf_raw).strip() not in ("", "-1") else 0.0
                    top = int(data["top"][i]) // scale
                    if conf > best[2]:
                        best = (value, top, conf)

        return best[0], best[1]

    def _detect_card_color(
        self,
        screen: np.ndarray,
        ex: int,
        ey: int,
        ew: int,
        eh: int,
        value_top_abs: int,
    ) -> Color:
        full_h, full_w = screen.shape[:2]
        x0 = max(0, ex - max(3, ew // 3))
        x1 = min(full_w, ex + ew + max(3, ew // 3))

        y0 = min(full_h - 1, ey + eh + 2)
        y1 = min(full_h, max(y0 + 4, value_top_abs - 2))
        if y1 <= y0:
            y1 = min(full_h, y0 + 16)

        strip = screen[y0:y1, x0:x1]
        if strip.size == 0:
            # deterministic fallback
            return Color.BLUE

        # Keep saturated pixels (ignore gray/white UI noise)
        hsv = cv2.cvtColor(strip, cv2.COLOR_BGR2HSV)
        sat_mask = hsv[:, :, 1] > 60
        pixels = strip[sat_mask]

        if pixels.size == 0:
            mean = strip.reshape(-1, 3).mean(axis=0)
            return self._nearest_color_from_bgr((int(mean[0]), int(mean[1]), int(mean[2])))

        votes: list[Color] = []
        for b, g, r in pixels[::2]:  # sample every other pixel for speed
            matched = self._color_from_bgr((int(b), int(g), int(r)), tolerance=80.0)
            if matched is not None:
                votes.append(matched)

        if votes:
            return Counter(votes).most_common(1)[0][0]

        mean = pixels.reshape(-1, 3).mean(axis=0)
        return self._nearest_color_from_bgr((int(mean[0]), int(mean[1]), int(mean[2])))

    def scan_player_cards(self) -> list[Card]:
        if self.state.player.side is CardJitsuSide.UNKNOWN:
            raise ValueError("Unable to scan cards: player side is unknown.")

        screen = self.bot.screenshot()
        full_h, full_w = screen.shape[:2]

        y0 = (full_h * 2) // 3
        y1 = full_h
        x_cut = (full_w * 2) // 3

        if self.state.player.side is CardJitsuSide.LEFT:
            x0, x1 = 0, x_cut
        else:
            x0, x1 = full_w - x_cut, full_w

        focus = screen[y0:y1, x0:x1]
        cv2.imwrite("card-jitsu-focus.png", focus)

        templates: list[tuple[Type, Template]] = [
            (Type.FIRE, Template.FIRE_EMBLEM_PLAYER_CARD),
            (Type.WATER, Template.WATER_EMBLEM_PLAYER_CARD),
            (Type.ICE, Template.ICE_EMBLEM_PLAYER_CARD),
            (Type.ICE, Template.ICE_EMBLEM_PLAYER_CARD_2),
        ]

        raw_matches: list[tuple[Type, int, int, int, int, float]] = []
        for card_type, template_name in templates:
            matches = self.bot.find_template_matches_in(
                focus,
                template_name,
                threshold=0.85,
                grayscale=True,
            )
            for mx, my, tw, th, score in matches:
                raw_matches.append((card_type, x0 + mx, y0 + my, tw, th, score))

        # Keep high-confidence, non-overlapping emblem detections.
        raw_matches.sort(key=lambda item: item[5], reverse=True)
        chosen: list[tuple[Type, int, int, int, int, float]] = []
        for candidate in raw_matches:
            _, cx, cy, cw, ch, _ = candidate
            is_overlap = False
            for _, ox, oy, ow, oh, _ in chosen:
                if abs(cx - ox) < max(cw, ow) // 2 and abs(cy - oy) < max(ch, oh) // 2:
                    is_overlap = True
                    break
            if not is_overlap:
                chosen.append(candidate)
            if len(chosen) == 5:
                break

        if len(chosen) != 5:
            raise ValueError(f"Expected 5 player card emblems, found {len(chosen)}.")

        chosen.sort(key=lambda item: item[1])
        cards: list[Card] = []
        for card_type, ex, ey, ew, eh, _ in chosen:
            pad = max(8, ew)
            col_x0 = max(0, ex - pad)
            col_x1 = min(full_w, ex + ew + pad)
            value_y0 = min(full_h, ey + eh)
            value_y1 = min(full_h, value_y0 + max(16, (full_h - value_y0) // 4))
            value_column = screen[value_y0:value_y1, col_x0:col_x1]

            value, value_top_rel = self._read_card_value(value_column)
            if value is None:
                raise ValueError(f"Could not read card value below emblem at x={ex}, y={ey}.")

            value_top_abs = value_y0 + (value_top_rel or 0)
            card_color = self._detect_card_color(screen, ex, ey, ew, eh, value_top_abs)

            cards.append(Card(type=card_type, color=card_color, value=value))

        return cards

    def scan_score(self, _side: CardJitsuSide) -> list[Card]:
        return []

    def run(self) -> None:
        if self.bot.page is None:
            raise ValueError("Page cannot be None.")

        self.bot.travel(Destination.DOJO)
        self.bot.click_template(Template.DOJO_CARD_JITSU_SIGN)
        self.bot.page.wait_for_timeout(5000)
        self.bot.click_template_retry(Template.YES_BUTTON)
        self.bot.page.wait_for_timeout(2000)
        self.bot.click_template_retry(Template.CARD_JISTU_EARN_YOUR_BELTS_BUTTON)

        # Step 1
        # Game Ready: walk.swf, tie.swf get sent.
        # Game Ready: 5 *.png images go through network consecutively.
        print("Waiting for game to be ready...")
        self._wait_for_game_ready()
        print("Card-Jitsu screen is ready!")
        self.state.started = True
        self.state.player.side = self.detect_side()
        self.state.enemy.side = CardJitsuSide.LEFT
        if self.state.player.side == CardJitsuSide.LEFT:
            self.state.enemy.side = CardJitsuSide.RIGHT
        print(f"Side: {self.state.player.side.value}")

        while True:
            # Step 2
            # Scan player cards.
            self.bot.page.wait_for_timeout(1500)
            self.state.player.cards = self.scan_player_cards()
            print(f"Scanned deck: {self.state.player.cards}")

            # Step 3
            # Scan the score for oponent and player
            self.state.player.score = self.scan_score(self.state.player.side)
            self.state.enemy.score = self.scan_score(self.state.enemy.side)

            # Step 4
            # Pick optimal card selection

            # Step 5
            # Listen for oponent <number>.png request. This request indicates the enemy selected a card
            # Oponent selected a card <number.png gets sent
            print("Waiting for enemy to play a card.")
            with self.bot.page.expect_response(self._is_number_png_response, timeout=self.settings.game_start_timeout_ms):
                pass
            print("Card was played.")

            # Step 6
            # Listen for player <number>.png request. This request / response indicates the player drew a card.
            # Player "draws" a new card, indicating the next turn: <number>.png gets sent
            print("Waiting for user to draw card.")
            with self.bot.page.expect_response(self._is_number_png_response, timeout=self.settings.game_start_timeout_ms):
                pass
            print("Card drawn! Reading deck...")

            # Step 7
            # If the previous round had a player or oponent one card away from winning, check for "OK" button.
            # If OK button exists, round ended and someone won. Scan the words on the screen to see if the name is the
            # user's name.
            # Otherwise, no win condition, repeat step 2.

            ## Step ??
            # If you earn a new belt, you see a background with sensei. Click twice to go back to the dojo.


def main():
    from club_penguin_bot.bot import Bot  # pylint: disable=C0415

    url = os.environ["CPJ_URL"]
    user = os.environ["CPJ_USERNAME"]
    password = os.environ["CPJ_PASSWORD"]
    server = os.getenv("CPJ_SERVER", "Blizzard")
    with Bot(url=url) as bot:
        bot.login(username=user, password=password, server=server)
        while True:
            CardJitsuAction(bot).run()


if __name__ == "__main__":
    main()
