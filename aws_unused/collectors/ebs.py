class EBSCollector:
    service = "ebs"
    display_name = "EBS"
    def __init__(self, aws):
        self.client = aws.client("ec2")
        self.region = aws.region

    @staticmethod
    def get_name(tags):
        if not tags:
            return ""

        for tag in tags:
            if tag["Key"] == "Name":
                return tag["Value"]

        return ""

    def collect(self):
        findings = []

        paginator = self.client.get_paginator("describe_volumes")

        for page in paginator.paginate():
            for volume in page["Volumes"]:
                if volume["State"] != "available":
                    continue

                findings.append({
                    "service": "EBS",
                    "resource_id": volume["VolumeId"],
                    "resource_name": self.get_name(volume.get("Tags")),
                    "finding": "UNATTACHED_VOLUME",
                    "risk": "High",
                    "region": self.region,
                    "details": {
                        "size_gb": volume["Size"],
                        "volume_type": volume["VolumeType"],
                        "state": volume["State"],
                        "availability_zone": volume["AvailabilityZone"],
                        "encrypted": volume["Encrypted"],
                        "iops": volume.get("Iops", ""),
                        "snapshot_id": volume.get("SnapshotId", ""),
                        "create_time": volume["CreateTime"].strftime("%Y-%m-%d %H:%M:%S")
                    }
                })

        return findings