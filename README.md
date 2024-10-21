## ECR Image Cleanup Tool

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [GitHub-based version publishing](#github-based-version-publishing)
- [Manual](#manual)
- [Building a Docker image](#building-a-docker-image)
- [Usage](#usage)


## Overview

The ECR Image Cleanup Tool addresses limitations in Amazon ECR's built-in lifecycle policies, particularly for multi-architecture images. It helps prevent repositories from hitting the 10,000 image hard limit imposed by ECR by providing more flexible and architecture-aware cleanup options.

## Features

1. Supports multi-architecture image cleanup
2. Allows fine-grained control over image retention
3. Can keep a specified number of recent images for each tag
4. Manages untagged images separately
5. Provides a dry-run option to preview actions before execution

### GitHub-based version publishing

The simplest way to publish a new version (if you have committer rights) is to tag a commit and push it to the repo:

**At a certain commit, ideally after merging a PR to main**

```shell
git tag v0.1.x
git push origin v0.1.x
```

### Manual

These steps can also be performed locally. For these commands to work, you will need to export two environment variables:

```shell
export TESTPYPI_PASSWORD=... # token for https://test.pypi.org/legacy/
export PYPI_PASSWORD=... # token for https://upload.pypi.org/legacy/
```

First, publish to the test repo and inspect the package:

```shell
task publish-test
```

If correct, distribute the wheel to the PyPI index:

Verify the distributed code

```shell
task publish-verify
```

## Building a Docker image

Build an image with:

IMPORTANT: This project uses [taskfile.dev](https://taskfile.dev/installation/),
which you will need to install for running the following commands:

```shell
task docker-build
```

and run it with

```shell
task docker-run
# or
task docker-run ARGS="--repositories my-repo:tag-prefix=2,untagged=10 --region us-east-2 --dry-run"
```

### Installation

```shell
pip install ecr-cleaner
```

### Usage

Support following CLI argument

```shell
usage: ecr_cleaner [-h] [--config-file CONFIG_FILE] [--repositories REPOSITORIES [REPOSITORIES ...]] [--region REGION] [--batch-size BATCH_SIZE] [--dry-run] [--debug]

ECR Cleaner CLI

options:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        Path to configuration file in YAML format. See example in README.md
  --repositories REPOSITORIES [REPOSITORIES ...]
                        List of repository names and policies(keep-most-recent). (e.g. my-repo:latest=3,tag-prefix=2,untagged=10)
  --region REGION       ECR region
  --batch-size BATCH_SIZE
                        Max number of images that can be deleted in one call
  --dry-run             Check result without deleting images
  --debug               Enable debug logging
```

Clean-up will keep most recent number of images based on inputs and it will delete remaining matching tagPrefix
