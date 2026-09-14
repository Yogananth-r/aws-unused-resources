# AWS Unused Resources Finder

A read-only AWS CLI tool that scans an AWS account for potentially unused resources and generates an Excel report.

It checks EC2, EBS, Elastic IPs, AMIs, RDS, Load Balancers, EFS, and S3. The tool only reads AWS resources and never modifies or deletes them.

## Installation in AWS CloudShell

### Clone the Repository

```bash
git clone https://github.com/Yogananth-r/aws-unused-resources
cd aws-unused-resources
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install the CLI

```bash
pip install -e .
```

Verify the installation:

```bash
aws-unused --help
```

Check the version:

```bash
aws-unused --version
```

## Usage

### Scan All Supported Services

```bash
aws-unused scan
```

Generates:

```text
unused_resources.xlsx
```

### Scan a Specific Service

```bash
aws-unused scan --service ec2
```

```bash
aws-unused scan --service ebs
```

```bash
aws-unused scan --service rds
```

```bash
aws-unused scan --service ami
```

```bash
aws-unused scan --service elastic-ip
```

```bash
aws-unused scan --service elbv2
```

```bash
aws-unused scan --service efs
```

```bash
aws-unused scan --service s3
```

### Specify AWS Region

```bash
aws-unused scan --region ap-south-1
```

### Custom Output File

```bash
aws-unused scan --output unused-report.xlsx
```

### Control Parallel Workers

Default is 6 workers:

```bash
aws-unused scan --workers 8
```

### Combine Options

```bash
aws-unused scan \
    --service ec2 \
    --region ap-south-1 \
    --workers 4 \
    --output ec2-report.xlsx
```

## Supported Detectors

| Service       | Detection                         |
| ------------- | --------------------------------- |
| EC2           | Stopped instances                 |
| EBS           | Unattached volumes                |
| Elastic IP    | Unassociated Elastic IPs          |
| AMI           | Unused account-owned AMIs         |
| RDS           | Stopped DB instances              |
| Load Balancer | No registered targets             |
| EFS           | No client connections for 30 days |
| S3            | Empty buckets                     |

## Output

The generated Excel report contains:

* Summary
* Service-specific sheets
* Consolidated Findings sheet

The tool is **read-only** and does not perform automatic cleanup.