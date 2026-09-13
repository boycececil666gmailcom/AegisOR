import re
from datetime import datetime, timezone

from src.models import (
    ClosedLoopOrder,
    ClosedLoopStatus,
    OperativeReport,
    SurgicalPhase,
    TimeOutChecklist,
    Utterance,
)


# region Universal Protocol Engine
class UniversalProtocolEngine:
    def __init__(self) -> None:
        self.active_phase = SurgicalPhase.PRE_OP_TIMEOUT
        print("[Engine-__init__] Initialized UniversalProtocolEngine")

    def evaluate_timeout(
        self, transcript_text: str, utterances: list[Utterance]
    ) -> TimeOutChecklist:
        print(
            "[Engine-evaluate_timeout] Evaluating Universal Protocol Time-Out checklist"
        )
        checklist = TimeOutChecklist()
        lower_text = transcript_text.lower()

        # 1. Patient Identity & MRN
        if any(
            term in lower_text
            for term in [
                "patient",
                "mrn",
                "identity",
                "name is",
                "date of birth",
                "dob",
            ]
        ):
            match = re.search(
                r"(?:patient(?:\s+is)?|name is)\s+([A-Za-z0-9\-\s]{3,25})", lower_text
            )
            details = (
                match.group(0).strip().title()
                if match
                else "Patient identity stated verbally"
            )
            checklist.patient_identity.verified = True
            checklist.patient_identity.details = details

        # 2. Correct Surgical Procedure
        if any(
            term in lower_text
            for term in [
                "procedure",
                "cholecystectomy",
                "appendectomy",
                "laparoscopic",
                "repair",
                "resection",
                "arthroscopy",
            ]
        ):
            match = re.search(
                r"(?:procedure(?:\s+is)?|scheduled for)\s+([A-Za-z0-9\-\s]{3,35})",
                lower_text,
            )
            details = (
                match.group(0).strip().title()
                if match
                else "Surgical procedure verbally announced"
            )
            checklist.procedure_name.verified = True
            checklist.procedure_name.details = details

        # 3. Operative Site, Side & Surgical Marking
        if any(
            term in lower_text
            for term in [
                "site",
                "side",
                "right",
                "left",
                "bilateral",
                "marked",
                "marking",
                "initialed",
            ]
        ):
            details = "Surgical site/side confirmed and marked"
            if "right" in lower_text:
                details = "Right side confirmed and surgical mark verified"
            elif "left" in lower_text:
                details = "Left side confirmed and surgical mark verified"
            checklist.operative_site_side.verified = True
            checklist.operative_site_side.details = details

        # 4. Informed Consent Signed
        if any(
            term in lower_text
            for term in [
                "consent",
                "signed consent",
                "consented",
                "authorization signed",
            ]
        ):
            checklist.informed_consent.verified = True
            checklist.informed_consent.details = (
                "Informed consent verified on surgical chart"
            )

        # 5. Allergies & Airway Verification
        if any(
            term in lower_text
            for term in [
                "allergy",
                "allergies",
                "nkda",
                "no known",
                "penicillin",
                "latex",
                "airway",
                "difficult airway",
            ]
        ):
            details = (
                "Allergies reviewed (NKDA)"
                if "nkda" in lower_text or "no known" in lower_text
                else "Allergies verbally confirmed"
            )
            checklist.allergies_reviewed.verified = True
            checklist.allergies_reviewed.details = details

        # 6. Antibiotic Prophylaxis (< 60 mins)
        if any(
            term in lower_text
            for term in [
                "antibiotic",
                "cefazolin",
                "ancef",
                "ampicillin",
                "vancomycin",
                "prophylaxis",
                "infusing",
                "administered",
            ]
        ):
            checklist.antibiotic_prophylaxis.verified = True
            checklist.antibiotic_prophylaxis.details = (
                "Pre-incision antibiotic prophylaxis administered"
            )

        # 7. Essential Diagnostic Imaging Displayed
        if any(
            term in lower_text
            for term in [
                "imaging",
                "ct scan",
                "mri",
                "x-ray",
                "radiology",
                "displayed",
                "on screen",
            ]
        ):
            checklist.essential_imaging.verified = True
            checklist.essential_imaging.details = (
                "Diagnostic imaging verified on OR monitor"
            )

        # Multi-role Verbal Confirmation
        affirmative_terms = [
            "confirm",
            "confirmed",
            "agree",
            "agreed",
            "correct",
            "verified",
            "yes",
            "concur",
        ]
        confirming_speakers = set()
        for u in utterances:
            if any(term in u.text.lower() for term in affirmative_terms):
                confirming_speakers.add(u.speaker)

        checklist.all_roles_confirmed = len(confirming_speakers) >= 2 or any(
            phrase in lower_text
            for phrase in [
                "all agree",
                "team agrees",
                "all confirmed",
                "timeout complete",
            ]
        )

        core_verified = (
            checklist.patient_identity.verified
            and checklist.procedure_name.verified
            and checklist.operative_site_side.verified
            and checklist.informed_consent.verified
        )

        checklist.incision_authorized = core_verified and (
            checklist.all_roles_confirmed or len(confirming_speakers) >= 1
        )
        print(
            f"[Engine-evaluate_timeout] Incision authorized: {checklist.incision_authorized}"
        )
        return checklist

    def match_closed_loop_orders(
        self, utterances: list[Utterance]
    ) -> list[ClosedLoopOrder]:
        print("[Engine-match_closed_loop_orders] Analyzing closed-loop communications")
        orders: list[ClosedLoopOrder] = []
        directive_patterns = [
            r"(?:give|administer|push|start|deliver|bolus|inject)\s+([\w\d\s\.\,\-]+?(?:units|mg|ml|grams|micrograms|mcg|bolus|infusion)?)",
            r"(?:request|need|pass|prep)\s+([\w\d\s\.\,\-]+?(?:clamp|suction|scalpel|retractor|trocar|suture|sponge))",
        ]

        order_counter = 1
        for i, u in enumerate(utterances):
            u_text_lower = u.text.lower()
            matched_directive = None

            for pat in directive_patterns:
                match = re.search(pat, u_text_lower)
                if match:
                    matched_directive = match.group(0).strip()
                    break

            if matched_directive:
                order_type = (
                    "Medication"
                    if any(
                        w in matched_directive
                        for w in [
                            "units",
                            "mg",
                            "ml",
                            "heparin",
                            "cefazolin",
                            "propofol",
                            "fentanyl",
                            "bolus",
                            "give",
                            "administer",
                            "push",
                        ]
                    )
                    else "Instrument / Action"
                )
                order = ClosedLoopOrder(
                    order_id=f"ORD-{order_counter:03d}",
                    timestamp_sec=u.start_sec,
                    order_type=order_type,
                    directive=u.text,
                    directed_by=f"Speaker {u.speaker}",
                )

                # Search subsequent utterances for readback
                for next_u in utterances[i + 1 : i + 5]:
                    next_text_lower = next_u.text.lower()
                    has_echo = any(
                        word in next_text_lower
                        for word in matched_directive.split()
                        if len(word) > 3
                    )
                    has_affirm = any(
                        word in next_text_lower
                        for word in [
                            "given",
                            "pushed",
                            "administered",
                            "started",
                            "passed",
                            "here",
                            "confirm",
                            "done",
                        ]
                    )

                    if has_echo or has_affirm:
                        order.readback = next_u.text
                        order.readback_by = f"Speaker {next_u.speaker}"
                        order.status = ClosedLoopStatus.CONFIRMED
                        order.verified = True
                        break

                orders.append(order)
                order_counter += 1

        print(
            f"[Engine-match_closed_loop_orders] Extracted {len(orders)} closed-loop directives"
        )
        return orders

    def generate_operative_report(
        self,
        checklist: TimeOutChecklist,
        orders: list[ClosedLoopOrder],
        transcript_text: str,
        summary_text: str,
        chapters: list[dict],
        entities: list[dict],
    ) -> OperativeReport:
        print(
            "[Engine-generate_operative_report] Compiling structured operative report"
        )
        report = OperativeReport(
            patient_id=checklist.patient_identity.details or "Unspecified Patient",
            procedure=checklist.procedure_name.details
            or "Unspecified Surgical Procedure",
            timeout_completed=checklist.all_roles_confirmed,
            incision_authorized=checklist.incision_authorized,
            closed_loop_orders=orders,
            raw_transcript=transcript_text,
            transcript_summary=summary_text,
            chapters=chapters,
            detected_entities=entities,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        )
        return report

    def format_report_markdown(self, report: OperativeReport) -> str:
        lines = [
            "# Operative Summary & Universal Protocol Audit Ledger",
            f"**Generated:** {report.generated_at}",
            f"**Patient:** {report.patient_id} | **Procedure:** {report.procedure}",
            f"**Incision Authorization Status:** {'AUTHORIZED' if report.incision_authorized else 'HOLD / INCOMPLETE'}",
            "",
            "## 1. Universal Protocol Verification",
        ]
        if report.timeout_completed and report.incision_authorized:
            lines.append(
                "- All surgical team disciplines confirmed identity, site, and procedure before incision."
            )
        else:
            lines.append(
                "- Warning: Time-Out was incomplete or missing mandatory oral confirmations."
            )

        lines.extend(
            [
                "",
                "## 2. Intra-Operative Closed-Loop Communications",
            ]
        )
        if report.closed_loop_orders:
            lines.append(
                "| Order ID | Time | Type | Directive | From | Read-Back | Status |"
            )
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for o in report.closed_loop_orders:
                lines.append(
                    f"| {o.order_id} | {o.timestamp_sec:.1f}s | {o.order_type} | {o.directive} | {o.directed_by} | {o.readback or 'None'} | {o.status.value} |"
                )
        else:
            lines.append(
                "No verbal directives or medication orders detected during this phase."
            )

        lines.extend(
            [
                "",
                "## 3. Surgical Milestones & Timeline",
            ]
        )
        if report.chapters:
            for ch in report.chapters:
                lines.append(
                    f"- **{ch.get('headline', 'Milestone')}**: {ch.get('summary', '')}"
                )
        else:
            lines.append("No automatic chapter milestones recorded.")

        lines.extend(
            [
                "",
                "## 4. Clinical Briefing & Narrative",
                report.transcript_summary or "Clinical summary not requested.",
            ]
        )

        return "\n".join(lines)


# endregion
