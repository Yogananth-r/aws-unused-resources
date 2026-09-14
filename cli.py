import argparse
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

from collectors import COLLECTORS, SUPPORTED_SERVICES
from utils.aws_session import AWSSession

from analyzer.findings import FindingsAnalyzer
from exporter.excel import ExcelExporter

SUPPORTED_SERVICES = [
    "ec2",
    "ebs",
    "elastic-ip",
    "ami",
    "rds",
    "elbv2",
    "efs",
    "s3"
]


def print_banner():
    print("=" * 70)
    print("              AWS Unused Resources Finder")
    print("=" * 70)


def scan_resources(service, output, region, profile, workers):
    aws = AWSSession(region=region, profile=profile)

    print(f"AWS Account : {aws.account_id()}")
    print(f"AWS Region  : {aws.region}")
    print()

    selected = (
        {service: COLLECTORS[service]}
        if service
        else COLLECTORS
    )

    findings = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(collector(aws).collect): collector
            for collector in selected.values()
        }

        for future in as_completed(futures):
            collector = futures[future]

            try:
                result = future.result()
                findings.extend(result)

                print(
                    f"[✓] {collector.display_name:<12}"
                    f"{len(result)} findings"
                )

            except Exception as e:
                print(
                    f"[✗] {collector.display_name:<12}"
                    f"{e}"
                )

    duration = round(time.time() - start, 2)

    analyzer = FindingsAnalyzer(findings)
    summary = analyzer.summary()

    exporter = ExcelExporter(
        findings=findings,
        aws=aws,
        output=output
    )

    exporter.export()

    print("-" * 60)
    print(f"Total Findings : {summary['total']}")
    print(f"Output File    : {output}")
    print(f"Duration       : {duration}s")

    return findings


def main():
    parser = argparse.ArgumentParser(
        prog="aws-unused-resources",
        description="Read-only AWS unused resource scanner."
    )

    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan AWS account for unused resources."
    )

    scan_parser.add_argument(
        "--service",
        choices=SUPPORTED_SERVICES,
        help="Scan a single AWS service."
    )

    scan_parser.add_argument(
        "--output",
        default="unused_resources.xlsx",
        help="Excel report filename."
    )

    scan_parser.add_argument(
    "--workers",
    type=int,
    default=6,
    help="Maximum parallel collectors (default: 6)."
        )

    scan_parser.add_argument(
        "--region",
        help="Override AWS region."
    )

    scan_parser.add_argument(
        "--profile",
        help="AWS CLI profile name."
    )

    args = parser.parse_args()

    print_banner()

    if args.command == "scan":
        scan_resources(
                    service=args.service,
                    output=args.output,
                    region=args.region,
                    profile=args.profile,
                    workers=args.workers
                )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()