class RDSCollector:
    service = "rds"
    display_name = "RDS"

    def __init__(self, aws):
        self.client = aws.client("rds")
        self.region = aws.region

    @staticmethod
    def get_name(tags):
        if not tags:
            return ""

        for tag in tags:
            if tag["Key"] == "Name":
                return tag["Value"]

        return ""

    def get_tags(self, arn):
        response = self.client.list_tags_for_resource(
            ResourceName=arn
        )
        return response.get("TagList", [])

    def collect(self):
        findings = []

        paginator = self.client.get_paginator("describe_db_instances")

        for page in paginator.paginate():
            for db in page["DBInstances"]:

                if db["DBInstanceStatus"] != "stopped":
                    continue

                tags = self.get_tags(db["DBInstanceArn"])

                findings.append({
                    "service": "RDS",
                    "resource_id": db["DBInstanceIdentifier"],
                    "resource_name": self.get_name(tags),
                    "finding": "STOPPED_RDS_INSTANCE",
                    "risk": "Medium",
                    "region": self.region,
                    "details": {
                        "engine": db["Engine"],
                        "engine_version": db["EngineVersion"],
                        "instance_class": db["DBInstanceClass"],
                        "status": db["DBInstanceStatus"],
                        "availability_zone": db.get("AvailabilityZone", ""),
                        "multi_az": db.get("MultiAZ", False),
                        "storage_gb": db.get("AllocatedStorage", ""),
                        "storage_type": db.get("StorageType", ""),
                        "backup_retention_days": db.get("BackupRetentionPeriod", ""),
                        "created_time": db["InstanceCreateTime"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    }
                })

        return findings