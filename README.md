## ECR Image Cleanup Tool

![Build Status](https://github.com/rahulinux/ecr-cleaner/actions/workflows/python-tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/ecr-cleaner.svg)](https://badge.fury.io/py/ecr-cleaner)
[![Python Versions](https://img.shields.io/pypi/pyversions/ecr-cleaner.svg)](https://pypi.org/project/ecr-cleaner/)
[![License](https://img.shields.io/github/license/rahulinux/ecr-cleaner.svg)](LICENSE)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)


## Overview

The ECR Image Cleanup Tool addresses limitations in Amazon ECR's built-in lifecycle policies, particularly for multi-architecture images. It helps prevent repositories from hitting the 10,000 image hard limit imposed by ECR by providing more flexible and architecture-aware cleanup options.

## Features

1. Supports multi-architecture image cleanup
2. Allows fine-grained control over image retention
3. Can keep a specified number of recent images for each tag
4. Manages untagged images separately
5. Provides a dry-run option to preview actions before execution


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

## Config example

```yaml
region: eu-central-1
repositories:
  - rahul-test:pinned=1,untagged=3
```

## Helm chart

## Prerequisites

AWS IAM role permission to manage ECR repositories

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ecr-cleaner",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchDeleteImage",
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ecr:ListImages",
        "ecr:DescribeRepositories"
      ]
    }
  ]
}
```

## Installation

[Helm Readme](./charts/ecr-cleaner/README.md)
