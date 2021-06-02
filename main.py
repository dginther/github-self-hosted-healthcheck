from flask import Flask
from healthcheck import HealthCheck, EnvironmentDump
import psutil
import os
import json
from ghapi.all import *
from fastcore.utils import *
from urllib.parse import urlparse

app = Flask(__name__)

health = HealthCheck()
envdump = EnvironmentDump(include_os=False,
                          include_python=False,
                          include_process=False)
api = GhApi()


def get_proc_info():
    procs = psutil.process_iter(['pid', 'name', 'username'])

    for proc in procs:
        if proc['name'] == 'Runner.Listener':
            print(proc.info)


def runner_available():
    for proc in psutil.process_iter():
        try:
            if 'runner.listener' in proc.name().lower():
                return True, "runner ok"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False, "runner not ok"


def runner_registered():
    with open(os.environ.get('RUNNER_HOME') + "/.runner", encoding='utf-8-sig') as f:
        runner_info = json.load(f)
        parsed = urlparse(runner_info['gitHubUrl'])
        org = os.path.split(parsed.path)[0].strip("/")
        repo = os.path.split(parsed.path)[1]
        runners = obj2dict(
            api.actions.list_self_hosted_runners_for_repo(org, repo))

        for runner in runners['runners']:
            if runner['name'] == runner_info['agentName']:
                if runner['status'] == "offline":
                    return False, "runner offline"
                else:
                    return True, "runner online"
            else:
                pass


health.add_check(runner_available)
health.add_check(runner_registered)


def application_data():
    with open("/home/runner/.runner", encoding='utf-8-sig') as f:
        runner_info = json.load(f)

    return {"maintainer": "Operations",
            "application": "Github Self Hosted Runner",
            "agentId": runner_info['agentId'],
            "agentName": runner_info['agentName'],
            "poolId": runner_info['poolId'],
            "poolName": runner_info['poolName'],
            "serverUrl": runner_info['serverUrl'],
            "gitHubUrl": runner_info['gitHubUrl'],
            "workFolder": runner_info['workFolder']
            }


envdump.add_section("application", application_data)

app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
app.add_url_rule("/info", "environment",
                 view_func=lambda: envdump.run())
