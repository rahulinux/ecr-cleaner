import argparse
import json
import unittest
from unittest import mock
import boto3
from moto import mock_aws
from ecr_lifecycle import Repository
from ecr_lifecycle_cli.ecr_lifecycle_cli import parse_args, RepositoryConfig


class TestECRLifecycle(unittest.TestCase):
    REPOSITORY_NAME = "test-image"
    REGION = "us-east-1"
    BATCH_SIZE = 1

    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()

        boto3.setup_default_session(region_name=self.REGION)
        self.ecr_client = boto3.client("ecr", region_name=self.REGION)
        self.ecr_client.create_repository(repositoryName=self.REPOSITORY_NAME)

        self._populate_repository()

    def _populate_repository(self):
        """Populate the mock ECR repository with images."""
        common_image_manifest = {
            "schemaVersion": 2,
            "mock": "manifest",
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        }

        image_details = [
            {"imageTags": ["latest"]},
            {"imageTags": ["stable"]},
            {
                "imageTags": [],
                "imageDigest": "sha256:4fc82b26aecb47d2868c4efbe3581732a3e7cbcc6c2efb32062c08170a05eeb8",
            },
            {
                "imageTags": [],
                "imageDigest": "sha256:73475cb40a568e8da8a045ced110137e159f890ac4da883b6b17dc651b3a8049",
            },
            {"imageTags": []},
        ]

        for image in image_details:
            manifest = {**common_image_manifest, **image}
            image_tags = image.get("imageTags", [])
            image_digest = image.get("imageDigest", "")

            if image_tags:
                self.ecr_client.put_image(
                    repositoryName=self.REPOSITORY_NAME,
                    imageManifest=json.dumps(manifest),
                    imageTag=image_tags[0],
                    imageDigest=image_digest,
                )
            else:
                self.ecr_client.put_image(
                    repositoryName=self.REPOSITORY_NAME,
                    imageManifest=json.dumps(manifest),
                    imageDigest=image_digest,
                )

    def test_ecr_lifecycle_management(self):
        """Test the ECR lifecycle management functionality."""
        policy = {"latest": 1, "untagged": 2}
        repo = Repository(
            name=self.REPOSITORY_NAME, batch_size=self.BATCH_SIZE, region=self.REGION
        )

        repo.manage_images(policy=policy, dry_run=False)

        images = self.ecr_client.describe_images(repositoryName=self.REPOSITORY_NAME)

        # Check expected number of images after management
        expected_image_count = (
            4  # 1 latest + 1 stable + 3 untagged - 1 deleted untagged
        )
        self.assertEqual(len(images["imageDetails"]), expected_image_count)

        latest_images = [
            img
            for img in images["imageDetails"]
            if "latest" in img.get("imageTags", [])
        ]
        self.assertEqual(
            len(latest_images), policy["latest"], "Latest image count mismatch."
        )

        stable_images = [
            img
            for img in images["imageDetails"]
            if "stable" in img.get("imageTags", [])
        ]
        self.assertEqual(len(stable_images), 1, "Stable image count mismatch.")

        untagged_images = [
            img for img in images["imageDetails"] if not img.get("imageTags")
        ]
        self.assertEqual(
            len(untagged_images), policy["untagged"], "Untagged image count mismatch."
        )

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            repositories=[
                "test-image-backend:latest=1",
                "test-image-frontend:stable=1,untagged=11",
            ],
            region="us-east-1",
            dry_run=False,
            debug=True,
            config_file=None,
            batch_size=11,
        ),
    )
    def test_parse_arguments(self, mock_args):
        """Test the argument parsing functionality."""
        actual = parse_args()

        expected = (
            [
                RepositoryConfig(
                    name="test-image-backend", policy={"latest": 1, "untagged": 0}
                ),
                RepositoryConfig(
                    name="test-image-frontend", policy={"stable": 1, "untagged": 11}
                ),
            ],
            "us-east-1",
            11,
            False,
        )

        self.assertEqual(actual, expected)

    def tearDown(self):
        self.mock_aws.stop()


if __name__ == "__main__":
    unittest.main()
