class EC2Collector:
    service = "ec2"
    display_name = "EC2"
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

        paginator = self.client.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    state = instance["State"]["Name"]

                    if state != "stopped":
                        continue

                    findings.append({
                        "service": "EC2",
                        "resource_id": instance["InstanceId"],
                        "resource_name": self.get_name(instance.get("Tags")),
                        "finding": "STOPPED_INSTANCE",
                        "risk": "Medium",
                        "region": self.region,
                        "details": {
                            "instance_type": instance["InstanceType"],
                            "availability_zone": instance["Placement"]["AvailabilityZone"],
                            "launch_time": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S"),
                            "private_ip": instance.get("PrivateIpAddress", ""),
                            "public_ip": instance.get("PublicIpAddress", ""),
                            "platform": instance.get("Platform", "Linux/UNIX"),
                            "state": state
                        }
                    })

        return findings