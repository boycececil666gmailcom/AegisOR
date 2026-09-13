from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# region Enums
class SurgicalPhase(str, Enum):
    PRE_OP_TIMEOUT = "Pre-Op Time-Out"
    INTRA_OP_MAINTENANCE = "Intra-Op Maintenance"
    POST_OP_SIGNOUT = "Post-Op Sign-Out"


class ChecklistStatus(str, Enum):
    PENDING = "Pending"
    VERIFIED = "Verified"
    FLAGGED = "Flagged"


class ClosedLoopStatus(str, Enum):
    OPEN = "Open (Awaiting Read-Back)"
    CONFIRMED = "Confirmed (Closed-Loop Complete)"
    DISCREPANCY = "Discrepancy Detected"


class SurgicalRole(str, Enum):
    SURGEON = "Attending Surgeon"
    ANESTHESIOLOGIST = "Anesthesiologist"
    NURSE = "Circulating Nurse"
    SCRUB_TECH = "Surgical Technologist"
    UNKNOWN = "Unassigned Staff"


# endregion


# region Domain Models
@dataclass
class ChecklistItem:
    key: str
    label: str
    verified: bool = False
    details: str = ""
    confirmed_by: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "verified": self.verified,
            "details": self.details,
            "confirmed_by": self.confirmed_by,
        }


@dataclass
class TimeOutChecklist:
    patient_identity: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "patient_identity", "Patient Identity & MRN"
        )
    )
    procedure_name: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "procedure_name", "Correct Surgical Procedure"
        )
    )
    operative_site_side: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "operative_site_side", "Operative Site, Side & Surgical Marking"
        )
    )
    informed_consent: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "informed_consent", "Informed Surgical Consent Signed"
        )
    )
    allergies_reviewed: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "allergies_reviewed", "Allergies & Airway Verification"
        )
    )
    antibiotic_prophylaxis: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "antibiotic_prophylaxis", "Antibiotic Prophylaxis (< 60 mins)"
        )
    )
    essential_imaging: ChecklistItem = field(
        default_factory=lambda: ChecklistItem(
            "essential_imaging", "Essential Diagnostic Imaging Displayed"
        )
    )
    all_roles_confirmed: bool = False
    incision_authorized: bool = False

    @property
    def items(self) -> list[ChecklistItem]:
        return [
            self.patient_identity,
            self.procedure_name,
            self.operative_site_side,
            self.informed_consent,
            self.allergies_reviewed,
            self.antibiotic_prophylaxis,
            self.essential_imaging,
        ]

    def completion_percentage(self) -> float:
        verified_count = sum(1 for item in self.items if item.verified)
        return (verified_count / len(self.items)) * 100.0


@dataclass
class Utterance:
    speaker: str
    start_sec: float
    end_sec: float
    text: str
    role: str = SurgicalRole.UNKNOWN.value


@dataclass
class ClosedLoopOrder:
    order_id: str
    timestamp_sec: float
    order_type: str
    directive: str
    directed_by: str
    readback: str = ""
    readback_by: str = ""
    status: ClosedLoopStatus = ClosedLoopStatus.OPEN
    verified: bool = False

    def to_row(self) -> list[str]:
        return [
            self.order_id,
            f"{self.timestamp_sec:.1f}s",
            self.order_type,
            self.directive,
            self.directed_by,
            self.readback if self.readback else "Pending...",
            self.readback_by if self.readback_by else "Awaiting staff",
            self.status.value,
        ]


@dataclass
class OperativeReport:
    patient_id: str
    procedure: str
    timeout_completed: bool
    incision_authorized: bool
    closed_loop_orders: list[ClosedLoopOrder] = field(default_factory=list)
    raw_transcript: str = ""
    transcript_summary: str = ""
    chapters: list[dict] = field(default_factory=list)
    detected_entities: list[dict] = field(default_factory=list)
    generated_at: str = ""


# endregion
