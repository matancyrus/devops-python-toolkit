# AWS Weekly Cost Report to Slack

A Python script that generates a weekly AWS cost report using AWS Cost Explorer and sends the summary to Slack.

The script compares the current week's AWS service costs with the previous week, highlights cost changes, and includes direct links to AWS Cost Explorer reports.

## Features

* Retrieves AWS costs using Cost Explorer
* Compares current week vs previous week
* Excludes predefined services such as Tax, AWS Support, and marketplace tools
* Detects service-level cost increases and decreases
* Sends a formatted report to Slack
* Supports AWS Lambda or scheduled cron execution

## Requirements

* Python 3.x
* AWS credentials with Cost Explorer permissions
* Slack Incoming Webhook URL

Python packages:

```bash
pip install boto3 requests
```

## Environment Variables

Set the following environment variables before running the script:

```bash
export AWS_REGION="us-east-1"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

`AWS_REGION` is used to generate the AWS Console Cost Explorer links.

`SLACK_WEBHOOK_URL` is used to send the report to Slack.

## AWS IAM Permissions

The script requires permission to read Cost Explorer data:

```json
{
  "Effect": "Allow",
  "Action": [
    "ce:GetCostAndUsage"
  ],
  "Resource": "*"
}
```

## Usage

Run the script manually:

```bash
python costmanagement-2-slack.py
```

Or deploy it as an AWS Lambda function and trigger it on a schedule using EventBridge.

Example schedule:

```text
rate(7 days)
```

## Output

The Slack message includes:

* Total spending for the current week
* Total spending for the previous week
* Links to AWS Cost Explorer reports
* Service-level cost changes

Example:

```text
Weekly AWS Spendings Report:
Total Spending This Week: $123.45
Total Spending Last Week: $98.20

Service Changes:
EC2 increased by +$25.25
S3 decreased by -$4.10
```

