from datetime import datetime, date, timedelta
from google.cloud import bigquery, monitoring_v3


class Collector:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_id = project_id
        self.location = location
        self.project_path = f"projects/{project_id}"

    def fetch_metric(self, metric_type: str, metric_name: str):
        """Returns metric data for input metric and resource types.
        Calculates metrics using MQL from 00:00 to 23:59:59 for yesterday
        Code template : https://cloud.google.com/monitoring/custom-metrics/reading-metrics"""
        end_time = datetime.combine(date.today() - timedelta(days=1), datetime.max.time())
        start_time = datetime.combine(date.today() - timedelta(days=1), datetime.min.time())
        end_time_sec = int(end_time.timestamp())
        start_time_sec = int(start_time.timestamp())
        nanos = int((end_time.timestamp() - end_time_sec) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {"seconds": end_time_sec, "nanos": nanos},
                "start_time": {"seconds": start_time_sec},
            }
        )

        aggregation = monitoring_v3.Aggregation(
            {
                "alignment_period": {"seconds": 86400},
                "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MAX,   # choose align method
            }
        )

        results = self.client.list_time_series(
            request={
                "name": self.project_path,
                "filter": f'metric.type = "{metric_type}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation
            }
        )

        for result in results:
            data = [
                {"Time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                 "MetricType": metric_name,
                 "MetricValue": result.points[0].value.int64_value}
            ]

        return data

    def load_metric(self, data, dataset, table):
        """Writes data to Big Query table"""
        client = bigquery.Client(project=self.project_id)
        table_ref = "{}.{}".format(dataset, table)
        table = client.get_table(table_ref)
        errors = client.insert_rows(table, data)
        if not errors:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))


if __name__ == '__main__':

    collector = Collector(project_id='silicon-synapse-372206')

    response = collector.fetch_metric(
        metric_type="storage.googleapis.com/storage/total_bytes",
        metric_name="bucket_size")

    collector.load_metric(data=response, dataset='metrics', table='metric_data')