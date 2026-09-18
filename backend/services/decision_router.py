from pathlib import Path
import json


def route_candidate(candidate):
    """
    Decides what should happen next to a duplicate candidate.

    HIGH confidence:
        Send toward merge decision.

    MEDIUM confidence:
        Send to AI investigation.

    LOW confidence:
        Preserve separately.
    """

    score = candidate["score"]
    confidence = candidate["confidence"]
    evidence = candidate["evidence"]

    # Check whether important conflicting evidence exists.
    has_conflict = any(
        "Different" in item or
        "Conflict" in item
        for item in evidence
    )

    # Conflicting evidence must be handled conservatively.
    if has_conflict:
        return {
            **candidate,
            "next_action": "FLAG_FOR_REVIEW",
            "reason": "Conflicting evidence detected."
        }

    if confidence == "HIGH":
        return {
            **candidate,
            "next_action": "MERGE_CANDIDATE",
            "reason": "Strong matching evidence detected."
        }

    if confidence == "MEDIUM":
        return {
            **candidate,
            "next_action": "AI_INVESTIGATION",
            "reason": "Evidence is ambiguous and requires investigation."
        }

    return {
        **candidate,
        "next_action": "PRESERVE_SEPARATELY",
        "reason": "Insufficient evidence for duplicate detection."
    }


def main():

    project_root = Path(__file__).resolve().parents[2]

    input_file = project_root / "data" / "candidate_results.json"
    output_file = project_root / "data" / "decision_results.json"

    with open(input_file, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    decisions = []

    for candidate in candidates:
        decision = route_candidate(candidate)
        decisions.append(decision)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(decisions, file, indent=2)

    print("=" * 60)
    print("        CLEANMASTER AI - DECISION ROUTER")
    print("=" * 60)

    print(f"\nCandidates received: {len(candidates)}")
    print(f"Results saved to: {output_file}")

    print("\nDECISIONS")
    print("-" * 60)

    for decision in decisions:

        print(
            f"\n{decision['customer_1']} "
            f"<--> "
            f"{decision['customer_2']}"
        )

        print(f"Score: {decision['score']}")
        print(f"Confidence: {decision['confidence']}")
        print(f"Next action: {decision['next_action']}")
        print(f"Reason: {decision['reason']}")

    print("\n" + "=" * 60)
    print("Decision routing completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()