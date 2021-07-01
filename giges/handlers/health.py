from typing import Dict, Tuple


def ping() -> Tuple[Dict[str, bool], int]:
    return {"pong": True}, 200
