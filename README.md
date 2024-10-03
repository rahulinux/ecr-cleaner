# Python Package template - 2024

![Build Status](https://github.com/MihaiBojin/template-python-package-2024/actions/workflows/python-tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/template-python-package-2024.svg)](https://badge.fury.io/py/template-python-package-2024)
[![Python Versions](https://img.shields.io/pypi/pyversions/template-python-package-2024.svg)](https://pypi.org/project/template-python-package-2024/)
[![License](https://img.shields.io/github/license/MihaiBojin/template-python-package-2024.svg)](LICENSE)

Use this repo as a template for starting multi-package Python projects.

## Quickstart

The project is published to <https://pypi.org/project/template-python-package-2024/>.
Install it via:

```shell
pip install template-python-package-2024

# or alternatively, directly from git
pip install "git+https://github.com/MihaiBojin/template-python-package-2024@main"
```

## Publishing to PyPI

### GitHub-based version publishing

The simplest way to publish a new version (if you have committer rights) is to tag a commit and push it to the repo:

```shell
# At a certain commit, ideally after merging a PR to main
git tag v0.1.x
git push origin v0.1.x
```

A [GitHub Action](https://github.com/MihaiBojin/template-python-package-2024/actions) will run, build the library and publish it to PyPI.

### Manual

These steps can also be performed locally. For these commands to work, you will need to export two environment variables:

```shell
export TESTPYPI_PASSWORD=... # token for https://test.pypi.org/legacy/
export PYPI_PASSWORD=... # token for https://upload.pypi.org/legacy/
```

First, publish to the test repo and inspect the package:

```shell
make publish-test
```

If correct, distribute the wheel to the PyPI index:

```shell
make publish
```

Verify the distributed code

```shell
make publish-verify
```

## Building a Docker image

Build an image with:

```shell
make docker
```

and run it with

```shell
make docker-run
# or
make docker-run ARGS="--arg1 --arg2 --etc"
```
