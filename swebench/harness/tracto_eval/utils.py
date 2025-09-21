import urllib.parse
import logging

import yt.wrapper as yt


def get_tracto_registry_url() -> str:
    tracto_url = urllib.parse.urlparse(yt.config["proxy"]["url"]).netloc
    return f"cr.{tracto_url}"


def logging_basic_config(level: int = logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
