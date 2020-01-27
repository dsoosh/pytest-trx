# pytest-trx


[![Build Status](https://dev.azure.com/DariuszSuszczewicz/mcaky/_apis/build/status/dsoosh.pytest-trx?branchName=master)](https://dev.azure.com/DariuszSuszczewicz/mcaky/_build/latest?definitionId=1&branchName=master) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

VSTest-style report for pytest (and Azure DevOps)

## Why?

\- "There's [pytest-html](https://pypi.org/project/pytest-html/)

## Usage
Once installed the plugin is enabled by default and produces a `results.trx` file 
in current working directory. This behavior can be overriden by specifying a 
`--trx path/to/report.trx` command line argument.

## Attachment support

`pytest-trx` comes with a session-scope `trx` fixture you can use to enhance your
test report with attachments in two ways:

- add test run attachment - 
```python
def test_add_test_run_attachment(trx):
    trx.add_test_run_attachment(uri="path/to/attachment.png")
```

- add test-specific attachment
```python
def test_add_test_result_attachment(trx, request):
    trx.add_test_attachment(test=request.nodeid, uri="path/to/attachment.png")
```
