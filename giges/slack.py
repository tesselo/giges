from typing import Any, Optional

import structlog
from flask import current_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

logger = structlog.get_logger(__file__)


class SlackClient(WebClient):
    def __init__(self, **kwargs: Any):
        super().__init__(token=current_app.config["SLACK_TOKEN"], **kwargs)

    def send_message(
        self, channel: str, message: str
    ) -> Optional[SlackResponse]:
        try:
            return self.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            logger.error("Failed to send a message to slack", error=e)
            return None

    def send_to_road_blocks(self, message: str) -> Optional[SlackResponse]:
        return self.send_message(
            current_app.config["SLACK_BLOCKS_CHANNEL"], message
        )
