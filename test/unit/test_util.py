from giges.util import validate_uuid


def test_validate_uuid_bad_format():
    assert validate_uuid("Nope") is False


def test_validate_uuid_not_string():
    assert validate_uuid(3) is False


def test_validate_uuid():
    assert validate_uuid("d6f0e3bb-8fea-42f3-89eb-6baae25f15da") is True
