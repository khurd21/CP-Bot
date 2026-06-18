import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import sys
import keyring
from keyring.errors import PasswordDeleteError

from PyQt6 import QtWidgets

from club_penguin_ui.ui_mainwindow import Ui_MainWindow
from club_penguin_ui.ui_settings import Ui_Settings

SERVICE = "ClubPenguinBot"
ACCOUNT = "main"


@dataclass
class AppConfig:
    username: str
    server: str
    url: str

    @property
    def password(self) -> Optional[str]:
        return keyring.get_password(SERVICE, ACCOUNT)

    @password.setter
    def password(self, value: Optional[str]) -> None:
        if value is None or value == "":
            try:
                keyring.delete_password(SERVICE, ACCOUNT)
            except PasswordDeleteError:
                pass
        else:
            keyring.set_password(SERVICE, ACCOUNT, value)

    @staticmethod
    def from_json(path: Path) -> "AppConfig":
        if not path.exists():
            raise FileNotFoundError(f"File {path.absolute()} does not exist.")

        raw = json.loads(path.read_text(encoding="utf-8"))
        return AppConfig(
            username=raw.get("username", ""),
            server=raw.get("server", ""),
            url=raw.get("url", ""),
        )

    def to_json(self) -> dict[str, str]:
        return {
            "username": self.username,
            "server": self.server,
            "url": self.url,
        }


CONFIG_PATH = ""


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        return AppConfig.from_json(self.path)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.config:
            self.path.write_text(json.dumps(asdict(self.config), indent=2), encoding="utf-8")


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.settingsTabLayout.addWidget(SettingsWidget(self.ui.settingsTab))

        self.ui.actionActions.triggered.connect(self.open_actions)
        self.ui.actionSettings.triggered.connect(self.open_settings)

    def open_actions(self) -> None:
        self.ui.mainTabWidget.setCurrentWidget(self.ui.actionsTab)

    def open_settings(self) -> None:
        self.ui.mainTabWidget.setCurrentWidget(self.ui.settingsTab)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
