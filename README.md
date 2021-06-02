Github Self-Hosted Runner Healthcheck
based on py-healthcheck (https://pypi.org/project/py-healthcheck/)

Getting Started:  
- Install requirements: `pip install -r requirements.txt`
- Run gunicorn: `gunicorn main:app`

You may now query  
http://localhost:8000/healthcheck  
http://localhost:8000/info  



Required env vars:  

GITHUB_TOKEN=`<PAT>`  
RUNNER_HOME=`<runner home dir>`  
