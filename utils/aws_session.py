import boto3


class AWSSession:
    def __init__(self, region=None, profile=None):
        session_args = {}

        if profile:
            session_args["profile_name"] = profile

        self.session = boto3.Session(**session_args)

        self.region = region or self.session.region_name

        self.sts = self.session.client("sts", region_name=self.region)

    def account_id(self):
        return self.sts.get_caller_identity()["Account"]

    def client(self, service):
        return self.session.client(service, region_name=self.region)

    def resource(self, service):
        return self.session.resource(service, region_name=self.region)