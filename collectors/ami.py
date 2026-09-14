from datetime import datetime, timezone


class AMICollector:
    service = "ami"
    display_name = "AMI"

    def __init__(self, aws):
        self.ec2 = aws.client("ec2")
        self.region = aws.region

    @staticmethod
    def get_name(tags):
        if not tags:
            return ""

        for tag in tags:
            if tag["Key"] == "Name":
                return tag["Value"]

        return ""

    def get_used_image_ids(self):
        image_ids = set()

        paginator = self.ec2.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    image_ids.add(instance["ImageId"])

        return image_ids

    def collect(self):
        findings = []

        used_images = self.get_used_image_ids()

        paginator = self.ec2.get_paginator("describe_images")

        for page in paginator.paginate(Owners=["self"]):
            for image in page["Images"]:

                if image["State"] != "available":
                    continue

                if image["ImageId"] in used_images:
                    continue

                created = datetime.fromisoformat(
                    image["CreationDate"].replace("Z", "+00:00")
                )

                age_days = (datetime.now(timezone.utc) - created).days

                findings.append({
                    "service": "AMI",
                    "resource_id": image["ImageId"],
                    "resource_name": image.get("Name", ""),
                    "finding": "UNUSED_AMI",
                    "risk": "High",
                    "region": self.region,
                    "details": {
                        "creation_date": created.strftime("%Y-%m-%d"),
                        "age_days": age_days,
                        "architecture": image.get("Architecture", ""),
                        "platform": image.get("PlatformDetails", ""),
                        "virtualization": image.get("VirtualizationType", ""),
                        "root_device": image.get("RootDeviceType", "")
                    }
                })

        return findings