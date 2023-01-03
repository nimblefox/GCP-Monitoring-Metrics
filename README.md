# GCP-Monitoring-Metrics

This architecture collects monitoring metrics of various GCP services and writes the metric data to Big Query

You can skip the workflow step if possible, I had to work around the [ingress settings](https://cloud.google.com/run/docs/securing/ingress)

You can also skip the scheduler if you can configure a Cloud run job

Note : I have deleted the JSON file for SA Key, a better way to authenticate would be using [auth](https://github.com/google-github-actions/auth) in the github actions workflow

<img src="https://github.com/nimblefox/GCP-Monitoring-Metrics/blob/main/GCP%20Architecture.png" width="90%"></img>
