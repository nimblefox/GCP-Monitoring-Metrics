import os
import logging
import time
from flask import Flask
from google.cloud import bigquery, monitoring_v3

app = Flask(__name__)

def get_metric_data(project_id: str, metric_type: str):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    interval = monitoring_v3.TimeInterval()

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - 86400), "nanos": nanos},
        }
    )

    aggregation = monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": 86400},
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MAX,
        }
    )

    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": f'metric.type = "{metric_type}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": aggregation
        }
    )

    for result in results: 
        return result

def load_metric_data(project_id: str, dataset: str, table:str, data):
    client = bigquery.Client(project = project_id)
    table_ref = "{}.{}".format(dataset, table)
    table = client.get_table(table_ref)
    errors = client.insert_rows(table, data)
    if not errors:
        print("New rows have been added !")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


@app.route('/', methods=['POST'])

def handle_post():
    data = get_metric_data(
        project_id="silicon-synapse-372206",
        metric_type="storage.googleapis.com/storage/total_bytes"
        )
    load_metric_data(
        project_id="silicon-synapse-372206",
        dataset="metrics"
        table="metrics-table"
    )
    

if __name__ != '__main__':
    # Redirect Flask logs to Gunicorn logs
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.info('Service started...')
else:
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))