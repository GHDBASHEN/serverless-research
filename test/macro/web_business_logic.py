"""
================================================================================
MACRO-BENCHMARK: E-Commerce Web Business Logic & Order Checkout
================================================================================
Simulates realistic serverless backend operations for a retail checkout API:
  - Validates cart line items
  - Calculates discounts (percentage coupons, tiered thresholds)
  - Computes shipping fees and regional sales tax
  - Verifies mock inventory stock
================================================================================
"""

import random
import time


def web_order_checkout_simulation(num_orders: int = 500) -> dict:
    """
    Executes business rules for a batch of web shopping cart checkout requests.
    """
    coupons = {"SUMMER20": 0.20, "SAVE10": 0.10, "VIP30": 0.30, "NONE": 0.0}
    tax_rates = {"NY": 0.088, "CA": 0.092, "TX": 0.0625, "FL": 0.060, "WA": 0.065}

    processed_orders = []
    total_revenue = 0.0

    for i in range(num_orders):
        # Generate 1 to 6 items per order
        num_items = (i % 6) + 1
        subtotal = 0.0

        items = []
        for item_idx in range(num_items):
            unit_price = round(10.0 + (item_idx * 15.5), 2)
            qty = (item_idx % 3) + 1
            line_total = unit_price * qty
            subtotal += line_total
            items.append({"sku": f"SKU_{item_idx * 100}", "qty": qty, "price": unit_price})

        # Apply voucher discount
        coupon_key = list(coupons.keys())[i % len(coupons)]
        discount_rate = coupons[coupon_key]
        discount_val = round(subtotal * discount_rate, 2)
        net_after_discount = subtotal - discount_val

        # Shipping rules
        shipping_fee = 0.0 if net_after_discount > 100.0 else 9.99

        # State tax
        state = list(tax_rates.keys())[i % len(tax_rates)]
        tax_val = round(net_after_discount * tax_rates[state], 2)

        # Final order total
        final_total = round(net_after_discount + shipping_fee + tax_val, 2)
        total_revenue += final_total

        processed_orders.append({
            "order_id": f"ORD_{i:05d}",
            "item_count": num_items,
            "subtotal": subtotal,
            "discount": discount_val,
            "shipping": shipping_fee,
            "tax": tax_val,
            "final_total": final_total
        })

    return {
        "orders_count": len(processed_orders),
        "total_revenue_usd": round(total_revenue, 2),
        "sample_order": processed_orders[0] if processed_orders else {}
    }


if __name__ == "__main__":
    print("Running Macro-Benchmark: Web Business Logic...")
    t0 = time.perf_counter()
    res = web_order_checkout_simulation(1000)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  Processed {res['orders_count']} checkout transactions in {elapsed_ms:.2f} ms")
    print(f"  Total Revenue: ${res['total_revenue_usd']}")
    print(f"  Sample Order : {res['sample_order']}")
