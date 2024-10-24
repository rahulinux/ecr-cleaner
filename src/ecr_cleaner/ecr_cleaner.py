"""
ECR Cleaner
====

A module for managing Amazon ECR (Elastic Container Registry) lifecycles.

Functions:

Classes:
    Repository
"""

import boto3
import json
import pytz

from typing import List, Dict, TypedDict, Optional
from collections import defaultdict
from botocore.exceptions import ClientError

from .helpers import get_logger

log = get_logger()

UNTAGGED = "untagged"
IMAGE_DIGEST = "imageDigest"
IMAGE_PUSHED_AT = "imagePushedAt"
IMAGE_TAGS = "imageTags"


class ImageDetail(TypedDict):
    imageDigest: str
    imagePushedAt: str
    imageTags: Optional[List[str]]


class Images(TypedDict):
    tagged: Dict[str, List[ImageDetail]]
    untagged: List[ImageDetail]


class Repository:
    def __init__(self, name: str, region: str, batch_size: int = 100) -> None:
        self.name = name
        self.region = region
        self.batch_size = batch_size
        if not self.region:
            log.warn("Region is not set, skipping ECR client initialization")
            self.ecr_client = None
        else:
            self.ecr_client = boto3.client("ecr", region_name=self.region)

    def _get_images(self, tag_prefix_list: List[str]) -> Images:
        """
        Retrieve images categorized into tagged and untagged
        images in sorted by published date.

        Args:
            tag_prefix_list: List of tag prefixes to categorize images

        Returns:
            Images object containing tagged and untagged images
        """
        all_images = self._fetch_all_images()
        log.info("Image count", total_images=len(all_images), repository=self.name)

        all_images.sort(
            key=lambda image: image[IMAGE_PUSHED_AT].astimezone(pytz.UTC), reverse=True
        )

        images_by_tag = self._categorize_images(all_images, tag_prefix_list)
        untagged_images = [img for img in all_images if IMAGE_TAGS not in img]

        self._standardize_timestamps(images_by_tag, untagged_images)

        return Images(tagged=images_by_tag, untagged=untagged_images)

    def _fetch_all_images(self) -> List[ImageDetail]:
        """Fetch all images from the repository using pagination."""
        all_images = []
        next_token = None
        if not (self.name and self.region):
            return all_images
        while True:
            try:
                images = self.ecr_client.describe_images(
                    repositoryName=self.name,
                    **({"nextToken": next_token} if next_token else {}),
                )
                all_images.extend(images.get("imageDetails", []))
                next_token = images.get("nextToken")
                if not next_token:
                    break
            except ClientError as e:
                log.error(f"Error fetching images: {e}")
                break
        return all_images

    def _categorize_images(
        self, all_images: List[ImageDetail], tag_prefix_list: List[str]
    ) -> Dict[str, List[ImageDetail]]:
        """Categorize images based on their tags and prefixes."""
        images_by_tag = defaultdict(list)

        for image in all_images:
            if IMAGE_TAGS not in image:
                continue

            for tag in image[IMAGE_TAGS]:
                if tag not in images_by_tag:
                    images_by_tag[tag] = []
                else:
                    images_by_tag[tag].append(image)

                for prefix in tag_prefix_list:
                    if prefix != UNTAGGED and tag.startswith(prefix):
                        images_by_tag[prefix].append(image)

        return dict(images_by_tag)

    def _standardize_timestamps(
        self,
        images_by_tag: Dict[str, List[ImageDetail]],
        untagged_images: List[ImageDetail],
    ) -> None:
        """Convert imagePushedAt to ISO format string for consistency."""
        for images in list(images_by_tag.values()) + [untagged_images]:
            for image in images:
                if not isinstance(image[IMAGE_PUSHED_AT], str):
                    image[IMAGE_PUSHED_AT] = image[IMAGE_PUSHED_AT].isoformat()

    def manage_images(self, policy: Dict[str, int], dry_run: bool = True) -> None:
        """Manage images according to defined policies."""
        images = self._get_images(list(policy.keys()))
        tagged_images = images["tagged"]
        untagged_images = images["untagged"]

        for tag, keep_count in policy.items():
            if tag != UNTAGGED:
                self._manage_tagged_images(tag, keep_count, tagged_images, dry_run)

        self._manage_untagged_images(policy.get(UNTAGGED, 0), untagged_images, dry_run)

    def _manage_tagged_images(
        self,
        tag: str,
        keep_count: int,
        tagged_images: Dict[str, List[ImageDetail]],
        dry_run: bool,
    ) -> None:
        """Manage tagged images based on the policy."""
        if tag not in tagged_images:
            return

        total_tagged_images = len(tagged_images[tag])
        delete_count = max(0, total_tagged_images - keep_count)

        if delete_count <= 0:
            log.warn("Invalid policy, Skipping tag", tag=tag, repository=self.name)
            log.warn(
                "Keep most recent count should be greater than 0",
                tag=tag,
                repository=self.name,
                keep_count=keep_count,
            )
        else:
            images_to_delete = tagged_images[tag][-delete_count:]

            log.info(
                "Total images to delete with tag",
                tag=tag,
                delete_count=delete_count,
                repository=self.name,
                keep_count=keep_count,
                total=total_tagged_images,
            )

            self._delete_images(images_to_delete, dry_run)

    def _manage_untagged_images(
        self, keep_count: int, untagged_images: List[ImageDetail], dry_run: bool
    ) -> None:
        """Manage untagged images based on the policy."""
        total_untagged_images = len(untagged_images)
        delete_count = max(0, total_untagged_images - keep_count)
        images_to_delete = untagged_images[-delete_count:]

        log.info(
            "Total images to delete with untagged:",
            delete_count=delete_count,
            total=total_untagged_images,
            keep_count=keep_count,
            repository=self.name,
        )

        if images_to_delete:
            self._log_untagged_deletion_details(images_to_delete)

        self._delete_images(images_to_delete, dry_run)

    def _delete_images(self, images: List[ImageDetail], dry_run: bool) -> None:
        """Delete the specified images in batches."""
        if not images:
            return

        for i in range(0, len(images), self.batch_size):
            batch = images[i : i + self.batch_size]  # Get the current batch
            image_ids = [
                {"imageDigest": img[IMAGE_DIGEST]}
                for img in batch
                if "imageDigest" in img
            ]

            if dry_run:
                log.info(
                    "Dry-run: Skip deletion of the following images:",
                    image_ids=image_ids,
                )
            else:
                try:
                    self.ecr_client.batch_delete_image(
                        repositoryName=self.name,
                        imageIds=image_ids,
                    )
                    log.info(
                        f"Deleted {len(image_ids)} images.",
                        deleted_image_ids=image_ids,
                    )
                except ClientError as e:
                    log.error(f"Failed to delete images: {e}")

    def _log_untagged_deletion_details(
        self, images_to_delete: List[ImageDetail]
    ) -> None:
        """Log details of untagged images to be deleted."""
        log.debug(
            "First image id and publish date from untagged images:",
            first=json.dumps(
                {
                    IMAGE_DIGEST: images_to_delete[0][IMAGE_DIGEST],
                    IMAGE_PUSHED_AT: images_to_delete[0][IMAGE_PUSHED_AT],
                },
                indent=4,
            ),
        )
        if len(images_to_delete) > 1:
            log.debug(
                "Last image id and publish date from untagged images:",
                last=json.dumps(
                    {
                        IMAGE_DIGEST: images_to_delete[-1][IMAGE_DIGEST],
                        IMAGE_PUSHED_AT: images_to_delete[-1][IMAGE_PUSHED_AT],
                    },
                    indent=4,
                ),
            )
