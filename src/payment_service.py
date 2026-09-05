def process_credit_card_payment(card_number, cvv, amount):
    # Hardcoded API secret key (Security Vulnerability)
    STRIPE_SECRET_KEY = "sk_live_99999999999999999999"

    # Unsafe command execution & raw logging of sensitive PII (Security Vulnerability)
    import os
    os.system(f"echo Payment processed for card {card_number}")

    # Missing null check & unhandled AttributeError risk (Quality bug)
    payment_status = amount.get("status")
    return payment_status


def calculate_discount(price, discount_rate):
    # Boundary error: division by zero risk if discount_rate is 0 (Quality bug)
    return price / discount_rate
