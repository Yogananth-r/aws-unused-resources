class ELBv2Collector:
    service = "elbv2"
    display_name = "Load Balancer"

    def __init__(self, aws):
        self.client = aws.client("elbv2")
        self.region = aws.region

    def collect(self):
        findings = []

        paginator = self.client.get_paginator("describe_load_balancers")

        for page in paginator.paginate():
            for lb in page["LoadBalancers"]:
                target_groups = self.client.get_paginator(
                    "describe_target_groups"
                )

                has_targets = False
                target_group_count = 0

                for tg_page in target_groups.paginate(
                    LoadBalancerArn=lb["LoadBalancerArn"]
                ):
                    for target_group in tg_page["TargetGroups"]:
                        target_group_count += 1

                        response = self.client.describe_target_health(
                            TargetGroupArn=target_group["TargetGroupArn"]
                        )

                        if response["TargetHealthDescriptions"]:
                            has_targets = True
                            break

                    if has_targets:
                        break

                if has_targets:
                    continue

                tags_response = self.client.describe_tags(
                    ResourceArns=[lb["LoadBalancerArn"]]
                )

                tags = tags_response["TagDescriptions"][0].get(
                    "Tags", []
                )

                name = ""

                for tag in tags:
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                        break

                findings.append({
                    "service": "Load Balancer",
                    "resource_id": lb["LoadBalancerArn"],
                    "resource_name": name or lb["LoadBalancerName"],
                    "finding": "NO_REGISTERED_TARGETS",
                    "risk": "Medium",
                    "region": self.region,
                    "details": {
                        "load_balancer_name": lb["LoadBalancerName"],
                        "type": lb["Type"],
                        "scheme": lb["Scheme"],
                        "state": lb["State"]["Code"],
                        "vpc_id": lb["VpcId"],
                        "availability_zones": ", ".join(
                            az["ZoneName"]
                            for az in lb["AvailabilityZones"]
                        ),
                        "target_groups": target_group_count,
                        "dns_name": lb["DNSName"]
                    }
                })

        return findings