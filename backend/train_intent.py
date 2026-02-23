import pickle
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

TRAINING_DATA = [
    ("Where is the Ellison Building?", 0),
    ("How do I get to the City Campus Library?", 0),
    ("Where can I find the Students Union?", 0),
    ("Navigate me to Sport Central", 0),
    ("I'm looking for the Northumberland Building", 0),
    ("Which way is the Pandon Building?", 0),
    ("Can you direct me to City Campus East?", 0),
    ("Where is the Coach Lane campus?", 0),
    ("How do I get to the library from Ellison?", 0),
    ("I need directions to the sports centre", 0),
    ("Where is the main entrance?", 0),
    ("How do I reach the engineering block?", 0),
    ("Find the nearest lecture hall", 0),
    ("Where is room 001 in the Ellison Building?", 0),
    ("How far is it to Coach Lane?", 0),
    ("Take me to the student support centre", 0),
    ("Where are the computer labs?", 0),
    ("I need to find the careers office", 0),
    ("Where is the international student office?", 0),
    ("Direct me to the nearest printing room", 0),
    ("What time does the library close?", 1),
    ("Is the library open now?", 1),
    ("When does Sport Central open?", 1),
    ("What are the opening hours for the Students Union?", 1),
    ("Is the gym open on Sunday?", 1),
    ("What time does the cafe close?", 1),
    ("When does the library open on Saturday?", 1),
    ("Is the sports centre open today?", 1),
    ("What are the library hours this week?", 1),
    ("Does the student union open on weekends?", 1),
    ("What time does the swimming pool close?", 1),
    ("Is the canteen open right now?", 1),
    ("What are the opening times for the gym?", 1),
    ("When does the IT lab close tonight?", 1),
    ("Is the library open on bank holidays?", 1),
    ("What time does student support close?", 1),
    ("How late is the library open on Friday?", 1),
    ("Are the computer labs open 24 hours?", 1),
    ("When does the printing room open?", 1),
    ("What time does the SU bar close?", 1),
    ("What is near the Ellison Building?", 2),
    ("What cafes are close to the library?", 2),
    ("What is the nearest food place to City Campus East?", 2),
    ("Is there a cafe near the Northumberland Building?", 2),
    ("What facilities are close to Sport Central?", 2),
    ("What is near the Students Union?", 2),
    ("Find me a cafe near the engineering block", 2),
    ("Is there a printer near the library?", 2),
    ("What is nearby the Pandon Building?", 2),
    ("Where can I eat near Ellison?", 2),
    ("Is there a shop near City Campus?", 2),
    ("What study spaces are near the library?", 2),
    ("Find me the nearest ATM to the Students Union", 2),
    ("What is around Coach Lane campus?", 2),
    ("Is there parking near the Northumberland Building?", 2),
    ("What is close to City Campus East?", 2),
    ("Where can I get coffee near the lecture halls?", 2),
    ("Is there a pharmacy near campus?", 2),
    ("What is the closest restaurant to the library?", 2),
    ("Find me somewhere to sit near the SU", 2),
    ("What events are on today?", 3),
    ("Are there any events at the Students Union this week?", 3),
    ("What is happening on campus tomorrow?", 3),
    ("Are there any lectures today?", 3),
    ("What seminars are happening this week?", 3),
    ("Is there an open day coming up?", 3),
    ("What social events are on this weekend?", 3),
    ("Are there any careers events this month?", 3),
    ("What is on at the Ellison Building today?", 3),
    ("Any events at the sports centre this week?", 3),
    ("What is happening at Northumbria this Friday?", 3),
    ("Are there any workshops today?", 3),
    ("What freshers events are on?", 3),
    ("Is there anything happening at City Campus East?", 3),
    ("What research events are scheduled?", 3),
    ("Are there any clubs meeting today?", 3),
    ("What is on at the SU tonight?", 3),
    ("Are there any graduation events this week?", 3),
    ("What sports events are happening this weekend?", 3),
    ("Any academic talks on campus today?", 3),
]

INTENT_LABELS = {0: "DIRECTIONS", 1: "FACILITY_HOURS", 2: "PROXIMITY", 3: "EVENTS"}
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def train():
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42))
    ])

    cv_scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=list(INTENT_LABELS.values())))
    print(confusion_matrix(y_test, y_pred))

    with open(os.path.join(OUTPUT_DIR, "intent_model.pkl"), "wb") as f:
        pickle.dump(pipeline.named_steps["clf"], f)
    with open(os.path.join(OUTPUT_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(pipeline.named_steps["tfidf"], f)

    print(f"Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train()