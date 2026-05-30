from enum import Enum
from pathlib import Path

import cv2
import pytest

from club_penguin_bot import templates as template_package


def _iter_template_enums() -> list[tuple[str, type[Enum]]]:
    enums: list[tuple[str, type[Enum]]] = []
    for name in getattr(template_package, "__all__", []):
        value = getattr(template_package, name, None)
        if isinstance(value, type) and issubclass(value, Enum) and name.endswith("Template"):
            enums.append((name, value))
    return enums


def _iter_template_members() -> list[tuple[str, Enum]]:
    members: list[tuple[str, Enum]] = []
    for enum_name, enum_type in _iter_template_enums():
        for member in enum_type:
            members.append((enum_name, member))
    return members


def test_discovers_template_enums() -> None:
    assert _iter_template_enums(), "No template enums were discovered from club_penguin_bot.templates.__all__."


@pytest.mark.parametrize(
    ("enum_name", "member"),
    _iter_template_members(),
    ids=lambda item: item if isinstance(item, str) else item.name,
)
def test_template_path_exists_and_is_image(enum_name: str, member: Enum) -> None:
    templates_dir = Path(template_package.__file__).resolve().parent
    relative_path = Path(str(member.value))
    assert relative_path.suffix.lower() == ".png", f"{enum_name}.{member.name} does not point to a PNG file: {relative_path}"

    absolute_path = templates_dir / relative_path
    assert absolute_path.exists(), f"{enum_name}.{member.name} points to a missing file: {absolute_path}"
    assert absolute_path.is_file(), f"{enum_name}.{member.name} does not point to a file: {absolute_path}"

    image = cv2.imread(str(absolute_path), cv2.IMREAD_COLOR)
    assert image is not None, f"{enum_name}.{member.name} is not a readable image: {absolute_path}"
