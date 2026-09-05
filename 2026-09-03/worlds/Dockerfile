# One world per fresh issue: the repo cloned at the closing PR's base commit,
# test deps installed, laid out like the SWE-bench images the ch07 harness
# expects (/testbed, and an activate shim at /opt/miniconda3/bin/activate so
# the harness's `source /opt/miniconda3/bin/activate testbed` keeps working).
# Network is available only at build time; the runner starts the container
# with --network none and seals git to the base commit.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv && mkdir -p /opt/miniconda3/bin \
    && printf 'source /opt/venv/bin/activate\n' > /opt/miniconda3/bin/activate \
    && /opt/venv/bin/pip install -q --upgrade pip
ENV PATH=/opt/venv/bin:$PATH
ARG REPO
RUN git clone -q https://github.com/${REPO} /testbed
WORKDIR /testbed
ARG SHA
RUN git checkout -q ${SHA}
ARG INSTALL
RUN bash -c "${INSTALL}"
