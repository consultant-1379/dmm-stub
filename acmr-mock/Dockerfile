ARG CBOS_VERSION
FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os_release/sles:${CBOS_VERSION}
ARG CBOS_VERSION
ARG CBO_REPO_URL=https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/${CBOS_VERSION}
ARG BUILD_DATE
ARG APP_VERSION
LABEL \
    org.opencontainers.image.title=eric-oss-acmr-mock \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.vendor=Ericsson \
    org.opencontainers.image.version=$APP_VERSION
RUN zypper ar -C -G -f $CBO_REPO_URL?ssl_verify=no \
    COMMON_BASE_OS_SLES_REPO \
    && zypper install -l -y python311 \
    && zypper install -l -y python311-pip \
    && zypper install -l -y curl \
    && zypper install -l -y jq \
    && zypper install -l -y unzip \
    && zypper clean --all \
    && zypper rr COMMON_BASE_OS_SLES_REPO
COPY acmr-mock/requirement.txt .
COPY acmr-mock/src /acmr-mock
RUN pip3.11 install -r requirement.txt
ARG USER_ID=40514
ARG USER_NAME="eric-oss-dmm"
USER $USER_ID
WORKDIR /acmr-mock
