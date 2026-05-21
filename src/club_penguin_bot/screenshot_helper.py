from datetime import datetime
from pathlib import Path
import os

import cv2

from club_penguin_bot.bot import Bot


def main():
    url = os.getenv("CPJ_URL", "https://play.cpjourney.net/")
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    with Bot(url) as bot:
        while True:
            input(
                "Browser launched. Navigate where needed, then press Enter to capture screenshot... "
            )
            image = bot.screenshot()
            if image is None:
                raise RuntimeError("Failed to capture screenshot.")

            filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            output_path = templates_dir / filename
            cv2.imwrite(str(output_path), image)
            print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
