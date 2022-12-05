#!/usr/bin/python

import argparse
import logging
import os
import time

import yaml
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from jenkins_exporter.logging import DEBUG, logger
from .client import JenkinsClient
from .collector import JenkinsCollector, Repository


def parse_args():
    parser = argparse.ArgumentParser(
        description="jenkins exporter args jenkins address and port"
    )
    parser.add_argument(
        "-j",
        "--jenkins",
        metavar="jenkins",
        required=False,
        help="server url from the jenkins api",
        default=os.environ.get("JENKINS_SERVER", "http://jenkins:8080"),
    )
    parser.add_argument(
        "--user",
        metavar="user",
        required=False,
        help="jenkins api user",
        default=os.environ.get("JENKINS_USER"),
    )
    parser.add_argument(
        "--password",
        metavar="password",
        required=False,
        help="jenkins api password",
        default=os.environ.get("JENKINS_PASSWORD"),
    )
    parser.add_argument(
        "-p",
        "--port",
        metavar="port",
        required=False,
        type=int,
        help="Listen to this port",
        default=int(os.environ.get("VIRTUAL_PORT", "9118")),
    )
    parser.add_argument(
        "-k",
        "--insecure",
        dest="insecure",
        required=False,
        action="store_true",
        help="Allow connection to insecure Jenkins API",
        default=False,
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.WARNING)

    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    args = parse_args()
    port = int(args.port)
    jenkins_base_url = args.jenkins.rstrip("/")
    with open("config.yml") as config_file:
        config = yaml.safe_load(config_file)

    repositories = [
        Repository(name=repo, group=repo_config["team"])
        for repo, repo_config in config["jobs"].items()
    ]

    jenkins_client = JenkinsClient(
        jenkins_base_url, args.user, args.password, args.insecure
    )
    logger.info("Polling %s", args.jenkins)
    collector = JenkinsCollector(jenkins_client, repositories)
    REGISTRY.register(collector)

    start_http_server(port)
    logger.info("Serving at  port: %s", port)
    while True:
        collector.update_metrics()
        time.sleep(60)


if __name__ == "__main__":
    main()
