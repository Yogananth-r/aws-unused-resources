from collectors.ec2 import EC2Collector
from collectors.ebs import EBSCollector
from collectors.elastic_ip import ElasticIPCollector
from collectors.ami import AMICollector
from collectors.rds import RDSCollector
from collectors.elbv2 import ELBv2Collector
from collectors.efs import EFSCollector
from collectors.s3 import S3Collector

COLLECTORS = {
    "ec2": EC2Collector,
    "ebs": EBSCollector,
    "elastic-ip": ElasticIPCollector,
    "ami": AMICollector,
    "rds": RDSCollector,
    "elbv2": ELBv2Collector,
    "efs": EFSCollector,
    "s3": S3Collector,
}


SUPPORTED_SERVICES = list(COLLECTORS.keys())