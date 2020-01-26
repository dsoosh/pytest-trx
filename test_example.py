import os

import pytest


@pytest.fixture
def failing_setup():
    assert False


@pytest.fixture
def failing_teardown():
    yield
    assert False


def test_no_attachment():
    assert True


def test_fail():
    assert False


def test_failing_setup(failing_setup):
    pass


def test_failing_teardown(failing_teardown):
    pass


def test_attachment(trx):
    trx.attachments.append(os.path.join(os.path.abspath(__file__), "lena.png"))


def test_failing_with_traceback():
    def loop():
        return loop()

    print("loopeedeedoo")
    loop()
