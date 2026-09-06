#!/usr/bin/env python3
"""
Lab 06 (Part 1): Direct Bedrock model invocation.
The AWS equivalent of a basic LLM call.
"""

import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def invoke_claude(prompt):
    """Call Claude via Bedrock."""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


if __name__ == "__main__":
    answer = invoke_claude("Explain what an AWS VPC is in 2 sentences.")
    print(answer)
