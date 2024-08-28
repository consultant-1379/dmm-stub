{{/*
Expand the name of the chart.
*/}}
{{- define "kafka-wrapper.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Expand the name of the chart.
*/}}
{{- define "kafka-ingress-wrapper.name" -}}
{{- .Values.KafkaIngressWrapper.name }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kafka-wrapper.fullname" -}}
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
{{- define "kafka-wrapper.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kafka-wrapper.labels" -}}
app.kubernetes.io/name: {{ include "kafka-wrapper.name" . }}
app.kubernetes.io/version: {{ .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kafka-ingress-wrapper.labels" -}}
app.kubernetes.io/name: {{ include "kafka-ingress-wrapper.name" . }}
app.kubernetes.io/version: {{ .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kafka-wrapper.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kafka-wrapper.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kafka-ingress-wrapper.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kafka-ingress-wrapper.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "kafka-wrapper.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "kafka-wrapper.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
{{/*
This helper defines label for object-storage-mn-access.
*/}}
{{- define "kafka-wrapper.eric-data-object-storage-mn-access-label" -}}
eric-data-object-storage-mn-access: "true"
{{- end -}}
{{/*
Used to create kafka wrapper image
*/}}
{{- define "kafka-wrapper.imagePath" -}}
    {{- $productInfo := fromYaml (.Files.Get "eric-product-info.yaml") -}}
    {{- $registryUrl := (index $productInfo "images" "kafka-wrapper" "registry") -}}
    {{- $repoPath := (index $productInfo "images" "kafka-wrapper" "repoPath") -}}
    {{- $name := (index $productInfo "images" "kafka-wrapper" "name") -}}
    {{- $tag := (index $productInfo "images" "kafka-wrapper" "tag") -}}
    {{- printf "%s/%s/%s:%s" $registryUrl $repoPath $name $tag -}}
{{- end }}

{{/*
Used to create kafka wrapper inside service mesh
*/}}
{{- define "kafka-wrapper.service-mesh-inject" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/inject: "true"
{{- else -}}
sidecar.istio.io/inject: "false"
{{- end -}}
{{- end -}}

{{/*
This helper defines which out-mesh services will be reached by wrapper.
*/}}
{{- define "kafka-wrapper.service-mesh-ism2osm-labels" }}
{{- if .Values.env.TLS }}
eric-oss-dmm-kf-op-sz-kafka-ism-access: "true"
eric-data-object-storage-mn-ism-access: "true"
{{- end -}}
{{- end -}}

{{/*
This helper defines the annotation for defining service mesh volume. Here, the wrapper certificates are mounted inside istio proxy container 
*/}}
{{- define "kafka-wrapper.service-mesh-volume" }}
{{- if .Values.env.TLS }}
sidecar.istio.io/userVolume: '{"kafka-wrapper-kafka-certs-tls":{"secret":{"secretName":"kafka-wrapper-secret","optional":true}},"kafka-wrapper-certs-ca-tls":{"secret":{"secretName":"eric-sec-sip-tls-trusted-root-cert"}},"kafka-wrapper-bdr-certs-tls":{"secret":{"secretName":"kafka-wrapper-bdr-secret","optional":true}}}'
sidecar.istio.io/userVolumeMount: '{"kafka-wrapper-kafka-certs-tls":{"mountPath":"/etc/istio/tls/eric-oss-dmm-kf-op-sz-kafka-bootstrap/","readOnly":true},"kafka-wrapper-bdr-certs-tls":{"mountPath":"/etc/istio/tls/eric-data-object-storage-mn/","readOnly":true},"kafka-wrapper-certs-ca-tls":{"mountPath":"/etc/istio/tls-ca","readOnly":true}}'
{{ end }}
{{- end -}}


{{/*
This heper defines the division of two variables and ensure result will next positive integer
*/}}
{{- define "kafka-wrapper.adcload-replicageneration" -}}
{{- if .Values.kafka.adcload -}}
{{- $totalmsgs := .Values.kafka.adctotalmessages -}}
{{- $singlereplicamsgs := .Values.kafka.adcmsgsperreplica -}}
{{- $result := div $totalmsgs $singlereplicamsgs -}}
{{- $result := add $result 1}}
{{- printf "%d" $result -}}
{{- end -}}
{{- end -}}
