"""
A ECR Cleaner CLI
==========

Example configuration file:

.. code-block:: yaml

    repositories:
      - my-repo:latest=3,stable=2,untagged=10
      - my-other-repo:tag-prefix=1,stable=1,untagged=5

"""

import os
import sys

import json
import yaml

from argparse import ArgumentParser, FileType
from dataclasses import dataclass, astuple
from typing import Dict, List, Tuple

from ecr_cleaner import Repository
from ecr_cleaner.helpers import get_logger, config_logger

log_level = "DEBUG" if "--debug" in sys.argv else os.environ.get("LOG_LEVEL", "INFO")
config_logger(log_level)
log = get_logger()


@dataclass
class RepositoryConfig:
    name: str
    policy: Dict[str, int]

    def __iter__(self):
        return iter(astuple(self))


def parse_repository_config(repo_config: str) -> RepositoryConfig:
    """
    Parse a single repository configuration string.

    Args:
        repo_config: Repository configuration string (e.g. my-repo:latest=3,tag-prefix=2,untagged=10)

    Returns:
        RepositoryConfig {name: str, policy: Dict[str, int]}
    """
    try:
        repo_name, policy = repo_config.split(":")
        tag_policy = dict(
            tuple(int(i) if i.isdigit() else i for i in item.split("="))
            for item in policy.split(",")
            if "=" in item
        )
        tag_policy.setdefault("untagged", 0)
        return RepositoryConfig(name=repo_name, policy=tag_policy)
    except ValueError as e:
        raise ValueError(f"Invalid repository configuration: {repo_config}") from e


def parse_args() -> Tuple[List[RepositoryConfig], bool, bool]:
    parser = ArgumentParser(description="ECR Cleaner CLI")
    parser.add_argument(
        "--config-file",
        help="Path to configuration file in YAML format. See example in README.md",
        type=FileType("r"),
        required=False,
    )
    parser.add_argument(
        "--repositories",
        nargs="+",
        action="extend",
        help="List of repository names and policies(keep-most-recent). (e.g. my-repo:latest=3,tag-prefix=2,untagged=10)",
    )
    parser.add_argument(
        "--region",
        help="ECR region",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Max number of images that can be deleted in one call",
    )
    parser.add_argument(
        "--dry-run",
        help="Check result without deleting images",
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
    )
    args = parser.parse_args()

    if not (args.config_file or (args.repositories and args.region)):
        parser.print_help()
        sys.exit(1)

    dry_run = args.dry_run
    batch_size = args.batch_size
    if args.config_file:
        config = yaml.safe_load(args.config_file)
        repositories = config.get("repositories", [])
        region = config.get("region")
    else:
        repositories = args.repositories or []
        region = args.region

    repository_list = [parse_repository_config(repo) for repo in repositories]

    return repository_list, region, batch_size, dry_run


def main() -> None:
    repositories, region, batch_size, dry_run = parse_args()

    log.debug("args", region=region)
    log.debug("args", dry_run=dry_run)
    log.debug("args", batch_size=batch_size)
    log.debug("args", repositories=json.dumps(repositories, indent=4, default=str))

    for repo in repositories:
        repo_name, tag_policy = repo
        repo = Repository(repo_name, region, batch_size)
        repo.manage_images(policy=tag_policy, dry_run=dry_run)


if __name__ == "__main__":
    main()
