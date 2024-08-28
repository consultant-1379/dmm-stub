{{/*
Expand the name of the chart.
*/}}
{{- define "acmr-mock.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "acmr-mock.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "acmr-mock.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "acmr-mock.labels" -}}
app.kubernetes.io/name: {{ include "acmr-mock.name" . }}
app.kubernetes.io/version: {{ .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}


{{/*
Selector labels
*/}}
{{- define "acmr-mock.selectorLabels" -}}
app.kubernetes.io/name: {{ include "acmr-mock.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{/*
Create the name of the service account to use
*/}}
{{- define "acmr-mock.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "acmr-mock.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Used to create kafka wrapper image
*/}}
{{- define "acmr-mock.imagePath" -}}
    {{- $productInfo := fromYaml (.Files.Get "eric-product-info.yaml") -}}
    {{- $registryUrl := (index $productInfo "images" "acmr-mock" "registry") -}}
    {{- $repoPath := (index $productInfo "images" "acmr-mock" "repoPath") -}}
    {{- $name := (index $productInfo "images" "acmr-mock" "name") -}}
    {{- $tag := (index $productInfo "images" "acmr-mock" "tag") -}}
    {{- printf "%s/%s/%s:%s" $registryUrl $repoPath $name $tag -}}
{{- end }}

{{/*
Used to create kafka wrapper inside service mesh
*/}}
{{- define "acmr-mock.service-mesh-inject" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/inject: "true"
{{- else -}}
sidecar.istio.io/inject: "false"
{{- end -}}
{{- end -}}

{{/*
This helper defines which out-mesh services will be reached by wrapper.
*/}}
{{- define "acmr-mock.service-mesh-ism2osm-labels" }}
{{- if .Values.env.TLS }}
eric-oss-dmm-kf-op-sz-kafka-ism-access: "true"
{{- end -}}
{{- end -}}

{{/*
This helper defines the annotation for defining service mesh volume. Here, the wrapper certificates are mounted inside istio proxy container 
*/}}
{{- define "acmr-mock.service-mesh-volume" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/userVolume: '{"acmr-mock-kafka-certs-tls":{"secret":{"secretName":"acmr-mock-secret","optional":true}},"acmr-mock-certs-ca-tls":{"secret":{"secretName":"eric-sec-sip-tls-trusted-root-cert"}}}'
sidecar.istio.io/userVolumeMount: '{"acmr-mock-kafka-certs-tls":{"mountPath":"/etc/istio/tls/eric-oss-dmm-kf-op-sz-kafka-bootstrap/","readOnly":true},"acmr-mock-certs-ca-tls":{"mountPath":"/etc/istio/tls-ca","readOnly":true}}'
{{ end }}
{{- end -}}



