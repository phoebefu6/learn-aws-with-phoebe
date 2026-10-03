"""Extract the us-east-1 prices the bench uses from the AWS Price List bulk API (no login).

Offer files fetched 2026-10-03 from
  https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<Offer>/current/us-east-1/index.json
Run: python3 build-prices.py <dir holding AmazonS3.json AmazonS3GlacierDeepArchive.json AmazonAthena.json
                                  AWSLambda.json AmazonRedshift.json AWSGlue.json AmazonBedrock.json AmazonECS.json>
Writes materials/prices-us-east-1.json (each price with its SKU, usagetype, description, publicationDate).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1]
RETRIEVED = "2026-10-03"


def dims(offer, usagetype, location="US East (N. Virginia)"):
    d = json.load(open(os.path.join(D, offer + ".json")))
    out = []
    for sku, p in d["products"].items():
        a = p["attributes"]
        if a.get("usagetype") != usagetype or a.get("location") != location:
            continue
        for t in d["terms"]["OnDemand"].get(sku, {}).values():
            for dim in t["priceDimensions"].values():
                out.append({"offer": offer, "sku": sku, "usagetype": usagetype, "unit": dim["unit"],
                            "begin": dim["beginRange"], "end": dim["endRange"],
                            "usd": float(dim["pricePerUnit"]["USD"]), "description": dim["description"].strip(),
                            "publicationDate": d["publicationDate"]})
    if not out:
        raise SystemExit(f"missing {offer} {usagetype}")
    return sorted(out, key=lambda x: float(x["begin"]))


P = {
    "region": "us-east-1", "retrieved": RETRIEVED,
    "source": "AWS Price List bulk API, offers/v1.0/aws/<Offer>/current/us-east-1/index.json",
    "s3": {
        "STANDARD": dims("AmazonS3", "TimedStorage-ByteHrs"),
        "INTELLIGENT_TIERING_FA": dims("AmazonS3", "TimedStorage-INT-FA-ByteHrs"),
        "STANDARD_IA": dims("AmazonS3", "TimedStorage-SIA-ByteHrs"),
        "ONEZONE_IA": dims("AmazonS3", "TimedStorage-ZIA-ByteHrs"),
        "GLACIER_IR": dims("AmazonS3", "TimedStorage-GIR-ByteHrs"),
        "GLACIER": dims("AmazonS3", "TimedStorage-GlacierByteHrs"),
        "DEEP_ARCHIVE": dims("AmazonS3GlacierDeepArchive", "TimedStorage-GDA-ByteHrs"),
        "PUT_TIER1": dims("AmazonS3", "Requests-Tier1"),
        "GET_TIER2": dims("AmazonS3", "Requests-Tier2"),
        "RETRIEVAL_SIA": dims("AmazonS3", "Retrieval-SIA"),
    },
    "fargate": {"VCPU_HR": dims("AmazonECS", "USE1-Fargate-vCPU-Hours:perCPU"), "GB_HR": dims("AmazonECS", "USE1-Fargate-GB-Hours")},
    "athena": {"SCAN_TB": dims("AmazonAthena", "USE1-DataScannedInTB")},
    "lambda": {"REQUEST": dims("AWSLambda", "Request"), "GB_SECOND": dims("AWSLambda", "Lambda-GB-Second")},
    "redshift": {"SERVERLESS_RPU_HR": dims("AmazonRedshift", "USE1-Redshift:ServerlessUsage"),
                 "RMS_GB_MO": dims("AmazonRedshift", "USE1-RMS:Serverless")},
    "glue": {"ETL_DPU_HR": dims("AWSGlue", "USE1-ETL-DPU-Hour"), "CRAWLER_DPU_HR": dims("AWSGlue", "USE1-Crawler-DPU-Hour"),
             "CATALOG_STORAGE": dims("AWSGlue", "USE1-Catalog-Storage"), "CATALOG_REQUEST": dims("AWSGlue", "USE1-Catalog-Request")},
    "bedrock": {"NOVA_MICRO_IN_1K": dims("AmazonBedrock", "USE1-NovaMicro-input-tokens"),
                "NOVA_MICRO_OUT_1K": dims("AmazonBedrock", "USE1-NovaMicro-output-tokens"),
                "NOVA_MICRO_IN_BATCH_1K": dims("AmazonBedrock", "USE1-NovaMicro-input-tokens-batch"),
                "NOVA_MICRO_OUT_BATCH_1K": dims("AmazonBedrock", "USE1-NovaMicro-output-tokens-batch"),
                "NOVA_LITE_IN_1K": dims("AmazonBedrock", "USE1-NovaLite-input-tokens"),
                "NOVA_LITE_OUT_1K": dims("AmazonBedrock", "USE1-NovaLite-output-tokens")},
}
json.dump(P, open(os.path.join(HERE, "prices-us-east-1.json"), "w"), indent=1)
for grp, items in P.items():
    if isinstance(items, dict):
        for k, v in items.items():
            print(grp, k, [(x["begin"], x["usd"], x["unit"]) for x in v])
