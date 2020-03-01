import getpass
import uuid
from dataclasses import dataclass

from attrdict import AttrDict


class TestRun:
    def __init__(self):
        self.id = uuid.uuid4()
        self.name = "default"  # todo
        self.run_user = getpass.getuser()
        self.xmlns = "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"

    @property
    def attribs(self):
        return {
            "id": self.id,
            "name": self.name,
            "runUser": self.run_user,
            "xmlns": self.xmlns,
        }


class ResultSummary:
    outcome = None


class Counters:
    total = 0
    executed = 0
    passed = 0
    error = 0
    failed = 0
    timeout = 0
    aborted = 0
    inconclusive = 0
    passedButRunAborted = 0
    notRunnable = 0
    notExecuted = 0
    disconnected = 0
    warning = 0
    completed = 0
    inProgress = 0
    pending = 0


@dataclass
class Times:
    creation = ""
    queuing = ""
    start = ""
    finish = ""

t = Times()


i = AttrDict({"foo": 1})
print(i.foo)
