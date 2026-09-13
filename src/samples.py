from src.models import Utterance

# region Sample Clinical Transcripts
SAMPLE_TIMEOUT_TEXT = (
    "Attention operating room team, commencing Universal Protocol Time-Out. "
    "Patient is Jane Doe, MRN 98214, date of birth June 4 1985. "
    "The planned procedure is laparoscopic cholecystectomy. "
    "Operative site is right upper quadrant, surgical marking verified by surgeon. "
    "Informed consent is signed and in the electronic chart. "
    "Allergies: no known drug allergies, airway assessed and secure. "
    "Antibiotic prophylaxis: cefazolin 2 grams IV was fully infused 25 minutes ago. "
    "Diagnostic CT imaging is displayed on monitor. "
    "Dr. Davis: Anesthesia, do you agree? "
    "Anesthesia confirms and agrees. "
    "Nursing team confirms, all agree, Time-Out complete."
)

SAMPLE_INTRAOP_TEXT = (
    "Dr. Davis: Please push 5000 units Heparin intravenously now. "
    "Nurse Sarah: Heparin 5000 units IV pushed and confirmed. "
    "Dr. Davis: Administer 100 mcg fentanyl for patient comfort. "
    "Nurse Sarah: Fentanyl 100 mcg administered and charted. "
    "Dr. Davis: Pass laparoscopic clip applier. "
    "Scrub Tech: Clip applier passed."
)

SAMPLE_POSTOP_TEXT = (
    "Commencing surgical sign-out. Procedure completed: Laparoscopic cholecystectomy with critical view of safety verified. "
    "Sponge, needle, and instrument counts are verified and correct. "
    "Gallbladder specimen labeled for pathology examination. "
    "Estimated blood loss 20 ml. Patient vitals stable, reversing neuromuscular blockade, transferring to PACU."
)
# endregion


# region Fallback Mock Data
def get_default_timeout_utterances(transcript_text: str) -> list[Utterance]:
    return [
        Utterance(speaker="1", start_sec=0.0, end_sec=15.0, text=transcript_text),
        Utterance(
            speaker="2",
            start_sec=15.5,
            end_sec=17.0,
            text="Anesthesia confirms and agrees.",
        ),
        Utterance(
            speaker="3",
            start_sec=17.2,
            end_sec=19.0,
            text="Nursing team confirms, all agree.",
        ),
    ]


DEFAULT_INTRAOP_UTTERANCES: list[Utterance] = [
    Utterance(
        speaker="1",
        start_sec=20.0,
        end_sec=23.0,
        text="Please push 5000 units Heparin intravenously now.",
    ),
    Utterance(
        speaker="2",
        start_sec=24.0,
        end_sec=26.5,
        text="Heparin 5000 units IV pushed and confirmed.",
    ),
    Utterance(
        speaker="1",
        start_sec=45.0,
        end_sec=48.0,
        text="Administer 100 mcg fentanyl for patient comfort.",
    ),
    Utterance(
        speaker="2",
        start_sec=49.0,
        end_sec=51.0,
        text="Fentanyl 100 mcg administered and charted.",
    ),
    Utterance(
        speaker="1",
        start_sec=70.0,
        end_sec=72.0,
        text="Pass laparoscopic clip applier.",
    ),
    Utterance(speaker="3", start_sec=73.0, end_sec=75.0, text="Clip applier passed."),
]

DEFAULT_INTRAOP_ENTITIES: list[dict[str, str]] = [
    {"text": "Heparin", "entity_type": "medication"},
    {"text": "5000 units", "entity_type": "dosage"},
    {"text": "Fentanyl", "entity_type": "medication"},
    {"text": "100 mcg", "entity_type": "dosage"},
    {"text": "Laparoscopic clip applier", "entity_type": "surgical_instrument"},
]

DEFAULT_POSTOP_SUMMARY: str = (
    "- Laparoscopic cholecystectomy successfully concluded.\n"
    "- Sponge, needle, and instrument counts verified correct by nursing.\n"
    "- Gallbladder specimen labeled and dispatched for pathology.\n"
    "- Patient stable and transferred to recovery."
)

DEFAULT_POSTOP_CHAPTERS: list[dict[str, str]] = [
    {
        "headline": "Incision & Access",
        "summary": "Pneumoperitoneum established with 10mm umbilical trocar.",
    },
    {
        "headline": "Dissection & Ligation",
        "summary": "Cystic duct and artery identified, clipped, and divided.",
    },
    {
        "headline": "Closure & Sign-Out",
        "summary": "Instrument counts reconciled; trocar sites closed in layers.",
    },
]

DEFAULT_POSTOP_ENTITIES: list[dict[str, str]] = [
    {"text": "Cholecystectomy", "entity_type": "medical_procedure"},
    {"text": "Gallbladder", "entity_type": "anatomy"},
]
# endregion
