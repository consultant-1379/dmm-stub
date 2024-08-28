#
# COPYRIGHT Ericsson 2021
#
#
#
# The copyright to the computer program(s) herein is the property of
#
# Ericsson Inc. The programs may be used and/or copied only with written
#
# permission from Ericsson Inc. or in accordance with the terms and
#
# conditions stipulated in the agreement/contract under which the
#
# program(s) have been supplied.
#
ARG CBOS_VERSION
FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os_release/sles:${CBOS_VERSION}
ARG CBOS_VERSION
ARG CBO_REPO_URL=https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/${CBOS_VERSION}
ARG JAR_FILE
ARG BUILD_DATE
ARG APP_VERSION
LABEL \
    org.opencontainers.image.title=eric-oss-dmm-stub \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.vendor=Ericsson \
    org.opencontainers.image.version=$APP_VERSION 
RUN zypper ar -C -G -f $CBO_REPO_URL?ssl_verify=no \
    COMMON_BASE_OS_SLES_REPO \
    && zypper install -l -y java-17-openjdk-headless \
    && zypper install -l -y curl \
    && zypper install -l -y jq \
    && zypper clean --all \
    && zypper rr COMMON_BASE_OS_SLES_REPO
ARG USER_ID=40514
ARG USER_NAME="eric-oss-dmm"
ADD target/${JAR_FILE} kafka-wrapper-java.jar
RUN echo "$USER_ID:x:$USER_ID:0:An Identity for $USER_NAME:/nonexistent:/bin/false" >>/etc/passwd
RUN echo "$USER_ID:!::0:::::" >>/etc/shadow
USER $USER_ID
# CMD ["/bin/sleep", "3650d"]
CMD java -jar kafka-wrapper-java.jar
