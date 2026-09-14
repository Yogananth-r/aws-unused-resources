class S3Collector:
    service = "s3"
    display_name = "S3"

    def __init__(self, aws):
        self.client = aws.client("s3")
        self.region = aws.region

    def get_bucket_region(self, bucket_name):
        response = self.client.get_bucket_location(
            Bucket=bucket_name
        )

        location = response.get("LocationConstraint")

        if location is None:
            return "us-east-1"

        if location == "EU":
            return "eu-west-1"

        return location

    def is_empty(self, bucket_name):
        response = self.client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=1
        )

        return response.get("KeyCount", 0) == 0

    def collect(self):
        findings = []

        response = self.client.list_buckets()

        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]

            bucket_region = self.get_bucket_region(
                bucket_name
            )

            if bucket_region != self.region:
                continue

            if not self.is_empty(bucket_name):
                continue

            findings.append({
                "service": "S3",
                "resource_id": bucket_name,
                "resource_name": bucket_name,
                "finding": "EMPTY_BUCKET",
                "risk": "Low",
                "region": self.region,
                "details": {
                    "creation_date": bucket["CreationDate"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "bucket_region": bucket_region
                }
            })

        return findings