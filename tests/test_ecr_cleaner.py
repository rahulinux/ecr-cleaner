import argparse
import boto3
import hashlib
import json
import pytz
import random
import unittest
import uuid
from freezegun import freeze_time
from moto import mock_aws
from unittest import mock

from ecr_cleaner import Repository
from ecr_cleaner.helpers import config_logger
from ecr_cleaner_cli import RepositoryConfig, parse_args

config_logger("DEBUG")


class TestECRCleaner(unittest.TestCase):
    REPOSITORY_NAME = f"test-image-{uuid.uuid4()}"
    REGION = "us-east-1"
    BATCH_SIZE = 1

    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()

        boto3.setup_default_session(region_name=self.REGION)
        self.ecr_client = boto3.client("ecr", region_name=self.REGION)
        self.ecr_client.create_repository(repositoryName=self.REPOSITORY_NAME)

        self._populate_repository()

    def _create_image_digest(self):
        contents = str(random.SystemRandom().randint(0, 10**6))
        return "sha256:%s" % hashlib.sha256(contents.encode("utf-8")).hexdigest()

    def _put_images(self, images):
        for image in images:
            image_tags = image.get("imageTags", [])
            image_digest = self._create_image_digest()
            data = {
                "repositoryName": self.REPOSITORY_NAME,
                "imageManifest": json.dumps(image),
                "imageTag": image_tags[0] if image_tags else None,
                "imageDigest": image_digest,
            }
            if not image_tags:
                del data["imageTag"]

            if "imagePushedAt" in image:
                with freeze_time(image["imagePushedAt"]):
                    self.ecr_client.put_image(**data)
            else:
                self.ecr_client.put_image(**data)

    def _populate_repository(self):
        """Populate the mock ECR repository with images."""
        common_image_manifest = {
            "schemaVersion": 2,
            "mock": "manifest",
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "repositoryName": self.REPOSITORY_NAME,
        }

        with open("tests/images.json") as f:
            image_details = json.load(f)

        images = [{**common_image_manifest, **image} for image in image_details]
        self._put_images(images)

    def test_ecr_cleaner_management(self):
        """Test the ECR Cleaner functionality."""
        images = self.ecr_client.describe_images(repositoryName=self.REPOSITORY_NAME)

        total_images = len(images["imageDetails"])

        other_images = len(
            [
                img
                for img in images["imageDetails"]
                for tag in img.get("imageTags", [])
                if tag.startswith("other-")
            ]
        )

        policy = {
            "beta": 2,  # total 4
            "untagged": 2,  # total 5
            "latest": 1,  # total 1
        }
        repo = Repository(
            name=self.REPOSITORY_NAME, batch_size=self.BATCH_SIZE, region=self.REGION
        )

        # Apply dry run to ensure no images are deleted
        repo.manage_images(policy=policy, dry_run=True)
        self.assertEqual(len(images["imageDetails"]), total_images)

        # Apply policy to delete images
        repo.manage_images(policy=policy, dry_run=False)

        images_with_applied_policy = self.ecr_client.describe_images(
            repositoryName=self.REPOSITORY_NAME
        )

        # Calculate expected remaining images
        expected_remaining_images = (
            policy["beta"] + policy["untagged"] + policy["latest"] + other_images
        )

        self.assertEqual(
            expected_remaining_images,
            len(images_with_applied_policy["imageDetails"]),
            "The repository does not have the expected number of images after management.",
        )

        latest_images = [
            img
            for img in images_with_applied_policy["imageDetails"]
            for tag in img.get("imageTags", [])
            if tag.startswith("latest")
        ]
        self.assertEqual(
            len(latest_images), policy["latest"], "Latest image count mismatch."
        )

        untagged_images_after = [
            img
            for img in images_with_applied_policy["imageDetails"]
            if not img.get("imageTags")
        ]

        self.assertEqual(
            policy["untagged"],
            len(untagged_images_after),
            "Untagged image count mismatch.",
        )

        untagged_image_dates_before = [
            image.get("imagePushedAt")
            for image in images["imageDetails"]
            if "imageTags" not in image
        ]
        untagged_image_dates_before.sort(
            key=lambda x: x.astimezone(pytz.UTC), reverse=True
        )

        untagged_image_dates_after = [
            image.get("imagePushedAt")
            for image in images_with_applied_policy["imageDetails"]
            if "imageTags" not in image
        ]
        untagged_image_dates_after.sort(
            key=lambda x: x.astimezone(pytz.UTC), reverse=True
        )

        self.assertEqual(
            untagged_image_dates_before[: policy.get("untagged")],
            untagged_image_dates_after,
            "Images are not deleted by date in ascending order.",
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
