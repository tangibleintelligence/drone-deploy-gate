FROM python:3.9

# copy in script
COPY ./check_deploy_valid.py /opt/check_deploy_valid.py

# Use bash by default, not python, and should run defining vars and publishing/building with poetry
CMD python /opt/check_deploy_valid.py