#!/usr/bin/env groovy
def defaultBobImage = 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob.2.0:1.7.0-55'
def bob = new BobCommand()
    .bobImage(defaultBobImage)
    .envVars([
        HOME:'${HOME}',
        RELEASE:'${RELEASE}',
        GERRIT_CHANGE_NUMBER:'${GERRIT_CHANGE_NUMBER}',
        KUBECONFIG:'${KUBECONFIG}',
        K8S_NAMESPACE: '${K8S_NAMESPACE}',
        USER:'${USER}',
        SELI_ARTIFACTORY_REPO_USER:'${CREDENTIALS_SELI_ARTIFACTORY_USR}',
        SELI_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SELI_ARTIFACTORY_PSW}',
        SERO_ARTIFACTORY_REPO_USER:'${CREDENTIALS_SERO_ARTIFACTORY_USR}',
        SERO_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SERO_ARTIFACTORY_PSW}',
        GERRIT_CHANGE_URL: '${GERRIT_CHANGE_URL}'
    ])
    .needDockerSocket(true)
    .toString()
def LOCKABLE_RESOURCE_LABEL = "kaas"
pipeline {
    agent {
        node {
            label NODE_LABEL
        }
    }
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '50', artifactNumToKeepStr: '50'))
    }
    environment {
        RELEASE = "true"
        TEAM_NAME = "TeamMiddlemen"
        KUBECONFIG = "${WORKSPACE}/.kube/config"
        CREDENTIALS_SELI_ARTIFACTORY = credentials('SELI_ARTIFACTORY')
        CREDENTIALS_SERO_ARTIFACTORY = credentials('SERO_ARTIFACTORY')
    }
    // Stage names (with descriptions) taken from ADP Microservice CI Pipeline Step Naming Guideline: https://confluence.lmera.ericsson.se/pages/viewpage.action?pageId=122564754
    stages {
        stage('Prepare') {
            steps {
                checkout([$class: 'GitSCM',
                          branches: [
                                  [name: "${GERRIT_PATCHSET_REVISION}"]
                          ],
                          extensions: [
                                  [$class: 'SubmoduleOption',
                                   disableSubmodules: false,
                                   parentCredentials: true,
                                   recursiveSubmodules: true,
                                   reference: '',
                                   trackingSubmodules: false],
                                  [$class: 'CleanBeforeCheckout']
                          ],
                          userRemoteConfigs: [
                                  [url: '${GERRIT_MIRROR}/OSS/com.ericsson.oss.dmi/eric-oss-data-catalog']
                          ]
                ])
                /* End of generated snippet */
                sh "${bob} --help"
                script {
                    env.KAFKA_WRAPPER = false
                    env.RAPP_SIMULATION = false

                }
            }
        }
        stage('Clean') {
            steps {
                echo 'Inject settings.xml into workspace:'
                configFileProvider([configFile(fileId: "${env.SETTINGS_CONFIG_FILE_NAME}", targetLocation: "${env.WORKSPACE}")]) {}
                archiveArtifacts allowEmptyArchive: true, artifacts: 'ruleset2.0.yaml, precodereview.Jenkinsfile'
                sh "${bob} clean"
            }
        }
        stage('Kafka wrapper Init') {
            steps {
                sh "${bob} init-drop"
                script {
                    env.KAFKA_WRAPPER = true
                    echo "Value of KAFKA_WRAPPER: ${env.KAFKA_WRAPPER}"
                    authorName = sh(returnStdout: true, script: 'git show -s --pretty=%an')
                    currentBuild.displayName = currentBuild.displayName + ' / ' + authorName
                }
            }
        }
        stage('Rapp Simulation Init') {
            steps {
                sh "${bob} init-drop -r python-ruleset2.0.yaml"
                script {
                    env.RAPP_SIMULATION = true
                    echo "Value of RAPP_SIMULATION: ${env.RAPP_SIMULATION}"
                    authorName = sh(returnStdout: true, script: 'git show -s --pretty=%an')
                    currentBuild.displayName = currentBuild.displayName + ' / ' + authorName
                }
            }
        }
        stage('Kafka Wrapper Image') {
            steps {
                sh "${bob} image"
            }
        }
        stage('Rapp Simulation Image') {
            steps {
                sh "${bob} image -r python-ruleset2.0.yaml"
            }
        }
        stage('Kafka Wrapper Publish') {
            steps {
                script {
                    sh "${bob} publish"
                }
            }
        }
        stage('Rapp Simulation Publish') {
            steps {
                script {
                    sh "${bob} publish -r python-ruleset2.0.yaml"
                }
            }
        }
}
    post {
        success {
            script {
                echo "Value outside of KAFKA_WRAPPER: ${env.KAFKA_WRAPPER}"
                echo "Value of outside RAPP_SIMULATION: ${env.RAPP_SIMULATION}"
                if( env.KAFKA_WRAPPER == "true"){
                    kwBumpVersionPrefixPatch()
                }
                if( env.RAPP_SIMULATION == "true"){
                    pythonBumpVersionPrefixPatch()
                }
            }
        }
    }
}
def kwBumpVersionPrefixPatch() {
    env.oldPatchVersionPrefix = readFile "kafka-wrapper/VERSION_PREFIX"
    env.VERSION_PREFIX_CURRENT = env.oldPatchVersionPrefix.trim()
    sh 'docker run --rm -v $PWD/kafka-wrapper/VERSION_PREFIX:/app/VERSION -w /app --user $(id -u):$(id -g) armdocker.rnd.ericsson.se/proj-eric-oss-drop/utilities/bump patch'
    env.newPatchVersionPrefix = readFile "kafka-wrapper/VERSION_PREFIX"
    env.VERSION_PREFIX_UPDATED = env.newPatchVersionPrefix.trim()
        echo "VERSION_PREFIX has been bumped from ${VERSION_PREFIX_CURRENT} to ${VERSION_PREFIX_UPDATED}"
        sh """
            git add kafka-wrapper/VERSION_PREFIX
            git commit -m "[ci-skip] Kafka wrapper Automatic new patch version bumping: ${VERSION_PREFIX_UPDATED}"
            git push origin HEAD:master
        """
}
def pythonBumpVersionPrefixPatch() {
    env.oldPatchVersionPrefix = readFile "rapp-simulation/VERSION_PREFIX"
    env.VERSION_PREFIX_CURRENT = env.oldPatchVersionPrefix.trim()
    sh 'docker run --rm -v $PWD/rapp-simulation/VERSION_PREFIX:/app/VERSION -w /app --user $(id -u):$(id -g) armdocker.rnd.ericsson.se/proj-eric-oss-drop/utilities/bump patch'
    env.newPatchVersionPrefix = readFile "rapp-simulation/VERSION_PREFIX"
    env.VERSION_PREFIX_UPDATED = env.newPatchVersionPrefix.trim()
        echo "VERSION_PREFIX has been bumped from ${VERSION_PREFIX_CURRENT} to ${VERSION_PREFIX_UPDATED}"
        sh """
            git add rapp-simulation/VERSION_PREFIX
            git commit -m "[ci-skip] rapp simulation Automatic new patch version bumping: ${VERSION_PREFIX_UPDATED}"
            git push origin HEAD:master
        """
}

// More about @Builder: http://mrhaki.blogspot.com/2014/05/groovy-goodness-use-builder-ast.html
import groovy.transform.builder.Builder
import groovy.transform.builder.SimpleStrategy
@Builder(builderStrategy = SimpleStrategy, prefix = '')
class BobCommand {
    def bobImage = 'bob.2.0:latest'
    def envVars = [:]
    def needDockerSocket = false
    String toString() {
        def env = envVars
                .collect({ entry -> "-e ${entry.key}=\"${entry.value}\"" })
                .join(' ')
        def cmd = """\
            |docker run
            |--init
            |--rm
            |--workdir \${PWD}
            |--user \$(id -u):\$(id -g)
            |-v \${PWD}:\${PWD}
            |-v /etc/group:/etc/group:ro
            |-v /etc/passwd:/etc/passwd:ro
            |-v \${HOME}:\${HOME}
            |-v /proj/mvn/:/proj/mvn
            |${needDockerSocket ? '-v /var/run/docker.sock:/var/run/docker.sock' : ''}
            |${env}
            |\$(for group in \$(id -G); do printf ' --group-add %s' "\$group"; done)
            |--group-add \$(stat -c '%g' /var/run/docker.sock)
            |${bobImage}
            |"""
        return cmd
                .stripMargin()           // remove indentation
                .replace('\n', ' ')      // join lines
                .replaceAll(/[ ]+/, ' ') // replace multiple spaces by one
    }
}
