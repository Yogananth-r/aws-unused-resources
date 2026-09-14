from aws_unused.collectors.ec2 import EC2Collector
from aws_unused.collectors.ebs import EBSCollector
from aws_unused.collectors.elastic_ip import ElasticIPCollector
from aws_unused.collectors.ami import AMICollector
from aws_unused.collectors.rds import RDSCollector
from aws_unused.collectors.elbv2 import ELBv2Collector
from aws_unused.collectors.efs import EFSCollector
from aws_unused.collectors.s3 import S3Collector

COLLECTORS = {
    EC2Collector.service: EC2Collector,
    EBSCollector.service: EBSCollector,
    ElasticIPCollector.service: ElasticIPCollector,
    AMICollector.service: AMICollector,
    RDSCollector.service: RDSCollector,
    ELBv2Collector.service: ELBv2Collector,
    EFSCollector.service: EFSCollector,
    S3Collector.service: S3Collector,
}

SUPPORTED_SERVICES = list(COLLECTORS.keys())