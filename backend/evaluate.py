"""
Priya Campus Navigation Chatbot - Evaluation Script
Runs NER evaluation and end-to-end system evaluation
Run from backend/ directory with venv activated:
    python evaluate.py
"""

import asyncio
import sys
import json
sys.path.insert(0, '.')

# ─── NER Evaluation ───────────────────────────────────────────────────────────

def evaluate_ner():
    print("=" * 60)
    print("NER MODEL EVALUATION")
    print("=" * 60)

    import spacy
    from pathlib import Path

    model_path = Path("models/ner/model-best")
    if not model_path.exists():
        print("ERROR: NER model not found at models/ner/model-best")
        return

    nlp = spacy.load(str(model_path))

    # Test examples with ground truth entities
    # Format: (text, [(phrase, label), ...])
    TEST_NER = [
        ("Where is the Ellison Building?", [("Ellison Building", "CAMPUS_LOCATION")]),
        ("Is the cafe in Ellison Building open on Saturday?", [("cafe", "FACILITY_TYPE"), ("Ellison Building", "CAMPUS_LOCATION"), ("Saturday", "TIME_REFERENCE")]),
        ("When is the careers fair at the Student Union?", [("careers fair", "EVENT_TYPE"), ("Student Union", "CAMPUS_LOCATION")]),
        ("Is the library open on Sunday?", [("library", "FACILITY_TYPE"), ("Sunday", "TIME_REFERENCE")]),
        ("How do I get to City Campus East?", [("City Campus East", "CAMPUS_LOCATION")]),
        ("Is there a gym near the Northumberland Building?", [("gym", "FACILITY_TYPE"), ("Northumberland Building", "CAMPUS_LOCATION")]),
        ("What time does Sport Central close on Friday?", [("Sport Central", "CAMPUS_LOCATION"), ("Friday", "TIME_REFERENCE")]),
        ("Is there an open day today?", [("open day", "EVENT_TYPE"), ("today", "TIME_REFERENCE")]),
        ("Where is the nearest printer to the Student Union?", [("printer", "FACILITY_TYPE"), ("Student Union", "CAMPUS_LOCATION")]),
        ("Is the canteen open at lunchtime?", [("canteen", "FACILITY_TYPE"), ("lunchtime", "TIME_REFERENCE")]),
        ("When is freshers week?", [("freshers week", "EVENT_TYPE")]),
        ("Where is the Sutherland Building?", [("Sutherland Building", "CAMPUS_LOCATION")]),
        ("Is the gym open on weekends?", [("gym", "FACILITY_TYPE"), ("weekends", "TIME_REFERENCE")]),
        ("Is there a hackathon on campus this weekend?", [("hackathon", "EVENT_TYPE")]),
        ("What are the opening hours for the printing room?", [("printing room", "FACILITY_TYPE")]),
        ("Is the library open during Christmas break?", [("library", "FACILITY_TYPE"), ("Christmas break", "TIME_REFERENCE")]),
        ("Where is the nearest cafe to the Ellison Building?", [("cafe", "FACILITY_TYPE"), ("Ellison Building", "CAMPUS_LOCATION")]),
        ("When is the graduation ceremony?", [("graduation ceremony", "EVENT_TYPE")]),
        ("Is Student Services open on Monday morning?", [("Student Services", "CAMPUS_LOCATION"), ("Monday", "TIME_REFERENCE"), ("morning", "TIME_REFERENCE")]),
        ("Is there a study room in the Lipman Building open late at night?", [("study room", "FACILITY_TYPE"), ("Lipman Building", "CAMPUS_LOCATION"), ("late at night", "TIME_REFERENCE")]),
    ]

    # Count TP, FP, FN per entity type
    from collections import defaultdict
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    print("\nRunning NER evaluation on 20 test examples...\n")

    for text, expected_entities in TEST_NER:
        doc = nlp(text)
        predicted = [(ent.text.lower(), ent.label_) for ent in doc.ents]
        expected = [(phrase.lower(), label) for phrase, label in expected_entities]

        for exp_text, exp_label in expected:
            matched = any(
                exp_text in pred_text or pred_text in exp_text
                for pred_text, pred_label in predicted
                if pred_label == exp_label
            )
            if matched:
                tp[exp_label] += 1
            else:
                fn[exp_label] += 1

        for pred_text, pred_label in predicted:
            matched = any(
                pred_text in exp_text or exp_text in pred_text
                for exp_text, exp_label in expected
                if exp_label == pred_label
            )
            if not matched:
                fp[pred_label] += 1

    # Calculate metrics
    all_labels = ["CAMPUS_LOCATION", "FACILITY_TYPE", "TIME_REFERENCE", "EVENT_TYPE"]
    print(f"{'Entity Type':<20} {'Precision':>10} {'Recall':>10} {'F1':>10} {'TP':>6} {'FP':>6} {'FN':>6}")
    print("-" * 70)

    total_tp = total_fp = total_fn = 0
    results = {}

    for label in all_labels:
        t = tp[label]
        f = fp[label]
        n = fn[label]
        precision = t / (t + f) if (t + f) > 0 else 0
        recall    = t / (t + n) if (t + n) > 0 else 0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        print(f"{label:<20} {precision:>10.3f} {recall:>10.3f} {f1:>10.3f} {t:>6} {f:>6} {n:>6}")
        results[label] = {"precision": precision, "recall": recall, "f1": f1}
        total_tp += t
        total_fp += f
        total_fn += n

    overall_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = 2 * overall_p * overall_r / (overall_p + overall_r) if (overall_p + overall_r) > 0 else 0
    print("-" * 70)
    print(f"{'OVERALL':<20} {overall_p:>10.3f} {overall_r:>10.3f} {overall_f1:>10.3f}")

    return results, overall_f1


# ─── End-to-End Evaluation ────────────────────────────────────────────────────

async def evaluate_end_to_end():
    print("\n" + "=" * 60)
    print("END-TO-END SYSTEM EVALUATION")
    print("=" * 60)

    import httpx

    # 40 test queries with expected intent and expected response keywords
    TEST_QUERIES = [
        # DIRECTIONS (10)
        {"query": "Where is the Ellison Building?", "intent": "DIRECTIONS", "expect": ["Ellison", "Ellison Place"]},
        {"query": "How do I get to the Student Union?", "intent": "DIRECTIONS", "expect": ["Students' Union", "Sandyford"]},
        {"query": "Where is City Campus East?", "intent": "DIRECTIONS", "expect": ["City Campus East", "Sandyford"]},
        {"query": "Directions to the Northumberland Building please", "intent": "DIRECTIONS", "expect": ["Northumberland", "Northumberland Road"]},
        {"query": "Where is Coach Lane Campus?", "intent": "DIRECTIONS", "expect": ["Coach Lane", "Benton"]},
        {"query": "How do I get to Sport Central?", "intent": "DIRECTIONS", "expect": ["Sport Central", "Northumberland"]},
        {"query": "Where is the Pandon Building?", "intent": "DIRECTIONS", "expect": ["Pandon"]},
        {"query": "I need to find the City Campus Library", "intent": "DIRECTIONS", "expect": ["Library", "Sandyford"]},
        {"query": "Where is the Students Union?", "intent": "DIRECTIONS", "expect": ["Union", "Sandyford"]},
        {"query": "Can you help me find the Northumberland Building?", "intent": "DIRECTIONS", "expect": ["Northumberland"]},

        # FACILITY_HOURS (10)
        {"query": "Is the library open on Saturday?", "intent": "FACILITY_HOURS", "expect": ["10:00am", "6:00pm"]},
        {"query": "What time does the gym close?", "intent": "FACILITY_HOURS", "expect": ["Sport Central", "10:00pm"]},
        {"query": "Is the cafe open on Sunday?", "intent": "FACILITY_HOURS", "expect": ["Closed", "Campus Cafe"]},
        {"query": "What are the opening hours for the Student Union?", "intent": "FACILITY_HOURS", "expect": ["Students' Union", "9:00am"]},
        {"query": "Is the printing room open on Saturday?", "intent": "FACILITY_HOURS", "expect": ["Printing Room", "10:00am"]},
        {"query": "What time does Sport Central open on Monday?", "intent": "FACILITY_HOURS", "expect": ["6:30am"]},
        {"query": "Is Student Services open on Saturday?", "intent": "FACILITY_HOURS", "expect": ["Student Services", "Closed"]},
        {"query": "What are the weekend hours for the library?", "intent": "FACILITY_HOURS", "expect": ["Saturday", "Sunday"]},
        {"query": "Is the gym open on Sunday?", "intent": "FACILITY_HOURS", "expect": ["9:00am", "7:00pm"]},
        {"query": "When does the Ellison Building close on Friday?", "intent": "FACILITY_HOURS", "expect": ["Ellison", "9:00pm"]},

        # PROXIMITY (10)
        {"query": "What is nearest to the Ellison Building?", "intent": "PROXIMITY", "expect": ["Library", "Northumberland", "Sport Central"]},
        {"query": "What facilities are near the Northumberland Building?", "intent": "PROXIMITY", "expect": ["Union", "Ellison", "Library"]},
        {"query": "What is close to City Campus Library?", "intent": "PROXIMITY", "expect": ["Ellison", "Northumberland", "Union"]},
        {"query": "Where is the nearest cafe?", "intent": "PROXIMITY", "expect": ["cafe", "Ellison", "Union"]},
        {"query": "What is nearby the Student Union?", "intent": "PROXIMITY", "expect": ["Ellison", "Library"]},
        {"query": "Where can I find a printer near Ellison?", "intent": "PROXIMITY", "expect": ["Library", "Northumberland"]},
        {"query": "What is the closest facility to the Northumberland Building?", "intent": "PROXIMITY", "expect": ["Union", "Ellison"]},
        {"query": "Where is the nearest gym?", "intent": "PROXIMITY", "expect": ["Sport Central", "gym", "cafe"]},
        {"query": "What is near City Campus East?", "intent": "PROXIMITY", "expect": ["campus", "northumbria"]},
        {"query": "Where is the nearest study room?", "intent": "PROXIMITY", "expect": ["Library", "campus", "cafe"]},

        # EVENTS (10)
        {"query": "Is there an open day today?", "intent": "EVENTS", "expect": ["Open Day", "10:00am", "Ellison"]},
        {"query": "What events are on today?", "intent": "EVENTS", "expect": ["Open Day", "Seminar", "Careers"]},
        {"query": "Is there a careers workshop today?", "intent": "EVENTS", "expect": ["Careers Workshop", "3:00pm"]},
        {"query": "Is there a research seminar today?", "intent": "EVENTS", "expect": ["AI Research Seminar", "2:00pm"]},
        {"query": "When is the freshers fair?", "intent": "EVENTS", "expect": ["Freshers Fair", "tomorrow"]},
        {"query": "What is happening at the Student Union?", "intent": "EVENTS", "expect": ["today", "tomorrow", "event"]},
        {"query": "Is there a seminar on campus today?", "intent": "EVENTS", "expect": ["Seminar", "2:00pm"]},
        {"query": "What campus events are on this week?", "intent": "EVENTS", "expect": ["Open Day", "Seminar", "Careers"]},
        {"query": "Is there an open day this month?", "intent": "EVENTS", "expect": ["Open Day", "Ellison"]},
        {"query": "When is the next careers event?", "intent": "EVENTS", "expect": ["Careers", "today", "tomorrow"]},
    ]

    print(f"\nRunning {len(TEST_QUERIES)} test queries against live API...\n")
    print(f"{'#':<4} {'Intent':<16} {'Result':<12} Query")
    print("-" * 80)

    results = {"correct": 0, "partial": 0, "incorrect": 0, "by_intent": {}}
    for intent in ["DIRECTIONS", "FACILITY_HOURS", "PROXIMITY", "EVENTS"]:
        results["by_intent"][intent] = {"correct": 0, "partial": 0, "incorrect": 0}

    async with httpx.AsyncClient() as client:
        for i, test in enumerate(TEST_QUERIES, 1):
            try:
                response = await client.post(
                    "http://127.0.0.1:8000/api/v1/query",
                    json={"query": test["query"]},
                    timeout=10.0
                )
                data = response.json()
                response_text = data.get("response", "").lower()
                predicted_intent = data.get("intent", {}).get("intent", "")

                # Check how many expected keywords appear in response
                matched = sum(1 for kw in test["expect"] if kw.lower() in response_text)
                total = len(test["expect"])

                if matched == total:
                    status = "CORRECT"
                    results["correct"] += 1
                    results["by_intent"][test["intent"]]["correct"] += 1
                elif matched > 0:
                    status = "PARTIAL"
                    results["partial"] += 1
                    results["by_intent"][test["intent"]]["partial"] += 1
                else:
                    status = "INCORRECT"
                    results["incorrect"] += 1
                    results["by_intent"][test["intent"]]["incorrect"] += 1

                print(f"{i:<4} {test['intent']:<16} {status:<12} {test['query'][:50]}")

            except Exception as e:
                print(f"{i:<4} {test['intent']:<16} {'ERROR':<12} {test['query'][:50]} -- {e}")
                results["incorrect"] += 1
                results["by_intent"][test["intent"]]["incorrect"] += 1

    # Summary
    total = len(TEST_QUERIES)
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nOverall: {results['correct']}/{total} correct ({results['correct']/total*100:.1f}%)")
    print(f"Partial: {results['partial']}/{total} ({results['partial']/total*100:.1f}%)")
    print(f"Incorrect: {results['incorrect']}/{total} ({results['incorrect']/total*100:.1f}%)")

    print(f"\n{'Intent':<16} {'Correct':>8} {'Partial':>8} {'Incorrect':>10} {'Accuracy':>10}")
    print("-" * 55)
    for intent, counts in results["by_intent"].items():
        acc = counts["correct"] / 10 * 100
        print(f"{intent:<16} {counts['correct']:>8} {counts['partial']:>8} {counts['incorrect']:>10} {acc:>9.0f}%")

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nPRIYA CAMPUS NAVIGATION CHATBOT - FULL EVALUATION")
    print("=" * 60)
    print("Make sure the server is running: uvicorn app.main:app --reload")
    print("=" * 60)

    # NER Evaluation
    ner_results = evaluate_ner()

    # End-to-end
    asyncio.run(evaluate_end_to_end())

    print("\nEvaluation complete.")