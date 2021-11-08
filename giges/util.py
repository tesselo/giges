from uuid import UUID


def validate_uuid(test_uuid: str) -> bool:
    if not isinstance(test_uuid, str):
        return False
    try:
        gen_uuid = UUID(test_uuid)
        return str(gen_uuid) == test_uuid
    except (ValueError, TypeError):
        return False
