import boto3
import requests
from datetime import datetime, timedelta
import os 

#Note, this script was mainly tested on AWS Lambda, but can also run as a Cronjob.

#Uncomment and wrap under the following to make it work for AWS Lambda
#def lambda_handler(event, context):
#    ...


#Set those variables before running the script
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_CONSOLE_BASE_URL = f"https://{AWS_REGION}.console.aws.amazon.com/costmanagement/home?region={AWS_REGION}"

client = boto3.client('ce')    
def get_service_costs(start_date, end_date, excluded_services):
    # Create a filter to exclude the specified services
    service_filter = {
        "Not": {
            "Dimensions": {
                "Key": "SERVICE",
                "Values": excluded_services
            }
        }
    }  
    response = client.get_cost_and_usage(
        TimePeriod={'Start': str(start_date), 'End': str(end_date)},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
        Filter=service_filter
    )
    service_costs = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service_name = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            if service_name not in service_costs:
                service_costs[service_name] = 0.0
            service_costs[service_name] += amount
    return service_costs

# Specify the services you want to exclude
services_to_exclude = ["Tax", "WIZ Cloud Infrastructure Security Platform","Firebolt","Human Defense Platform","Imply Polaris","JumpCloud Open Directory Platform","AWS Support (Enterprise)"]
# Calculate date ranges for the current and previous weeks
end_date = datetime.today().date() 
start_date = end_date - timedelta(days=7)
previous_end_date = start_date
previous_start_date = previous_end_date - timedelta(days=7)

# Get service costs for the current week and the previous week
current_week_costs = get_service_costs(start_date, end_date, services_to_exclude)
previous_week_costs = get_service_costs(previous_start_date, previous_end_date, services_to_exclude)

# Function to identify billing changes and alert accordingly
def identify_service_changes(current_costs, previous_costs):
    report_lines = []
    all_services = set(current_costs.keys()).union(set(previous_costs.keys()))
    
    for service in all_services:
        current_cost = current_costs.get(service, 0.0)
        previous_cost = previous_costs.get(service, 0.0)
        delta = current_cost - previous_cost
        
        if delta > 1:
            if delta > 100:
                if delta < 1000:
                    report_lines.append(f"      :large_orange_circle: *{service} increased by +${delta:.2f}*")
                else:
                    report_lines.append(f"      :red_circle: *{service} significantly increased by +${delta:.2f}*")
            else:
                report_lines.append(f"      :large_green_circle: *{service} increased slightly by +${delta:.2f}*")
        elif delta < -1:
            report_lines.append(f"      :large_green_circle: *{service} decreased by -${-delta:.2f}*")
    
    return "\n".join(report_lines)

# Identify changes in services
service_changes = identify_service_changes(current_week_costs, previous_week_costs)

report_url = f"{AWS_CONSOLE_BASE_URL}#/cost-explorer?chartStyle=STACK&costAggregate=unBlendedCost&endDate={end_date - timedelta(days=1)}&excludeForecasting=true&filter=%5B%7B%22dimension%22:%7B%22id%22:%22Service%22,%22displayValue%22:%22Service%22%7D,%22operator%22:%22EXCLUDES%22,%22values%22:%5B%7B%22value%22:%22WIZ%20Cloud%20Infrastructure%20Security%20Platform%22,%22displayValue%22:%22WIZ%20Cloud%20Infrastructure%20Security%20Platform%22%7D,%7B%22value%22:%22Tax%22,%22displayValue%22:%22Tax%22%7D,%7B%22value%22:%22JumpCloud%20Open%20Directory%20Platform%22,%22displayValue%22:%22JumpCloud%20Open%20Directory%20Platform%22%7D,%7B%22value%22:%22Imply%20Polaris%22,%22displayValue%22:%22Imply%20Polaris%22%7D,%7B%22value%22:%22Human%20Defense%20Platform%22,%22displayValue%22:%22Human%20Defense%20Platform%22%7D,%7B%22value%22:%22Firebolt%22,%22displayValue%22:%22Firebolt%22%7D,%7B%22value%22:%22AWS%20Support%20(Enterprise)%22,%22displayValue%22:%22Support%20(Enterprise)%22%7D%5D%7D%5D&futureRelativeRange=CUSTOM&granularity=Daily&groupBy=%5B%22RecordTypeV2%22%5D&historicalRelativeRange=CUSTOM&isDefault=true&reportName=New%20cost%20and%20usage%20report&showOnlyUncategorized=false&showOnlyUntagged=false&startDate={start_date}&usageAggregate=undefined&useNormalizedUnits=false"

report_url_last_week = f"{AWS_CONSOLE_BASE_URL}#/cost-explorer?chartStyle=STACK&costAggregate=unBlendedCost&endDate={previous_end_date - timedelta(days=1)}&excludeForecasting=true&filter=%5B%7B%22dimension%22:%7B%22id%22:%22Service%22,%22displayValue%22:%22Service%22%7D,%22operator%22:%22EXCLUDES%22,%22values%22:%5B%7B%22value%22:%22WIZ%20Cloud%20Infrastructure%20Security%20Platform%22,%22displayValue%22:%22WIZ%20Cloud%20Infrastructure%20Security%20Platform%22%7D,%7B%22value%22:%22Tax%22,%22displayValue%22:%22Tax%22%7D,%7B%22value%22:%22JumpCloud%20Open%20Directory%20Platform%22,%22displayValue%22:%22JumpCloud%20Open%20Directory%20Platform%22%7D,%7B%22value%22:%22Imply%20Polaris%22,%22displayValue%22:%22Imply%20Polaris%22%7D,%7B%22value%22:%22Human%20Defense%20Platform%22,%22displayValue%22:%22Human%20Defense%20Platform%22%7D,%7B%22value%22:%22Firebolt%22,%22displayValue%22:%22Firebolt%22%7D,%7B%22value%22:%22AWS%20Support%20(Enterprise)%22,%22displayValue%22:%22Support%20(Enterprise)%22%7D%5D%7D%5D&futureRelativeRange=CUSTOM&granularity=Daily&groupBy=%5B%22RecordTypeV2%22%5D&historicalRelativeRange=CUSTOM&isDefault=true&reportName=New%20cost%20and%20usage%20report&showOnlyUncategorized=false&showOnlyUntagged=false&startDate={previous_start_date}&usageAggregate=undefined&useNormalizedUnits=false"

report_url_devops = f"{AWS_CONSOLE_BASE_URL}#/cost-explorer?chartStyle=STACK&costAggregate=unBlendedCost&endDate={end_date - timedelta(days=1)}&excludeForecasting=true&filter=%5B%7B%22dimension%22:%7B%22id%22:%22Service%22,%22displayValue%22:%22Service%22%7D,%22operator%22:%22INCLUDES%22,%22values%22:%5B%7B%22value%22:%22Amazon%20Elastic%20Compute%20Cloud%20-%20Compute%22,%22displayValue%22:%22EC2-Instances%20(Elastic%20Compute%20Cloud%20-%20Compute)%22%7D,%7B%22value%22:%22Amazon%20EC2%20Container%20Registry%20(ECR)%22,%22displayValue%22:%22EC2%20Container%20Registry%20(ECR)%22%7D,%7B%22value%22:%22EC2%20-%20Other%22,%22displayValue%22:%22EC2%20-%20Other%22%7D,%7B%22value%22:%22Amazon%20CloudFront%22,%22displayValue%22:%22CloudFront%22%7D,%7B%22value%22:%22Amazon%20Elastic%20Load%20Balancing%22,%22displayValue%22:%22Elastic%20Load%20Balancing%22%7D,%7B%22value%22:%22Amazon%20Simple%20Storage%20Service%22,%22displayValue%22:%22S3%20(Simple%20Storage%20Service)%22%7D,%7B%22value%22:%22Amazon%20Virtual%20Private%20Cloud%22,%22displayValue%22:%22VPC%20(Virtual%20Private%20Cloud)%22%7D,%7B%22value%22:%22Amazon%20Elastic%20Container%20Service%20for%20Kubernetes%22,%22displayValue%22:%22Elastic%20Container%20Service%20for%20Kubernetes%22%7D%5D%7D%5D&futureRelativeRange=CUSTOM&granularity=Daily&groupBy=%5B%22Service%22%5D&historicalRelativeRange=CUSTOM&isDefault=true&reportName=New%20cost%20and%20usage%20report&showOnlyUncategorized=false&showOnlyUntagged=false&startDate={start_date}&usageAggregate=undefined&useNormalizedUnits=false"
report = f"""
*┌──────────────────────────┐*
*Date: {end_date}*
*Weekly AWS Spendings Report:*
:black_small_square: *Total Spending This Week ({start_date} - {end_date - timedelta(days=1)}):* :heavy_dollar_sign:{sum(current_week_costs.values()):.2f}
:black_small_square: *Total Spending Last Week ({previous_start_date} - {previous_end_date - timedelta(days=1)}):* :heavy_dollar_sign:{sum(previous_week_costs.values()):.2f}
*:bar_chart: <{report_url_devops}|Click Here for the DevOps Report!>*
*:bar_chart: <{report_url}|Click Here for the General Report!>*
*:bar_chart: <{report_url_last_week}|Click Here for last week's General Report!>*
:black_small_square: *Service Changes:*
{service_changes}
*└──────────────────────────┘*
"""
#Set the webhook URL, either here or as an ENV.
slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]

payload = {
    'text': report
}
print (report)
response = requests.post(slack_webhook_url, json=payload)