# Analyst session 7 - Bedrock for AI teams. No model is called: botocore checks the request against
# Bedrock's real API schema, and a Stubber stands in for the response (clearly fake).
import json, boto3
from botocore.stub import Stubber

MODEL = "amazon.nova-micro-v1:0"
rt = boto3.client("bedrock-runtime", region_name="us-east-1", aws_access_key_id="x", aws_secret_access_key="x")
request = {
    "modelId": MODEL,
    "messages": [{"role": "user", "content": [{"text": "Classify this trip note as fare_dispute, lost_item or other: 'driver kept my umbrella'"}]}],
    "inferenceConfig": {"maxTokens": 20, "temperature": 0},
}
with Stubber(rt) as stub:
    stub.add_response("converse", {
        "output": {"message": {"role": "assistant", "content": [{"text": "lost_item (STUBBED, not a model output)"}]}},
        "stopReason": "end_turn", "usage": {"inputTokens": 31, "outputTokens": 4, "totalTokens": 35}, "metrics": {"latencyMs": 0},
    }, request)
    r = rt.converse(**request)
    print("request accepted by the Converse schema; stubbed reply:", r["output"]["message"]["content"][0]["text"])
try:
    rt.converse(modelId=MODEL, messages=[{"role": "user", "content": "plain string"}])
except Exception as e:
    print("schema check catches a malformed request:", type(e).__name__)

# The cost of classifying a backlog, at Price List rates (us-east-1, retrieved 2026-10-03), per 1K tokens
IN_OD, OUT_OD, IN_BATCH, OUT_BATCH = 0.000035, 0.00014, 0.0000175, 0.00007
notes, tok_in, tok_out = 1_000_000, 120, 8          # your volumes and token counts will differ: assumptions
od = notes * (tok_in * IN_OD + tok_out * OUT_OD) / 1000
batch = notes * (tok_in * IN_BATCH + tok_out * OUT_BATCH) / 1000
print(f"1,000,000 notes on Nova Micro: on-demand ${od:,.2f}, batch ${batch:,.2f}")

# There is no bedrock:Converse IAM action: the AWS service reference lists 262 Bedrock actions and
# only InvokeModel and InvokeModelWithResponseStream for inference, so Converse is authorised by InvokeModel.
LEAST = {"Version": "2012-10-17", "Statement": [{"Sid": "OneModelOnly", "Effect": "Allow",
         "Action": ["bedrock:InvokeModel"],
         "Resource": f"arn:aws:bedrock:us-east-1::foundation-model/{MODEL}"}]}
print(json.dumps(LEAST["Statement"][0]["Action"]), "on", LEAST["Statement"][0]["Resource"])
