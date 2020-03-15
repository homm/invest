from parameterized import parameterized

from _crypto import is_password_weak


@parameterized([
    ("AbCdAbCdAbCd",   False, None),
    ("AbCd1234 AbCd",  False, None),
    ("AbCd1234 Ab",    True, "password is too short"),
    ("AbCd1234\tAbCd", True, "not all chars are printable"),
    ("AbCd1234 Абвг",  True, "not ascii chars"),
    ("abcd1234 abcd",  True, "all chars are lower"),
    ("ABCD1234 ABCD",  True, "all chars are upper"),
    ("123412341234",   True, "all chars are digits"),
])
def test_is_password_weak(password, weak, reason):
    assert (weak, reason) == is_password_weak(password)
