from abc import ABC, abstractmethod


class BaseAction(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
