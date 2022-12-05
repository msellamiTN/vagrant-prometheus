import datetime
import time
from collections import Counter
from dataclasses import dataclass

from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from .logging import logger

COLLECTION_TIME = Summary(
    "jenkins_collector_collect_seconds", "Time spent to collect metrics from Jenkins"
)


def calculate_total_duration(build_data):
    total_duration = 0
    for build in build_data:
        duration = build.get("duration")
        if duration == 0:
            duration = time.time() * 1000 - build.get("timestamp")

        total_duration += duration / 1000.0
    return total_duration


@dataclass
class Repository:
    name: str
    group: str


class JenkinsCollector(object):
    def __init__(self, jenkins_client, repositories):
        self._jenkins = jenkins_client
        self.repositories = repositories
        self._setup_empty_prometheus_metrics()

    def collect(self):

        # Request data from Jenkins

        for metric in self._prometheus_metrics.values():
            yield metric

    def update_metrics(self):
        logger.info("Collecting metrics")
        start = time.time()
        self._setup_empty_prometheus_metrics()
        for repository in self.repositories:
            try:
                logger.debug("Processing Job %s", repository.name)
                branches = self._jenkins.get_jobs(repository.name)
                for branch in branches:
                    job = f"{repository.name}/{branch}"
                    self._get_metrics(job, repository)
            except BaseException as e:
                logger.exception("Failed collecting metrics %s", e)
        duration = time.time() - start
        logger.info("Completed collecting metrics in %s s", duration)
        COLLECTION_TIME.observe(duration)

    def _request_data(self, name):
        job_name, branch = name.split("/", 2)
        logger.info("Requesting data from %s and branch %s", job_name, branch)

        def should_include_build(build):
            lookup_interval = datetime.timedelta(minutes=30)
            filter_lower_bound = datetime.datetime.now() - lookup_interval

            return (
                build["timestamp"] + build["duration"]
            ) > filter_lower_bound.timestamp() * 1000

        return self._jenkins.get_builds(
            job_name, branch, filter_func=should_include_build
        )

    def _setup_empty_prometheus_metrics(self):
        # The metrics we want to export.
        self._prometheus_metrics = {}

        self._prometheus_metrics = {
            "totalDurationMillis": GaugeMetricFamily(
                "jenkins_job_monitor_total_duration_seconds_sum",
                "Jenkins build total duration in millis",
                labels=["jobname", "group", "repository"],
            ),
            "failCount": GaugeMetricFamily(
                "jenkins_job_monitor_fail_count",
                "Jenkins build fail counts",
                labels=["jobname", "group", "repository"],
            ),
            "totalCount": GaugeMetricFamily(
                "jenkins_job_monitor_total_count",
                "Jenkins build total counts",
                labels=["jobname", "group", "repository"],
            ),
            "passCount": GaugeMetricFamily(
                "jenkins_job_monitor_pass_count",
                "Jenkins build pass counts",
                labels=["jobname", "group", "repository"],
            ),
            "pendingCount": GaugeMetricFamily(
                "jenkins_job_monitor_pending_count",
                "Jenkins build pending counts",
                labels=["jobname", "group", "repository"],
            ),
            "stage_duration": GaugeMetricFamily(
                "jenkins_job_monitor_stage_duration",
                "Jenkins build stage duration in ms",
                labels=["jobname", "group", "repository", "stagename", "build"],
            ),
            "stage_pass_count": CounterMetricFamily(
                "jenkins_job_monitor_stage_pass_count",
                "Jenkins build stage pass count",
                labels=["jobname", "group", "repository", "stagename"],
            ),
            "stage_pass_duration_sum": GaugeMetricFamily(
                "jenkins_job_monitor_stage_pass_duration_sum",
                "Jenkins build stage pass count",
                labels=["jobname", "group", "repository", "stagename"],
            ),
            "stage_fail_count": CounterMetricFamily(
                "jenkins_job_monitor_stage_fail_count",
                "Jenkins build stage fail count",
                labels=["jobname", "group", "repository", "stagename"],
            ),
            "stage_fail_duration_sum": GaugeMetricFamily(
                "jenkins_job_monitor_stage_fail_duration_sum",
                "Jenkins build stage pass count",
                labels=["jobname", "group", "repository", "stagename"],
            ),
        }

    def _get_metrics(self, name, repository):
        build_data = self._request_data(name) or {}
        self._add_data_to_prometheus_structure(build_data, name, repository)

    def _add_data_to_prometheus_structure(self, build_data, name, repository):
        aggregates = self.get_aggregate_data(build_data, name)

        for key, metric in aggregates.items():
            self._prometheus_metrics[key].add_metric(
                [name, repository.group, repository.name], metric
            )

        stages_wise_metrics = self.get_stages_data(build_data, name)

        for stage_name, stage_metrics in stages_wise_metrics.items():
            labels = [name, repository.group, repository.name, stage_name]

            self._prometheus_metrics["stage_pass_count"].add_metric(
                labels,
                stage_metrics["passed"],
            )
            self._prometheus_metrics["stage_pass_duration_sum"].add_metric(
                labels,
                stage_metrics["passed_duration_sum"],
            )
            self._prometheus_metrics["stage_fail_count"].add_metric(
                labels,
                stage_metrics["failed"],
            )
            self._prometheus_metrics["stage_fail_duration_sum"].add_metric(
                labels,
                stage_metrics["failed_duration_sum"],
            )

    def get_stages_data(self, build_data, name):
        stages_data = {}

        for build in build_data:
            if build["result"] in ["SUCCESS", "FAILED", "ABORTED"]:
                for stage in build["stages"]:
                    stage_name = stage["name"]
                    if stage_name not in stages_data:
                        stages_data[stage_name] = {
                            "passed_duration_sum": 0,
                            "failed_duration_sum": 0,
                            "failed": 0,
                            "passed": 0,
                        }

                    if stage["status"] == "SUCCESS":
                        logger.info(
                            "Recording SUCCESS for %s build #%s and stage %s",
                            name,
                            build["number"],
                            stage_name,
                        )
                        stages_data[stage_name]["passed"] += 1
                        stages_data[stage_name]["passed_duration_sum"] += stage[
                            "durationMillis"
                        ]

                    elif stage["status"] in ["FAILED", "ABORTED"]:
                        logger.info(
                            "Recording FAIL for %s build #%s and stage %s",
                            name,
                            build["number"],
                            stage_name,
                        )
                        stages_data[stage_name]["failed"] += 1
                        stages_data[stage_name]["failed_duration_sum"] += stage[
                            "durationMillis"
                        ]

        return stages_data

    def get_aggregate_data(self, build_data, name):
        finished = len(list(filter(lambda x: x["duration"] != 0, build_data)))
        pending = len(list(filter(lambda x: x["duration"] == 0, build_data)))
        successful = len(list(filter(lambda x: x["result"] == "SUCCESS", build_data)))
        failed = len(
            list(filter(lambda x: x["result"] in ["FAILURE", "ABORTED"], build_data))
        )
        total_duration = calculate_total_duration(build_data)

        logger.info(
            "For job %s recorded %s finished %s pending %s successful %s failed",
            name,
            finished,
            pending,
            successful,
            failed,
        )

        return {
            "passCount": successful,
            "failCount": failed,
            "pendingCount": pending,
            "totalCount": finished,
            "totalDurationMillis": total_duration,
        }
