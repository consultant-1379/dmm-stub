{{/*
Expand the name of the chart.
*/}}
{{- define "kafka-oauth-java-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kafka-oauth-java-app.fullname" -}}
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
{{- define "kafka-oauth-java-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kafka-oauth-java-app.labels" -}}
helm.sh/chart: {{ include "kafka-oauth-java-app.chart" . }}
{{ include "kafka-oauth-java-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kafka-oauth-java-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kafka-oauth-java-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "kafka-oauth-java-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "kafka-oauth-java-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}



{{/*
Used to create kafka wrapper inside service mesh
*/}}
{{- define "kafka-oauth-java-app.service-mesh-inject" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/inject: "true"
{{- else -}}
sidecar.istio.io/inject: "false"
{{- end -}}
{{- end -}}


{{/*
This helper defines which out-mesh services will be reached by wrapper.
*/}}
{{- define "kafka-oauth-java-app.service-mesh-ism2osm-labels" }}
{{- if .Values.env.TLS }}
eric-oss-dmm-kf-op-sz-kafka-ism-access: "true"
eric-data-object-storage-mn-ism-access: "true"
{{- end -}}
{{- end -}}

{{/*
This helper defines label for object-storage-mn-access.
*/}}
{{- define "kafka-oauth-java-app.eric-data-object-storage-mn-access-label" -}}
eric-data-object-storage-mn-access: "true"
{{- end -}}

{{/*
This helper defines the annotation for defining service mesh volume. Here, the wrapper certificates are mounted inside istio proxy container 
*/}}
{{- define "kafka-oauth-java-app.service-mesh-volume" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/userVolume: '{"kafka-oauth-java-app-kafka-certs-tls":{"secret":{"secretName":"kafka-oauth-java-app-secret","optional":true}},"kafka-oauth-java-app-certs-ca-tls":{"secret":{"secretName":"eric-sec-sip-tls-trusted-root-cert"}},"kafka-oauth-java-app-bdr-certs-tls":{"secret":{"secretName":"kafka-oauth-java-app-bdr-secret","optional":true}}}'
sidecar.istio.io/userVolumeMount: '{"kafka-oauth-java-app-kafka-certs-tls":{"mountPath":"/etc/istio/tls/eric-oss-dmm-kf-op-sz-kafka-bootstrap/","readOnly":true},"kafka-oauth-java-app-bdr-certs-tls":{"mountPath":"/etc/istio/tls/eric-data-object-storage-mn/","readOnly":true},"kafka-oauth-java-app-certs-ca-tls":{"mountPath":"/etc/istio/tls-ca","readOnly":true}}'
{{ end }}
{{- end -}}