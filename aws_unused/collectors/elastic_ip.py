class ElasticIPCollector:
    service = "elastic-ip"
    display_name = "Elastic IP"

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

        response = self.client.describe_addresses()

        for address in response["Addresses"]:
            if "AssociationId" in address:
                continue

            findings.append({
                "service": "Elastic IP",
                "resource_id": address["AllocationId"],
                "resource_name": self.get_name(address.get("Tags")),
                "finding": "UNASSOCIATED_ELASTIC_IP",
                "risk": "High",
                "region": self.region,
                "details": {
                    "public_ip": address["PublicIp"],
                    "domain": address["Domain"],
                    "network_border_group": address.get("NetworkBorderGroup", "")
                }
            })

        return findings