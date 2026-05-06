"""
Priya Project - Expanded Intent Classifier Training Script
400+ labelled examples across 4 intent classes
Run from backend/ directory with venv activated:
    python train_intent.py
"""

import pickle
import os
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings("ignore")

DIRECTIONS = [
    "Where is the Ellison Building?",
    "How do I get to City Campus?",
    "Can you give me directions to the library?",
    "I need to find the Student Union",
    "Where is the Northumbria Library?",
    "How do I get to the Sutherland Building?",
    "Where is Coach Lane Campus?",
    "Directions to the Sports Centre please",
    "How do I reach the Pandon Building?",
    "Where is City Campus East?",
    "Can you help me find the Camden Building?",
    "I am looking for the Lipman Building",
    "Where is the Squires Building?",
    "How do I get to the Graduate School?",
    "Where is the Law School?",
    "I need directions to the Engineering block",
    "How do I find Student Services?",
    "Where is the main reception?",
    "Can you tell me how to get to the Sports Centre?",
    "I need to get to the Northumberland Building",
    "Where exactly is the Ellison Building?",
    "How far is City Campus from Coach Lane?",
    "What is the address of the Student Union?",
    "How do I walk to the library from Ellison?",
    "Where is the nearest building to here?",
    "Can you show me how to get to City Campus East?",
    "I am lost, where is the Sutherland Building?",
    "How long does it take to walk to Coach Lane?",
    "What bus stop is nearest to City Campus?",
    "Where is the main campus entrance?",
    "How do I get from Ellison to the Student Union?",
    "Where is the Northumbria University main building?",
    "I need to find the computing department",
    "Where is the business school?",
    "How do I get to the arts building?",
    "Where is the health sciences block?",
    "Can you direct me to the admin office?",
    "Where is the IT helpdesk?",
    "How do I find the careers centre?",
    "Where is the student hub?",
    "I need directions to the postgraduate centre",
    "Where is the international office?",
    "How do I get to the research centre?",
    "Where is the nursing department?",
    "I need to find the psychology building",
    "Where is the social sciences block?",
    "How do I get to the media studio?",
    "Where is the design school?",
    "I need directions to the sports hall",
    "Where is the lecture theatre?",
    "How do I get to the seminar room?",
    "Where is room NB101?",
    "I need to find classroom CCE001",
    "Where is the main hall?",
    "How do I get to the conference centre?",
    "Where is the accommodation office?",
    "I need directions to the finance office",
    "Where is the registrar?",
    "How do I find the examination hall?",
    "Where is the disability support office?",
    "I need to get to the counselling service",
    "Where is the chaplaincy?",
    "How do I reach the alumni office?",
    "Where is the car park entrance?",
    "I need directions to the bike storage",
    "Where is the loading bay?",
    "How do I get to the student common room?",
    "Where is the quiet study area?",
    "I need to find the postroom",
    "Where is the print centre?",
    "How do I get to the language centre?",
    "Where is the music room?",
    "I need directions to the art studio",
    "Where is the electronics lab?",
    "How do I get to the robotics lab?",
    "Where is the anatomy suite?",
    "I need directions to the simulation lab",
    "Where is the nursing skills room?",
    "How do I find the law clinic?",
    "Where is the moot court?",
    "I need to get to the trading room",
    "Where is the finance lab?",
    "How do I reach the geography department?",
    "Where is the history office?",
    "I need directions to the English department",
    "Where is the sociology department?",
    "How do I get to the criminology block?",
    "Where is the journalism studio?",
    "I need directions to the TV studio",
    "Where is the radio studio?",
    "How do I find the photography suite?",
    "Where is the film editing suite?",
    "I need directions to the animation lab",
    "Where is the game design studio?",
    "How do I get to the philosophy room?",
    "Where is the student welfare office?",
    "I need to find the mental health support office",
    "Where is the learning support centre?",
    "How do I get to the library help desk?",
    "Where is the campus security office?",
    "I need directions to the timetabling office",
]

FACILITY_HOURS = [
    "What time does the library close?",
    "Is the gym open on Saturday?",
    "When does the cafe open?",
    "What are the opening hours for the Student Union?",
    "Is the library open on Sunday?",
    "What time does Sport Central close?",
    "Is the canteen open today?",
    "When does the printing room close?",
    "What are the weekend hours for the library?",
    "Is the gym open early in the morning?",
    "What time does Student Services open?",
    "Is the cafe open on Bank Holiday?",
    "When does the Ellison Building close?",
    "What are the opening times for the sports centre?",
    "Is the library open during Christmas?",
    "What time does the Student Union bar close?",
    "Is the canteen open after 5pm?",
    "When does Coach Lane Campus open?",
    "What are the hours for the printing room?",
    "Is the gym open on Sunday morning?",
    "What time does the library open on Monday?",
    "Is the cafe open before 9am?",
    "When does the sports centre open on weekdays?",
    "Is Student Services open in the afternoon?",
    "What are the late night hours for the library?",
    "Is the computer lab open overnight?",
    "When does the Northumberland Building close?",
    "What are the Saturday opening hours for the gym?",
    "Is the prayer room open today?",
    "When does the student lounge close?",
    "What time does City Campus East open?",
    "Is the library open during reading week?",
    "When does the cafe in Ellison close on Friday?",
    "What are the exam period hours for the library?",
    "Is the gym open on public holidays?",
    "When does the Student Union open on weekends?",
    "What time does the canteen close on Thursday?",
    "Is the printing room open on Saturday morning?",
    "When does the library open on Easter Sunday?",
    "What are the summer hours for the sports centre?",
    "Is the cafe open at lunchtime?",
    "When does the student kitchen close?",
    "What are the opening hours for the pharmacy?",
    "Is the medical centre open on weekends?",
    "When does the counselling service open?",
    "What time does the careers centre close?",
    "Is the international office open on Friday afternoon?",
    "When does the accommodation office close?",
    "What are the hours for the finance office?",
    "Is the library open 24 hours during exams?",
    "When does the IT helpdesk close?",
    "What time does the gym close on Christmas Eve?",
    "Is the canteen open during freshers week?",
    "When does the sports centre open on Bank Holiday?",
    "What are the hours for the disability support office?",
    "Is the chaplaincy open at weekends?",
    "When does the language centre close?",
    "What time does the music room open?",
    "Is the art studio open on Sunday?",
    "When does the electronics lab close?",
    "What are the hours for the simulation lab?",
    "Is the nursing skills room open today?",
    "When does the moot court open?",
    "What time does the trading room close?",
    "Is the journalism studio open on weekends?",
    "When does the TV studio close?",
    "What are the hours for the radio studio?",
    "Is the photography suite open on Saturday?",
    "When does the film editing suite close?",
    "What time does the animation lab open?",
    "Is the game design studio open today?",
    "When does the robotics lab close?",
    "What are the opening hours for the anatomy suite?",
    "Is the dark room open this evening?",
    "When does the ceramics workshop close?",
    "What time does the woodwork studio open?",
    "Is the geography field station open today?",
    "When does the history office close?",
    "What are the hours for the English department?",
    "Is the philosophy room open on Friday?",
    "When does the sociology department close?",
    "What time does the criminology block open?",
    "Is the law clinic open this morning?",
    "When does the finance lab close?",
    "What are the hours for the postgraduate centre?",
    "Is the research centre open on weekends?",
    "When does the conference centre close?",
    "What time does the examination hall open?",
    "Is the student common room open late?",
    "When does the quiet study area close?",
    "What are the hours for the print centre?",
    "Is the postroom open on Saturday?",
    "When does the loading bay close?",
    "What time does the alumni office open?",
    "When does the registrar close?",
    "What are the hours for the careers centre?",
    "Is the student hub open on Sunday?",
    "When does the bike storage close?",
    "What time does the car park open?",
    "Is the welfare office open this afternoon?",
    "When does the learning support centre close?",
]

PROXIMITY = [
    "What is nearest to the Ellison Building?",
    "Where is the closest cafe to the library?",
    "What facilities are near City Campus?",
    "What is close to the Student Union?",
    "Where is the nearest ATM?",
    "What is the closest gym to Ellison Building?",
    "Where can I find a printer near here?",
    "What is nearby the Northumberland Building?",
    "Where is the nearest toilet?",
    "What facilities are close to Coach Lane?",
    "Where is the nearest coffee shop?",
    "What is close to City Campus East?",
    "Where is the nearest study room?",
    "What is the closest pharmacy to campus?",
    "Where can I find food near the library?",
    "What is nearby the Sports Centre?",
    "Where is the nearest bus stop?",
    "What facilities are near the Pandon Building?",
    "Where is the closest car park?",
    "What is near the Sutherland Building?",
    "Where is the nearest vending machine?",
    "What is the closest toilet to Ellison?",
    "Where can I find a locker nearby?",
    "What is near City Campus North?",
    "Where is the nearest water fountain?",
    "What facilities are close to the Students Union?",
    "Where is the nearest bike rack?",
    "What is close to the Squires Building?",
    "Where is the nearest first aid room?",
    "What facilities are near the Lipman Building?",
    "Where is the closest restaurant to campus?",
    "What is nearby the Camden Building?",
    "Where is the nearest quiet room?",
    "What is the closest library to Coach Lane?",
    "Where can I find a cash machine nearby?",
    "What is near the Graduate School?",
    "Where is the nearest prayer room?",
    "What facilities are close to City Campus East?",
    "Where is the nearest meditation room?",
    "What is close to the Law School?",
    "Where is the nearest photocopy room?",
    "What is the closest sports facility to here?",
    "Where can I find a quiet study space nearby?",
    "What is near the Northumbria Library?",
    "Where is the nearest student lounge?",
    "What facilities are close to the Ellison Building?",
    "Where is the nearest food outlet?",
    "What is nearby the City Campus Library?",
    "Where is the closest medical centre?",
    "What is near the Engineering block?",
    "Where is the nearest disabled toilet?",
    "What facilities are close to the Pandon Building?",
    "Where is the nearest shower room?",
    "What is the closest student kitchen to here?",
    "Where can I find a phone charging point nearby?",
    "What is near the arts building?",
    "Where is the nearest IT support?",
    "What facilities are close to the health sciences block?",
    "Where is the nearest counselling centre?",
    "What is close to the international office?",
    "Where is the nearest cash point?",
    "What facilities are near the nursing department?",
    "Where is the closest exam hall?",
    "What is nearby the psychology building?",
    "Where is the nearest common room?",
    "What facilities are close to the social sciences block?",
    "Where is the nearest seminar room?",
    "What is the closest lecture theatre to here?",
    "Where can I find a meeting room nearby?",
    "What is near the design school?",
    "Where is the nearest accessible toilet?",
    "What facilities are close to the media studio?",
    "Where is the nearest language lab?",
    "What is close to the journalism studio?",
    "Where is the nearest computer cluster?",
    "What facilities are near the robotics lab?",
    "Where is the closest anatomy suite?",
    "What is near the simulation lab?",
    "Where is the nearest electronics lab?",
    "What facilities are close to the law clinic?",
    "Where is the nearest moot court?",
    "What is the closest trading room to here?",
    "Where can I find a finance terminal nearby?",
    "What is near the conference centre?",
    "Where is the nearest exhibition space?",
    "What facilities are close to the ceramics workshop?",
    "Where is the nearest woodwork studio?",
    "What is close to the photography suite?",
    "Where is the nearest dark room?",
    "What facilities are near the animation lab?",
    "Where is the closest game design studio?",
    "What is near the film editing suite?",
    "Where is the nearest radio studio?",
    "What facilities are close to the TV studio?",
    "Where is the nearest music room?",
    "What is the closest art studio to here?",
    "Where can I find a practice room nearby?",
    "What is near the geography department?",
    "Where is the nearest field station?",
    "What facilities are close to the history office?",
]

EVENTS = [
    "When is the next careers fair?",
    "Is there an open day this month?",
    "When is freshers week?",
    "What events are on today?",
    "Is there a graduation ceremony coming up?",
    "When is the next research seminar?",
    "What is happening at the Student Union tonight?",
    "Is there a job fair on campus?",
    "When is the welcome week?",
    "Are there any workshops today?",
    "When is the next open evening?",
    "What campus events are on this week?",
    "Is there a hackathon coming up?",
    "When is the next pub quiz?",
    "Are there any sports tryouts today?",
    "When is the next student society fair?",
    "Is there a networking event this month?",
    "When is the Christmas party?",
    "Are there any coding bootcamps?",
    "When is the arts exhibition?",
    "Is there a film screening today?",
    "When is the student awards ceremony?",
    "Are there any volunteering events?",
    "When is sports day?",
    "Is there a mental health awareness event?",
    "When is the postgraduate research conference?",
    "Are there any sustainability events on campus?",
    "When is the student union AGM?",
    "Is there a guest lecture this week?",
    "When is the next society recruitment fair?",
    "Are there any international student events?",
    "When is the degree show?",
    "Is there a book fair on campus?",
    "When is the next alumni event?",
    "Are there any career workshops today?",
    "When is the next thesis workshop?",
    "Is there an exam revision session today?",
    "When is the next student council meeting?",
    "Are there any cultural events this week?",
    "When is the international food fair?",
    "Is there a music concert on campus?",
    "When is the poetry reading event?",
    "Are there any art workshops today?",
    "When is the photography exhibition?",
    "Is there a dance showcase this month?",
    "When is the drama performance?",
    "Are there any debate events on campus?",
    "When is the quiz night at the Student Union?",
    "Is there a charity fundraiser today?",
    "When is the next blood donation session?",
    "Are there any religious events on campus?",
    "When is the meditation class?",
    "Is there a yoga session today?",
    "When is the next fitness class at Sport Central?",
    "Are there any swimming lessons this week?",
    "When is the climbing wall open session?",
    "Is there a football match today?",
    "When is the basketball tournament?",
    "Are there any rugby tryouts this week?",
    "When is the tennis tournament?",
    "Is there a badminton session today?",
    "When is the next squash tournament?",
    "Are there any table tennis events?",
    "When is the cycling event?",
    "Is there a running club meeting today?",
    "When is the next triathlon?",
    "Are there any martial arts classes this week?",
    "When is the boxing session?",
    "Is there a swimming gala today?",
    "When is the athletics meeting?",
    "Are there any outdoor adventure events?",
    "When is the orienteering event?",
    "Is there a climbing competition today?",
    "When is the next kayaking session?",
    "Are there any sailing events this month?",
    "When is the next charity run?",
    "Are there any sponsored walks this week?",
    "When is the next community volunteering day?",
    "Is there a litter pick today?",
    "When is the next environmental awareness event?",
    "Are there any recycling drives on campus?",
    "When is the energy awareness week?",
    "Is there a green campus event today?",
    "When is the next sustainability lecture?",
    "Are there any vegan events this week?",
    "When is the next food bank drive?",
    "Is there a clothes swap event today?",
    "When is the next craft fair?",
    "Are there any bake sales on campus?",
    "When is the next quiz fundraiser?",
    "Is there a games night today?",
    "When is the next board games event?",
    "Are there any escape room events this week?",
    "When is the next movie night?",
    "Is there a gaming tournament today?",
    "When is the esports competition?",
    "Are there any virtual reality events on campus?",
    "When is the next tech showcase?",
    "Is there an innovation fair today?",
    "When is the next startup pitch event?",
]

# ─── Build dataset ─────────────────────────────────────────────────────────────

TRAIN_DATA = (
    [(text, "DIRECTIONS")     for text in DIRECTIONS] +
    [(text, "FACILITY_HOURS") for text in FACILITY_HOURS] +
    [(text, "PROXIMITY")      for text in PROXIMITY] +
    [(text, "EVENTS")         for text in EVENTS]
)

print("=" * 60)
print("Priya Intent Classifier - Expanded Training")
print("=" * 60)
print(f"\nTotal examples: {len(TRAIN_DATA)}")
print(f"  DIRECTIONS:     {len(DIRECTIONS)}")
print(f"  FACILITY_HOURS: {len(FACILITY_HOURS)}")
print(f"  PROXIMITY:      {len(PROXIMITY)}")
print(f"  EVENTS:         {len(EVENTS)}")

random.seed(42)
random.shuffle(TRAIN_DATA)

texts  = [t for t, _ in TRAIN_DATA]
labels = [l for _, l in TRAIN_DATA]

# ─── Train ────────────────────────────────────────────────────────────────────

print("\nTraining TF-IDF + Logistic Regression...")
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)
X = vectorizer.fit_transform(texts)

clf = LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", random_state=42)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(clf, X, labels, cv=cv, scoring="f1_macro")
print(f"\n5-Fold CV Macro F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
print(f"Per-fold: {[round(s,3) for s in cv_scores]}")

# ─── Evaluation on held-out test set ─────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42, stratify=labels
)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\nClassification Report (held-out test set):")
print(classification_report(
    y_test, y_pred,
    target_names=["DIRECTIONS", "FACILITY_HOURS", "PROXIMITY", "EVENTS"]
))

print("Confusion Matrix (rows=actual, cols=predicted):")
print("                 DIR   FAC   PRX   EVT")
cm = confusion_matrix(
    y_test, y_pred,
    labels=["DIRECTIONS", "FACILITY_HOURS", "PROXIMITY", "EVENTS"]
)
labels_abbr = ["DIRECTIONS  ", "FACIL_HOURS ", "PROXIMITY   ", "EVENTS      "]
for i, row in enumerate(cm):
    print(f"  {labels_abbr[i]} {list(row)}")

# ─── Final fit on full data and save ─────────────────────────────────────────

print("\nFitting final model on full dataset...")
clf.fit(X, labels)

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open("data/processed/intent_model.pkl", "wb") as f:
    pickle.dump(clf, f)

print("\n" + "=" * 60)
print("SUCCESS - Models saved to data/processed/")
print("=" * 60)