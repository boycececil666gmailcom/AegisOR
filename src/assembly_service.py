import os
from typing import Any

import assemblyai as aai
from dotenv import load_dotenv

from src.models import Utterance

# region Surgical Lexicon
SURGICAL_WORD_BOOST = [
    "Time-Out",
    "Universal Protocol",
    "cholecystectomy",
    "laparoscopic",
    "heparin",
    "cefazolin",
    "Ancef",
    "Calot's triangle",
    "cystic duct",
    "cystic artery",
    "trocar",
    "hemostasis",
    "ligation",
    "gallbladder",
    "suction irrigation",
    "NKDA",
    "endotracheal",
    "Marcaine",
    "bupivacaine",
    "propofol",
    "fentanyl",
    "read-back",
    "sponge count",
    "needle count",
    "incision",
    "attending surgeon",
    "anesthesiologist",
    "circulating nurse",
]

SPECIALTY_PRESETS: dict[str, list[str]] = {
    "General Surgery (Laparoscopy)": [
        "cholecystectomy",
        "laparoscopic",
        "trocar",
        "Calot's triangle",
        "cystic duct",
        "cystic artery",
        "gallbladder",
        "suction irrigation",
        "Pneumoperitoneum",
        "Veress needle",
    ],
    "Orthopedic Surgery (Arthroplasty)": [
        "arthroplasty",
        "arthroscopy",
        "femoral stem",
        "acetabular cup",
        "tourniquet",
        "bone cement",
        "oscillating saw",
        "tranexamic acid",
        "prosthesis",
        "polyethylene liner",
    ],
    "Cardiovascular Surgery": [
        "sternotomy",
        "cardiopulmonary bypass",
        "cannulation",
        "aortic cross-clamp",
        "protamine",
        "cardioplegia",
        "heparin",
        "saphenous vein graft",
        "internal mammary artery",
    ],
    "Neurosurgery & Spine": [
        "craniotomy",
        "dura mater",
        "bipolar cautery",
        "microdissector",
        "mannitol",
        "intracranial pressure",
        "dural closure",
        "stereotactic",
        "laminectomy",
    ],
}
# endregion


# region AssemblyAI Service
class AssemblyAIService:
    def __init__(self, api_key: str | None = None) -> None:
        load_dotenv()
        self.api_key = api_key or os.getenv("assembly_ai_api")
        self.custom_vocabulary: list[str] = []
        self.procedure_guidelines: str = ""
        if self.api_key:
            aai.settings.api_key = self.api_key
            print("[AssemblyAIService-__init__] Configured AssemblyAI API key")
        else:
            print("[AssemblyAIService-__init__] Warning: assembly_ai_api not found in environment")

    def set_custom_vocabulary(self, words: list[str]) -> list[str]:
        self.custom_vocabulary = sorted({w.strip() for w in words if w.strip()})
        print(f"[AssemblyAIService-set_custom_vocabulary] Updated custom terms: {len(self.custom_vocabulary)}")
        return self.get_active_vocabulary()

    def add_vocabulary_words(self, words: list[str]) -> list[str]:
        current = set(self.custom_vocabulary) | {w.strip() for w in words if w.strip()}
        self.custom_vocabulary = sorted(current)
        print(f"[AssemblyAIService-add_vocabulary_words] Active terms: {len(self.custom_vocabulary)}")
        return self.get_active_vocabulary()

    def get_active_vocabulary(self) -> list[str]:
        return sorted(set(SURGICAL_WORD_BOOST + self.custom_vocabulary))

    def clear_custom_vocabulary(self) -> list[str]:
        self.custom_vocabulary = []
        print("[AssemblyAIService-clear_custom_vocabulary] Reset custom vocabulary")
        return self.get_active_vocabulary()

    def set_procedure_guidelines(self, guidelines: str) -> None:
        self.procedure_guidelines = guidelines.strip()
        print(f"[AssemblyAIService-set_procedure_guidelines] Set guideline: {self.procedure_guidelines[:40]}...")

    def transcribe(
        self,
        audio_source: str,
        generative_mode: str = "Summarization",
        enable_diarization: bool = True,
        enable_entities: bool = True,
        custom_boost_words: list[str] | None = None,
    ) -> dict[str, Any]:
        print(f"[AssemblyAIService-transcribe] Ingesting audio source: {audio_source}")
        words = list(set(self.get_active_vocabulary() + (custom_boost_words or [])))

        config_kwargs: dict[str, Any] = {
            "word_boost": words,
            "boost_param": "high",
            "speaker_labels": enable_diarization,
            "entity_detection": enable_entities,
        }
        if generative_mode == "Summarization":
            config_kwargs["summarization"] = True
            config_kwargs["summary_model"] = aai.SummarizationModel.informative
            config_kwargs["summary_type"] = aai.SummarizationType.bullets
        elif generative_mode == "Auto Chapters":
            config_kwargs["auto_chapters"] = True

        try:
            transcript = aai.Transcriber().transcribe(
                audio_source,
                config=aai.TranscriptionConfig(**config_kwargs),
            )
            if transcript.status == aai.TranscriptStatus.error:
                raise RuntimeError(transcript.error)

            utterances = [
                Utterance(speaker=str(u.speaker), start_sec=u.start / 1000.0, end_sec=u.end / 1000.0, text=u.text)
                for u in (transcript.utterances or [])
            ]
            chapters = [
                {"start_sec": ch.start / 1000.0, "end_sec": ch.end / 1000.0, "headline": ch.headline, "gist": ch.gist, "summary": ch.summary}
                for ch in (transcript.chapters or [])
            ]
            entities = [
                {"text": ent.text, "entity_type": ent.entity_type}
                for ent in (transcript.entities or [])
            ]

            print(f"[AssemblyAIService-transcribe] Processed {len(utterances)} utterances")
            return {
                "transcript_text": transcript.text or "",
                "utterances": utterances,
                "summary": transcript.summary or "",
                "chapters": chapters,
                "entities": entities,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            print(f"[AssemblyAIService-transcribe] Transcription failed: {exc}")
            return {
                "transcript_text": "",
                "utterances": [],
                "summary": "",
                "chapters": [],
                "entities": [],
                "error": str(exc),
            }
# endregion
