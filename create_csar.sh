TMP_VOLUME=$1
ENV_PATH=$2 
docker run --init --rm \
  --volume ${TMP_VOLUME}:${TMP_VOLUME}:rw \
  --workdir /target \
  --volume ${ENV_PATH}:/target:rw \
  armdocker.rnd.ericsson.se/proj-eric-oss-dev-test/releases/eric-oss-app-package-tool:latest \
  generate --tosca /target/Metadata/tosca.meta \
  --name rapp-simulation \
  --images ${TMP_VOLUME}/docker.tar \
  --helm3 \
  --output ${ENV_PATH}