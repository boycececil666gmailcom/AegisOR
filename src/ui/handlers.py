from src.assembly_service import SPECIALTY_PRESETS, AssemblyAIService
from src.engine import UniversalProtocolEngine
from src.models import Utterance
from src.samples import (
    DEFAULT_INTRAOP_ENTITIES,
    DEFAULT_INTRAOP_UTTERANCES,
    DEFAULT_POSTOP_CHAPTERS,
    DEFAULT_POSTOP_ENTITIES,
    DEFAULT_POSTOP_SUMMARY,
    SAMPLE_POSTOP_TEXT,
    SAMPLE_TIMEOUT_TEXT,
    get_default_timeout_utterances,
)

# region Service Instances
assembly_service = AssemblyAIService()
engine = UniversalProtocolEngine()
# endregion


# region Event Handlers
def handle_timeout(
    audio_file: str | None,
    transcript_override: str | None = None,
    audio_url: str | None = None,
) -> tuple[str, str, str]:
    print("[UI-handle_timeout] Invoked Time-Out evaluation")
    target_source = audio_file or (audio_url.strip() if audio_url else None)

    if target_source:
        res = assembly_service.transcribe(
            audio_source=target_source,
            generative_mode="None",
            enable_diarization=True,
            enable_entities=True,
        )
        if res.get("error"):
            return f"Error: {res['error']}", "", ""
        transcript_text = res["transcript_text"]
        utterances = res["utterances"]
    else:
        transcript_text = (
            transcript_override.strip() if transcript_override else SAMPLE_TIMEOUT_TEXT
        )
        utterances = get_default_timeout_utterances(transcript_text)

    checklist = engine.evaluate_timeout(transcript_text, utterances)

    # Status Banner
    if checklist.incision_authorized:
        status_banner = "### STATUS: INCISION AUTHORIZED\nAll mandatory Universal Protocol safety checks and multidisciplinary verbal agreements have been verified."
    else:
        status_banner = "### STATUS: SURGICAL HOLD / INCOMPLETE TIME-OUT\nMandatory safety checklist items or oral role confirmations are pending. Do NOT initiate incision."

    # Checklist Markdown Table
    table_lines = [
        "| Safety Verification Item | Verification Status | Clinical Evidence / Role Attribution |",
        "| :--- | :--- | :--- |",
    ]
    for item in checklist.items:
        status_label = "VERIFIED" if item.verified else "PENDING"
        details = item.details or (
            "Verbally confirmed" if item.verified else "Not detected in audio stream"
        )
        table_lines.append(f"| {item.label} | **{status_label}** | {details} |")

    checklist_markdown = "\n".join(table_lines)

    # Diarization log
    if utterances:
        diar_lines = [
            f"**[Speaker {u.speaker}]** ({u.start_sec:.1f}s - {u.end_sec:.1f}s): {u.text}"
            for u in utterances
        ]
        diar_log = "\n\n".join(diar_lines)
    else:
        diar_log = transcript_text

    return status_banner, checklist_markdown, diar_log


def handle_intraop(
    audio_file: str | None,
    transcript_override: str | None = None,
    audio_url: str | None = None,
) -> tuple[list[list[str]], str, str]:
    print("[UI-handle_intraop] Invoked Closed-Loop tracking")
    target_source = audio_file or (audio_url.strip() if audio_url else None)

    if target_source:
        res = assembly_service.transcribe(
            audio_source=target_source,
            generative_mode="None",
            enable_diarization=True,
            enable_entities=True,
        )
        if res.get("error"):
            return [], f"Error: {res['error']}", ""
        utterances = res["utterances"]
        entities = res["entities"]
    else:
        utterances = DEFAULT_INTRAOP_UTTERANCES
        entities = DEFAULT_INTRAOP_ENTITIES

    orders = engine.match_closed_loop_orders(utterances)
    rows = [order.to_row() for order in orders]

    if entities:
        ent_lines = [f"- **{e['text']}** ({e['entity_type']})" for e in entities]
        ent_markdown = "\n".join(ent_lines)
    else:
        ent_markdown = "No clinical entities identified."

    summary = f"Total Orders Detected: {len(orders)} | Closed-Loop Confirmations: {sum(1 for o in orders if o.verified)}"
    return rows, summary, ent_markdown


def handle_postop(
    audio_file: str | None,
    transcript_override: str | None = None,
    audio_url: str | None = None,
) -> str:
    print("[UI-handle_postop] Invoked Post-Op Sign-Out compilation")
    target_source = audio_file or (audio_url.strip() if audio_url else None)

    if target_source:
        res = assembly_service.transcribe(
            audio_source=target_source,
            generative_mode="Summarization",
            enable_diarization=True,
            enable_entities=True,
        )
        if res.get("error"):
            return f"Error: {res['error']}"
        transcript_text = res["transcript_text"]
        summary_text = res["summary"]
        chapters = res["chapters"]
        entities = res["entities"]
        utterances = res["utterances"]
    else:
        transcript_text = (
            transcript_override.strip() if transcript_override else SAMPLE_POSTOP_TEXT
        )
        summary_text = DEFAULT_POSTOP_SUMMARY
        chapters = DEFAULT_POSTOP_CHAPTERS
        entities = DEFAULT_POSTOP_ENTITIES
        utterances = [
            Utterance(speaker="1", start_sec=0.0, end_sec=10.0, text=transcript_text)
        ]

    checklist = engine.evaluate_timeout(transcript_text, utterances)
    orders = engine.match_closed_loop_orders(utterances)
    report = engine.generate_operative_report(
        checklist=checklist,
        orders=orders,
        transcript_text=transcript_text,
        summary_text=summary_text,
        chapters=chapters,
        entities=entities,
    )
    return engine.format_report_markdown(report)


def handle_apply_preset(specialty: str) -> str:
    print(f"[UI-handle_apply_preset] Selected specialty preset: {specialty}")
    terms = SPECIALTY_PRESETS.get(specialty, [])
    return ", ".join(terms)


def handle_save_vocabulary(words_text: str, guidelines_text: str) -> tuple[str, str]:
    print(
        "[UI-handle_save_vocabulary] Saving custom vocabulary and procedural guidelines"
    )
    words = [w.strip() for w in words_text.replace("\n", ",").split(",") if w.strip()]
    assembly_service.set_custom_vocabulary(words)
    assembly_service.set_procedure_guidelines(guidelines_text)
    active = assembly_service.get_active_vocabulary()
    status_msg = f"### STATUS: AI CONTEXT & LEXICON UPDATED\nConfigured {len(words)} custom words. Total active boost vocabulary: {len(active)} terms."
    formatted_words = ", ".join([f"`{w}`" for w in active])
    preview_md = f"**Total Active Boosted Terms ({len(active)}):**\n\n{formatted_words}"
    return status_msg, preview_md


def handle_reset_vocabulary() -> tuple[str, str, str, str]:
    print("[UI-handle_reset_vocabulary] Resetting vocabulary to surgical baseline")
    assembly_service.clear_custom_vocabulary()
    assembly_service.set_procedure_guidelines("")
    active = assembly_service.get_active_vocabulary()
    status_msg = "### STATUS: RESET TO BASELINE\nCustom vocabulary and guidelines cleared. Default surgical baseline active."
    formatted_words = ", ".join([f"`{w}`" for w in active])
    preview_md = f"**Total Active Boosted Terms ({len(active)}):**\n\n{formatted_words}"
    return "", "", status_msg, preview_md


# endregion
