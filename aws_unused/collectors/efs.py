from datetime import datetime, timedelta, timezone


class EFSCollector:
    service = "efs"
    display_name = "EFS"

    def __init__(self, aws):
        self.efs = aws.client("efs")
        self.cloudwatch = aws.client("cloudwatch")
        self.region = aws.region

    def get_name(self, tags):
        for tag in tags:
            if tag["Key"] == "Name":
                return tag["Value"]

        return ""

    def get_client_connections(self, filesystem_id):
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=30)

        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EFS",
            MetricName="ClientConnections",
            Dimensions=[
                {
                    "Name": "FileSystemId",
                    "Value": filesystem_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=["Maximum"]
        )

        datapoints = response.get("Datapoints", [])

        if not datapoints:
            return 0

        return max(
            datapoint.get("Maximum", 0)
            for datapoint in datapoints
        )

    def collect(self):
        findings = []

        paginator = self.efs.get_paginator("describe_file_systems")

        for page in paginator.paginate():
            for filesystem in page["FileSystems"]:
                filesystem_id = filesystem["FileSystemId"]

                tags_response = self.efs.describe_tags(
                    FileSystemId=filesystem_id
                )

                tags = tags_response.get("Tags", [])

                connections = self.get_client_connections(
                    filesystem_id
                )

                if connections > 0:
                    continue

                findings.append({
                    "service": "EFS",
                    "resource_id": filesystem_id,
                    "resource_name": (
                        self.get_name(tags)
                        or filesystem.get("Name", "")
                    ),
                    "finding": "NO_CLIENT_CONNECTIONS_30_DAYS",
                    "risk": "Medium",
                    "region": self.region,
                    "details": {
                        "state": filesystem["LifeCycleState"],
                        "performance_mode": filesystem["PerformanceMode"],
                        "throughput_mode": filesystem["ThroughputMode"],
                        "encrypted": filesystem["Encrypted"],
                        "size_bytes": filesystem.get(
                            "SizeInBytes", {}
                        ).get("Value", 0),
                        "client_connections_30d_max": connections,
                        "created_time": filesystem[
                            "CreationTime"
                        ].strftime("%Y-%m-%d %H:%M:%S")
                    }
                })

        return findings