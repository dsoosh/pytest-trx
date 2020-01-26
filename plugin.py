from __future__ import annotations
import time
import uuid
from datetime import datetime
from pprint import pprint
from typing import Dict, List, Type

import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureDef, FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport
from lxml.builder import ElementMaker
from lxml.etree import Element, tostring, SubElement


class Report:
    def __init__(self):
        super(Report, self).__init__()
        self._attachments = list()

    @property
    def attachments(self):
        return self._attachments

    @attachments.setter
    def attachments(self, uri: str):
        self._attachments.append(uri)


class TrxBuilder:
    tests: Dict[Item, Report]

    def __init__(self):
        self._root: Element = Element("TestRun",
                                      attrib={
                                          "xmlns": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010",
                                          "id": str(uuid.uuid4()),
                                          "name": "example",
                                      })
        self.tests = dict()

    def set_start_time(self, dt: datetime) -> TrxBuilder:
        return self._set_times("start", dt)

    def _set_times(self, when, dt):
        times = self._get_or_create(self._root, "Times")
        times.attrib[when] = str(dt)
        return self

    def set_finish_time(self, dt: datetime) -> TrxBuilder:
        return self._set_times("finish", dt)

    def set_creation_time(self, dt: datetime):
        return self._set_times("creation", dt)

    def set_attachments(self, test: Item, attachments: List[str]):
        results = self._root.find("Results")
        unittestresult = self._get_or_create(results, "UnitTestResult", testId=test.nodeid)
        result_files = self._get_or_create(unittestresult, "ResultFiles")
        for attachment in attachments:
            self._get_or_create(result_files, "ResultFile", path=attachment)

        return self

    def build(self) -> bytes:
        return tostring(self._root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def _get_or_create(self, root: Element, etype: str, **attribs) -> Element:
        _formatted_attribs = "".join(f"[@{attrib}='{value}']" for attrib, value in attribs.items())
        locator = f"{etype}{_formatted_attribs}"
        node = next(iter(root.findall(locator)), None)
        if node is None:
            node = SubElement(root, etype, attrib=attribs)
        return node

    def set_test_result(self, result: TestReport, test_type: str = "UnitTest"):
        results = self._get_or_create(self._root, "Results")
        _result = self._get_or_create(results, test_type + "Result", testId=result.nodeid)
        _result.attrib.update({
            "testName": result.nodeid,  # TODO
            "testType": test_type,  # TODO
            "testId": result.nodeid,  # TODO
            "testListId": "dummy",  # TODO
            "computerName": "dummy",  # TODO
        })
        if result.when == "call":
            _result.attrib.update({
                "outcome": result.outcome.upper(),
                "duration": str(result.duration),
            })
        if result.capstdout:
            self._set_output(_result, "StdOut", result.capstdout)
        if result.longrepr:
            self._set_error_info(_result, result)
        return self

    def _set_error_info(self, _result, result):
        output = self._get_or_create(_result, "Output")
        errorinfo = self._get_or_create(output, "ErrorInfo")
        message = self._get_or_create(errorinfo, "Message")
        stacktrace = self._get_or_create(errorinfo, "StackTrace")
        message.text = str(result.longrepr.reprcrash)
        stacktrace.text = str(result.longrepr.reprtraceback)

    def _set_output(self, result, output_type, text):
        output = self._get_or_create(result, "Output")
        stdout = self._get_or_create(output, output_type)
        if stdout.text is None:
            stdout.text = text
        else:
            stdout.text += text
        return output

    def set_test_definition(self, item: Item, test_type: str = "UnitTest"):
        definitions = self._get_or_create(self._root, "TestDefinitions")
        definition = self._get_or_create(definitions, test_type, id=item.nodeid)
        definition.attrib.update({"id": item.nodeid, "name": item.nodeid})
        test_method = self._get_or_create(definition, "TestMethod")
        test_method.attrib.update({
            "codeBase": "dummy",  # TODO
            "className": "dummy",  # TODO
            "name": "dummy",  # TODO
        })
        return self


class Plugin:

    def __init__(self):
        self.builder = TrxBuilder()
        self.builder.set_creation_time(datetime.now())

    def pytest_sessionstart(self, session: Session):
        self.builder.set_start_time(datetime.now())

    def pytest_sessionfinish(self, session: Session):
        self.builder.set_finish_time(datetime.now())
        with open("tr.trx", "wb+") as dump:
            dump.write(self.builder.build())

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            self.builder.set_test_definition(item)

    def pytest_runtest_logreport(self, report: TestReport):
        self.builder.set_test_result(report)

    def pytest_fixture_post_finalizer(self, fixturedef, request: FixtureRequest):
        if fixturedef.argname == "trx":
            trx = fixturedef.cached_result[0]
            self.builder.set_attachments(request.node, trx.attachments)


@pytest.fixture
def trx():
    return Report()


def pytest_configure(config):
    trx = Plugin()
    config.trx = trx
    config.pluginmanager.register(trx)


def pytest_unconfigure(config):
    if hasattr(config, "trx"):
        config.pluginmanager.unregister(getattr(config, "trx"))
        del config.trx
