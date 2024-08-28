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
        SERO_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SERO_ARTIFACTORY_PSW}'
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
                sh "${bob} init-precodereview"
                script {
                    env.KAFKA_WRAPPER = true
                    echo "Value of KAFKA_WRAPPER: ${env.KAFKA_WRAPPER}"
                    authorName = sh(returnStdout: true, script: 'git show -s --pretty=%an')
                    currentBuild.displayName = currentBuild.displayName + ' / ' + authorName
                }
            }
        }
        stage('Python App Init') {
            steps {
                sh "${bob} init-precodereview -r python-ruleset2.0.yaml"
                script {
                    env.RAPP_SIMULATION = true
                    echo "Value of RAPP_SIMULATION: ${env.RAPP_SIMULATION}"
                    authorName = sh(returnStdout: true, script: 'git show -s --pretty=%an')
                    currentBuild.displayName = currentBuild.displayName + ' / ' + authorName
                }
            }
        }
        stage('Kafka wrapper Image') {
            steps {
                sh "${bob} image"
            }
        }
        stage('Python App Image') {
            steps {
                sh "${bob} image -r python-ruleset2.0.yaml"
            }
        }
        stage('Kafka wrapper Package') {
            steps {
                script {
                    sh "${bob} package"
                }
            }
        }
        stage('Python App Package') {
            steps {
                script {
                    sh "${bob} package -r python-ruleset2.0.yaml"
                }
            }
        }
}
    post {
        success {
            script {
                echo "Test"
                echo "Value outside of KAFKA_WRAPPER: ${env.KAFKA_WRAPPER}"
                echo "Value of outside RAPP_SIMULATION: ${env.RAPP_SIMULATION}"
                if( env.KAFKA_WRAPPER == "true"){
                echo "Value of KAFKA_WRAPPER: ${env.KAFKA_WRAPPER}"
                }
                if( env.RAPP_SIMULATION == "true"){
                echo "Value of RAPP_SIMULATION: ${env.RAPP_SIMULATION}"
                }
            }
        }
    }

    
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
