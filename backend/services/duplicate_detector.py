import json
import re
from difflib import SequenceMatcher
from pathlib import Path


# --------------------------------------------------
# 1. NORMALIZE TEXT
# --------------------------------------------------

def normalize_text(value):
    """
    Converts text into a simple comparable format.

    Example:
        "  Lake ROAD " -> "lake road"
    """

    if value is None:
        return ""

    value = str(value).lower().strip()

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value)

    return value


# --------------------------------------------------
# 2. NORMALIZE EMAIL
# --------------------------------------------------

def normalize_email(value):
    """
    Converts an email into a standard format.
    """

    if value is None:
        return ""

    return str(value).lower().strip()


# --------------------------------------------------
# 3. NORMALIZE PHONE
# --------------------------------------------------

def normalize_phone(value):
    """
    Keeps only numbers from a phone number.

    Example:
        "+91 98765-43210"
        becomes
        "919876543210"
    """

    if value is None:
        return ""

    return re.sub(r"\D", "", str(value))


# --------------------------------------------------
# 4. CALCULATE TEXT SIMILARITY
# --------------------------------------------------

def similarity(text1, text2):
    """
    Returns a similarity value between 0 and 1.

    1.0 = exactly the same
    0.0 = completely different
    """

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(None, text1, text2).ratio()


# --------------------------------------------------
# 5. COMPARE TWO CUSTOMERS
# --------------------------------------------------

def compare_customers(customer1, customer2):
    """
    Compares two customer records and calculates
    a deterministic duplicate score.
    """

    score = 0
    evidence = []

    # -----------------------------
    # EMAIL
    # -----------------------------

    email1 = normalize_email(customer1.get("email"))
    email2 = normalize_email(customer2.get("email"))

    if email1 and email2 and email1 == email2:
        score += 40
        evidence.append("Same email")

    # -----------------------------
    # PHONE
    # -----------------------------

    phone1 = normalize_phone(customer1.get("phone"))
    phone2 = normalize_phone(customer2.get("phone"))

    if phone1 and phone2 and phone1 == phone2:
        score += 40
        evidence.append("Same phone")

    # -----------------------------
    # NAME
    # -----------------------------

    name_similarity = similarity(
        customer1.get("name"),
        customer2.get("name")
    )

    if name_similarity >= 0.80:
        score += 10
        evidence.append(
            f"Similar name ({name_similarity:.0%})"
        )

    # -----------------------------
    # ADDRESS
    # -----------------------------

    address_similarity = similarity(
        customer1.get("address"),
        customer2.get("address")
    )

    if address_similarity >= 0.75:
        score += 10
        evidence.append(
            f"Similar address ({address_similarity:.0%})"
        )

    # -----------------------------
    # CITY
    # -----------------------------

    city1 = normalize_text(customer1.get("city"))
    city2 = normalize_text(customer2.get("city"))

    if city1 and city2 and city1 == city2:
        score += 5
        evidence.append("Same city")

    # -----------------------------
    # CONFIDENCE
    # -----------------------------

    if score >= 70:
        confidence = "HIGH"
    elif score >= 40:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "customer_1": customer1.get("customer_id"),
        "customer_2": customer2.get("customer_id"),
        "score": score,
        "confidence": confidence,
        "evidence": evidence
    }


# --------------------------------------------------
# 6. FIND DUPLICATE CANDIDATES
# --------------------------------------------------

def find_duplicate_candidates(customers):
    """
    Compares every customer with every other customer.

    It does not compare a customer with itself.
    """

    candidates = []

    for i in range(len(customers)):

        for j in range(i + 1, len(customers)):

            customer1 = customers[i]
            customer2 = customers[j]

            result = compare_customers(
                customer1,
                customer2
            )

            # Only keep records that have
            # meaningful matching evidence.
            if result["score"] >= 40:
                candidates.append(result)

    return candidates


# --------------------------------------------------
# 7. LOAD CUSTOMER DATA
# --------------------------------------------------

def load_customers(file_path):
    """
    Reads the customers.json file.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# 8. MAIN PROGRAM
# --------------------------------------------------

def main():

    # Find the project root automatically.
    project_root = Path(__file__).resolve().parents[2]

    data_file = project_root / "data" / "customers.json"

    print("=" * 60)
    print("        CLEANMASTER AI - DUPLICATE DETECTOR")
    print("=" * 60)

    print(f"\nReading data from:")
    print(data_file)

    customers = load_customers(data_file)

    print(f"\nCustomers loaded: {len(customers)}")

    candidates = find_duplicate_candidates(customers)

    print(f"Duplicate candidates found: {len(candidates)}")
    output_file = project_root / "data" / "candidate_results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(candidates, file, indent=2)

    print(f"Results saved to: {output_file}")      

    print("\n" + "-" * 60)

    if not candidates:
        print("No duplicate candidates found.")
        return

    for candidate in candidates:

        print(
            f"\n{candidate['customer_1']}  <-->  "
            f"{candidate['customer_2']}"
        )

        print(f"Score: {candidate['score']}")
        print(f"Confidence: {candidate['confidence']}")

        print("Evidence:")

        for evidence in candidate["evidence"]:
            print(f"  - {evidence}")

    print("\n" + "=" * 60)
    print("Duplicate detection completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()