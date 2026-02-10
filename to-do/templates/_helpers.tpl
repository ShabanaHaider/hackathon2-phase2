{{/*
Expand the name of the chart.
*/}}
{{- define "hack2-todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "hack2-todo.fullname" -}}
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
{{- define "hack2-todo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hack2-todo.labels" -}}
helm.sh/chart: {{ include "hack2-todo.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "hack2-todo.backend.labels" -}}
{{ include "hack2-todo.labels" . }}
{{ include "hack2-todo.backend.selectorLabels" . }}
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "hack2-todo.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hack2-todo.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "hack2-todo.frontend.labels" -}}
{{ include "hack2-todo.labels" . }}
{{ include "hack2-todo.frontend.selectorLabels" . }}
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "hack2-todo.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hack2-todo.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "hack2-todo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hack2-todo.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret name
*/}}
{{- define "hack2-todo.secretName" -}}
{{- printf "%s-secrets" (include "hack2-todo.fullname" .) }}
{{- end }}
