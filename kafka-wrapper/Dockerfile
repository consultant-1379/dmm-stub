ARG CBOS_VERSION
FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os_release/sles:${CBOS_VERSION}
ARG CBOS_VERSION
ARG CBO_REPO_URL=https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/${CBOS_VERSION}
ARG PB_REL="https://github.com/protocolbuffers/protobuf/releases"
ARG BUILD_DATE
ARG APP_VERSION
LABEL \
    org.opencontainers.image.title=eric-oss-kafka-wrapper \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.vendor=Ericsson \
    org.opencontainers.image.version=$APP_VERSION
RUN zypper ar -C -G -f $CBO_REPO_URL?ssl_verify=no \
    COMMON_BASE_OS_SLES_REPO \
    && zypper install -l -y python311 \
    && zypper install -l -y python311-pip \
    && zypper install -l -y curl \
    && zypper install -l -y jq \
    && zypper install -l -y nodejs npm \
    && zypper install -l -y libprotobuf-lite20 \
    && zypper install -l -y unzip \
    && zypper clean --all \
    && zypper rr COMMON_BASE_OS_SLES_REPO
RUN curl -LO $PB_REL/download/v25.3/protoc-25.3-linux-x86_64.zip
RUN unzip protoc-25.3-linux-x86_64.zip -d /opt/protoc
ENV PATH="$PATH:/opt/protoc/bin"
COPY kafka-wrapper/requirement.txt .
COPY kafka-wrapper/src /kafka-wrapper
RUN pip3.11 install -r requirement.txt
ARG USER_ID=40514
ARG USER_NAME="eric-oss-dmm"
USER $USER_ID
WORKDIR /kafka-wrapper
# ENTRYPOINT ["python3", "/kafka-wrapper/app.py"]


# # Use an official Python base image
# FROM python:3.9.1

# # Install Node.js and npm (Node.js package manager)
# RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - \
#     && apt-get install -y nodejs npm

# # Create a working directory for your application

# WORKDIR /kafka-wrapper
# COPY src /kafka-wrapper

# # Copy and install Python dependencies (requirements.txt)
# COPY requirement.txt .
# RUN pip install --no-cache-dir -r requirement.txt

# Copy and install Node.js dependencies (package.json and package-lock.json)
# COPY package*.json ./
# RUN npm install
# # ENTRYPOINT ["python3", "/kafka-wrapper/app.py"]
