from abc import ABC, abstractmethod
from dataclasses import dataclass


class Block(ABC):
    @abstractmethod
    def render(self) -> dict:
        pass


class Divider(Block):
    def render(self) -> dict:
        return {"type": "divider"}


@dataclass
class Header(Block):
    title: str

    def render(self) -> dict:
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": self.title,
                "emoji": True,
            },
        }


@dataclass
class MarkdownSection(Block):
    text: str

    def render(self) -> dict:
        return {
            "type": "section",
            "text": {"type": "mrkdwn", "text": self.text},
        }
