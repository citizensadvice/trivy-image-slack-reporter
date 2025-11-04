"""Slack message blocks for Trivy image Slack reporter.

This module defines various Slack message block types used to construct
messages sent to Slack channels. Each block type is represented by a class
that implements the Block interface.

By constructing a list of these blocks, we can then render them into the
format required by the Slack API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Block(ABC):
    """Base class for Slack message blocks."""

    @abstractmethod
    def render(self) -> dict:
        pass


class Divider(Block):
    """Divider block for Slack messages."""

    def render(self) -> dict:
        return {"type": "divider"}


@dataclass
class Header(Block):
    """Header block for Slack messages.

    Plain text with emoji support enabled.
    """

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
    """Markdown section block for Slack messages.

    Markdown formatted text.
    """

    text: str

    def render(self) -> dict:
        return {
            "type": "section",
            "text": {"type": "mrkdwn", "text": self.text},
        }
