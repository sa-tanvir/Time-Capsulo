# Era toolchain for Python repos (2017-2019): CPython 3.7, pytest 5.x
# Base image pinned by digest (checked on 2026-10-20 to be the exact base of the images used for all published results).
FROM python:3.7-slim@sha256:b53f496ca43e5af6994f8e316cf03af31050bf7944e0e4a308ad86c001cf028b
RUN pip install --no-cache-dir "pytest==5.3.5" "pytest-timeout==1.3.4"
WORKDIR /w
