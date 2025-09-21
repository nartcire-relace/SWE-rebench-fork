"""
This is a script to copy images to Tracto registry via skopeo.

The script is executed on Tracto as a map job:
- stdin = JSON lines from the source table
- stdout = JSON lines to the output table

By design, this is a standalone script without any 3rd party or swebench
dependencies, which helps to avoid pickling issues and exemplifies
how the map jobs work on Tracto w/o sugar.
"""

import logging
import sys
import json
import subprocess
import os

logger = logging.getLogger(__name__)


def run_command(cmd: list[str]) -> None:
    subprocess.run(
        cmd,
        stdout=sys.stderr,
        stderr=sys.stderr,
        check=True,
    )


def process_row(input_row: dict) -> dict:
    instance_id = input_row["instance_id"]
    instance_image_key = input_row["instance_image_key"]
    tracto_instance_image_key = input_row["tracto_instance_image_key"]

    logger.info(
        f"Copying image for instance {instance_id}: "
        f"{instance_image_key} -> {tracto_instance_image_key}"
    )

    success = None
    try:
        run_command(
            [
                "skopeo",
                "--tmpdir",
                "/slot/sandbox/tmpfs/skopeo",
                "copy",
                "--retry-times",
                "3",
                f"docker://{instance_image_key}",
                f"docker://{tracto_instance_image_key}",
            ]
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to copy image for instance {instance_id}: {e}")
        success = False
    else:
        success = True

    return {
        "instance_id": instance_id,
        "instance_image_key": instance_image_key,
        "tracto_instance_image_key": tracto_instance_image_key,
        "success": success,
    }


def main():
    tracto_registry_username = os.environ["YT_SECURE_VAULT_TRACTO_REGISTRY_USERNAME"]
    tracto_registry_password = os.environ["YT_SECURE_VAULT_TRACTO_REGISTRY_PASSWORD"]
    tracto_registry_url = os.environ["TRACTO_REGISTRY_URL"]

    run_command(
        [
            "skopeo",
            "login",
            "--username",
            tracto_registry_username,
            "--password",
            tracto_registry_password,
            tracto_registry_url,
        ]
    )

    for json_line in sys.stdin:
        input_row = json.loads(json_line)
        output_row = process_row(input_row)
        json.dump(output_row, sys.stdout)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    main()
