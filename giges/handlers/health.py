from typing import Dict, Tuple


def ping() -> Tuple[Dict[str, bool], int]:
    """
    A trivial response to verify that the service is working.

    :return: a tuple with the response body and the status
    """
    return {"pong": True}, 200
