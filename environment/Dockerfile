# hash:sha256:47c1e6f4faac00ec835df774725e18aac1779540a5ddbb6a38647cbd14467718
FROM registry.apps.codeocean.com/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN mamba install -y \
        pandas==1.5.3 \
        requests==2.28.2 \
    && mamba clean -ya

RUN pip install -U --no-cache-dir \
    databricks-sql-connector==2.7.0

COPY postInstall /
RUN /postInstall
