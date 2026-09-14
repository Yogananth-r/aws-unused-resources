# AWS Unused Resources Finder

A read-only Python CLI tool that scans an AWS account for potentially unused resources and generates an Excel report.

The tool runs multiple AWS resource collectors in parallel and identifies resources such as stopped EC2 instances, unattached EBS volumes, unassociated Elastic IPs, unused AMIs, stopped RDS instances, unused Load Balancers, inactive EFS file systems, and empty S3 buckets.

## Features

* Read-only AWS resource scanning
* Parallel resource collectors
* AWS account and region detection
* Single-service scanning
* Configurable worker count
* Excel report generation
* Risk classification
* Consolidated findings sheet
* Service-specific Excel sheets
* No resource deletion or modification

## Resources Detected

| Service       | Detection                                   |
| ------------- | ------------------------------------------- |
| EC2           | Stopped instances                           |
| EBS           | Unattached volumes                          |
| Elastic IP    | Unassociated Elastic IPs                    |
| AMI           | Unreferenced account-owned AMIs             |
| RDS           | Stopped DB instances                        |
| Load Balancer | ALB/NLB with no registered targets          |
| EFS           | No client connections over the last 30 days |
| S3            | Empty buckets                               |

## Architecture

```text
                         AWS Account
                              |
                              v
                       +--------------+
                       |  AWSSession  |
                       +------+-------+
                              |
                    ThreadPoolExecutor
                              |
          +---------+---------+---------+---------+
          |         |         |         |         |
         EC2       EBS       AMI       RDS       EFS
          |         |         |         |         |
         EIP       S3       ELBv2       |         |
          |         |         |         |         |
          +---------+---------+---------+---------+
                              |
                              v
                     FindingsAnalyzer
                              |
                              v
                      ExcelExporter
                              |
                              v
                  unused_resources.xlsx
```

## Project Structure

```text
aws-unused-resources/
│
├── cli.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── collectors/
│   ├── __init__.py
│   ├── ec2.py
│   ├── ebs.py
│   ├── elastic_ip.py
│   ├── ami.py
│   ├── rds.py
│   ├── elbv2.py
│   ├── efs.py
│   └── s3.py
│
├── analyzer/
│   ├── __init__.py
│   └── findings.py
│
├── exporter/
│   ├── __init__.py
│   └── excel.py
│
└── utils/
    ├── __init__.py
    └── aws_session.py
```

## Requirements

* Python 3.10+
* AWS account
* AWS credentials configured locally
* Read-only permissions for the services being scanned

## Installation

Clone the repository:

```bash
git clone <tbd>
cd aws-unused-resources
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## AWS Credentials

The tool uses the standard Boto3 credential chain.

For example, configure AWS CLI credentials:

```bash
aws configure
```

Verify the configured identity:

```bash
aws sts get-caller-identity
```

You can also use a named AWS CLI profile:

```bash
python cli.py scan --profile my-profile
```

## Usage

### Scan the entire account

```bash
python cli.py scan
```

The default output file is:

```text
unused_resources.xlsx
```

### Scan a specific service

```bash
python cli.py scan --service ec2
```

Available services:

```text
ec2
ebs
elastic-ip
ami
rds
elbv2
efs
s3
```

### Specify an output filename

```bash
python cli.py scan --output aws-unused-report.xlsx
```

### Specify AWS region

```bash
python cli.py scan --region ap-south-1
```

### Use a specific AWS profile

```bash
python cli.py scan --profile my-profile
```

### Change the number of parallel workers

Default:

```text
6 workers
```

Example:

```bash
python cli.py scan --workers 8
```

## Excel Report

The generated workbook contains:

```text
Summary
EC2
EBS
ElasticIP
AMI
RDS
LoadBalancer
EFS
S3
Findings
```

### Summary

Contains:

* AWS account ID
* AWS region
* Report generation time
* Findings by service
* Total findings

### Service Sheets

Each service sheet contains:

* Resource ID
* Resource name
* Finding
* Risk
* Region
* Resource details

### Findings

A consolidated view of all detected unused resources.

## Risk Levels

| Risk   | Meaning                                                                  |
| ------ | ------------------------------------------------------------------------ |
| High   | Resource may have significant ongoing cost or should be reviewed quickly |
| Medium | Potentially unused resource requiring review                             |
| Low    | Lower-impact unused resource                                             |

The tool does **not** automatically delete resources based on risk.

## Future Improvements

Possible future versions may include:

* Multi-region scanning
* Cost estimation
* More unused-resource detectors
* HTML/CSV/JSON reports
* Historical reports
* Cost optimization recommendations
* Optional cleanup workflow with explicit confirmation
