#!/bin/bash

set -euo pipefail

AWS_REGION="ap-south-1"

ID=$(aws ec2 describe-instances \
    --region "$AWS_REGION" \
    --filters \
        "Name=tag:Name,Values=AuditPilot-App" \
        "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

if [ -z "$ID" ] || [ "$ID" = "None" ]; then
    echo "ERROR: AuditPilot-App instance not found."
    exit 1
fi

echo "Deploying to instance: $ID"

CMD=$(aws ssm send-command \
    --region "$AWS_REGION" \
    --instance-ids "$ID" \
    --document-name AWS-RunShellScript \
    --parameters "commands=/opt/auditpilot/deploy.sh $BUILD_NUMBER" \
    --query 'Command.CommandId' \
    --output text)

echo "SSM Command ID: $CMD"

for i in $(seq 1 60); do

    STATUS=$(aws ssm get-command-invocation \
        --region "$AWS_REGION" \
        --command-id "$CMD" \
        --instance-id "$ID" \
        --query Status \
        --output text 2>/dev/null || true)

    echo "Deployment status: $STATUS"

    if [ "$STATUS" = "Success" ]; then
        echo "Deployment successful!"
        exit 0
    fi

    if [ "$STATUS" = "Failed" ] || [ "$STATUS" = "Cancelled" ]; then
        break
    fi

    sleep 5
done

aws ssm get-command-invocation \
    --region "$AWS_REGION" \
    --command-id "$CMD" \
    --instance-id "$ID" \
    --query StandardErrorContent \
    --output text || true

exit 1
