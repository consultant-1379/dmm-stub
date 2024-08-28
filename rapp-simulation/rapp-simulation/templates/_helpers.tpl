{{/*
Expand the name of the chart.
*/}}
{{- define "rapp-simulation.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "rapp-simulation.fullname" -}}
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
{{- define "rapp-simulation.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "rapp-simulation.labels" -}}
app.kubernetes.io/name: {{ include "rapp-simulation.name" . }}
app.kubernetes.io/version: {{ .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}


{{/*
Selector labels
*/}}
{{- define "rapp-simulation.selectorLabels" -}}
app.kubernetes.io/name: {{ include "rapp-simulation.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "rapp-simulation.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "rapp-simulation.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Used to create kafka wrapper image
*/}}
{{- define "rapp-simulation.imagePath" -}}
    {{- $imageId := index . "imageId" -}}
    {{- $values := index . "values" -}}
    {{- $files := index . "files" -}}
    {{- $productInfo := fromYaml ($files.Get "eric-product-info.yaml") -}}
    {{- $registryUrl := index $productInfo "images" $imageId "registry" -}}
    {{- $repoPath := index $productInfo "images" $imageId "repoPath" -}}
    {{- $name := index $productInfo "images" $imageId "name" -}}
    {{- $tag :=  index $productInfo "images" $imageId "tag" -}}
    {{- if $values.global -}}
        {{- if $values.global.registry -}}
            {{- $registryUrl = default $registryUrl $values.global.registry.url -}}
        {{- end -}}
    {{- end -}}
    {{- if $values.imageCredentials -}}
        {{- if $values.imageCredentials.registry -}}
            {{- $registryUrl = default $registryUrl $values.imageCredentials.registry.url -}}
        {{- end -}}
        {{- if not (kindIs "invalid" $values.imageCredentials.repoPath) -}}
            {{- $repoPath = $values.imageCredentials.repoPath -}}
        {{- end -}}
        {{- $image := index $values.imageCredentials $imageId -}}
        {{- if $image -}}
            {{- if $image.registry -}}
                {{- $registryUrl = default $registryUrl $image.registry.url -}}
            {{- end -}}
            {{- if not (kindIs "invalid" $image.repoPath) -}}
                {{- $repoPath = $image.repoPath -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}
    {{- if $repoPath -}}
        {{- $repoPath = printf "%s/" $repoPath -}}
    {{- end -}}
    {{- printf "%s/%s%s:%s" $registryUrl $repoPath $name $tag -}}
{{- end }}

{{/*
    Create image pull secrets
*/}}
    {{- define "rapp-simulation.pullSecrets" -}}
      {{- $pullSecret := "" -}}
      {{- if .Values.global -}}
          {{- if .Values.global.pullSecret -}}
              {{- $pullSecret = .Values.global.pullSecret -}}
          {{- end -}}
      {{- end -}}
      {{- if .Values.imageCredentials -}}
          {{- if .Values.imageCredentials.pullSecret -}}
              {{- $pullSecret = .Values.imageCredentials.pullSecret -}}
          {{- end -}}
      {{- end -}}
      {{- print $pullSecret -}}
    {{- end -}}







