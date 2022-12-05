import time
from dataclasses import dataclass

import requests

from .logging import logger


class JenkinsClient:
    def __init__(self, jenkins_base_url, username=None, password=None, insecure=False):
        self._insecure = insecure
        self._password = password
        self._username = username
        self._jenkins_base_url = jenkins_base_url

    def get_jobs(self, parent):
        logger.info("Getting jobs for %s", parent)
        url_job = f"job/{parent}/api/json?tree=jobs[name]"
        params = {"tree": "jobs[name]"}
        response = self._make_request(url_job, params)
        return [job["name"] for job in response["jobs"]]

    def get_builds(self, job_name, branch, filter_func=None):
        logger.info("Getting build for %s and branch %s", job_name, branch)
        start = time.perf_counter()
        url = f"job/{job_name}/job/{branch}/api/json"
        params = {"tree": "builds[number,duration,result,timestamp]"}

        job_info = self._make_request(url, params)

        builds = (
            job_info["builds"]
            if filter is None
            else list(filter(filter_func, job_info["builds"]))
        )

        for build in builds:
            build_info = self.__get_build_info(job_name, branch, build["number"])

            # Populate stages data
            build["stages"] = build_info["stages"]

        duration = time.perf_counter() - start
        logger.info("Fetched build info in %s", duration)
        return builds

    def _make_request(self, url_fragment, params=None):
        if params is None:
            params = {}
        start = time.perf_counter()
        url = f"{self._jenkins_base_url}/{url_fragment}"
        logger.debug("Making request to url %s", url)

        has_auth_credentials = self._username and self._password

        if has_auth_credentials:
            response = requests.get(
                url,
                params=params,
                auth=(self._username, self._password),
                verify=(not self._insecure),
            )
        else:
            response = requests.get(url, params=params, verify=(not self._insecure))

        stop = time.perf_counter()
        logger.debug("Completed request in %s", stop - start)

        if response.status_code != 200:
            raise Exception(
                f"Call to url {url} failed with status: {response.status_code}"
            )

        return response.json()

    def __get_build_info(self, job_name, branch, build_number):
        url = f"job/{job_name}/job/{branch}/{build_number}/wfapi/describe"
        return self._make_request(url)
