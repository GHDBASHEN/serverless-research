"""
================================================================================
MACRO-BENCHMARK: ETL & JSON Data Processing Pipeline
================================================================================
Simulates realistic serverless event-driven data pipelines (e.g., S3/Blob event 
triggering a Lambda/Function to ingest, validate, transform, and aggregate records).
================================================================================
"""

import json
import random
import time


def etl_json_pipeline(num_records: int = 3000) -> dict:
    """
    End-to-end data transformation pipeline:
      1. Ingests raw JSON batch payload
      2. Validates schema and fields
      3. Filters out anomalies (negative values, inactive users)
      4. Calculates derived business metrics (markup, currency conversion)
      5. Generates summary statistics
    """
    # 1. Generate synthetic raw incoming payload
    raw_records = []
    categories = ["electronics", "clothing", "home", "books", "services"]
    regions = ["us-east", "eu-west", "ap-southeast", "sa-east"]

    for i in range(num_records):
        raw_records.append({
            "transaction_id": f"txn_{i:06d}",
            "user_id": f"usr_{i % 500:04d}",
            "amount": round(random.uniform(5.0, 850.0), 2),
            "category": categories[i % len(categories)],
            "region": regions[i % len(regions)],
            "status": "COMPLETED" if random.random() > 0.08 else "FAILED",
            "is_flagged": random.random() < 0.02
        })

    raw_json_str = json.dumps(raw_records)

    # 2. Pipeline Execution: Deserialize & Validate
    data = json.loads(raw_json_str)

    # 3. Filter valid transactions
    valid_transactions = [
        item for item in data 
        if item["status"] == "COMPLETED" and not item["is_flagged"]
    ]

    # 4. Transform: Add VAT (15%) and categorization
    transformed = []
    for txn in valid_transactions:
        net_amount = txn["amount"]
        vat = round(net_amount * 0.15, 2)
        gross = round(net_amount + vat, 2)
        transformed.append({
            "id": txn["transaction_id"],
            "category": txn["category"],
            "region": txn["region"],
            "net": net_amount,
            "vat": vat,
            "gross": gross
        })

    # 5. Aggregate: Category breakdown
    category_totals = {}
    for item in transformed:
        cat = item["category"]
        category_totals[cat] = category_totals.get(cat, 0.0) + item["gross"]

    # Round totals
    category_totals = {k: round(v, 2) for k, v in category_totals.items()}

    return {
        "total_ingested": len(data),
        "valid_processed": len(transformed),
        "category_totals": category_totals
    }


if __name__ == "__main__":
    print("Running Macro-Benchmark: ETL JSON Pipeline...")
    t0 = time.perf_counter()
    res = etl_json_pipeline(2500)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  Processed {res['valid_processed']} / {res['total_ingested']} records in {elapsed_ms:.2f} ms")
    print(f"  Sample summary: {res['category_totals']}")
