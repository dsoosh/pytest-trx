import os
from pathlib import Path

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
    path = os.path.join(Path(Path(__file__).parent, "lena.png"))
    trx.attachments.append(path)

def test_attachment_with_fail(trx):
    path = os.path.join(Path(Path(__file__).parent, "lena.png"))
    trx.attachments.append(path)
    pytest.fail("woah")

def test_failing_with_traceback():
    def loop():
        return loop()

    print("loopeedeedoo")
    loop()
