import unittest

from src.engine import UniversalProtocolEngine
from src.models import ClosedLoopStatus, Utterance


# region Unit Tests - Engine
class TestUniversalProtocolEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = UniversalProtocolEngine()

    def test_evaluate_timeout_authorized_success(self) -> None:
        # Arrange
        transcript = (
            "Time-Out. This is patient Jane Doe, MRN 48201. "
            "The scheduled procedure is laparoscopic cholecystectomy. "
            "Surgical site is right upper quadrant, site is marked. "
            "Informed consent is signed and verified. "
            "Allergies: no known drug allergies, airway intact. "
            "Antibiotic prophylaxis: cefazolin 2 grams infused. "
            "CT imaging displayed on screen. "
            "Team, do we all agree?"
        )
        utterances = [
            Utterance(speaker="1", start_sec=0.0, end_sec=12.0, text=transcript),
            Utterance(
                speaker="2", start_sec=12.5, end_sec=14.0, text="Anesthesia confirms."
            ),
            Utterance(
                speaker="3",
                start_sec=14.2,
                end_sec=15.5,
                text="Nursing agrees, all verified.",
            ),
        ]

        # Act
        checklist = self.engine.evaluate_timeout(transcript, utterances)

        # Assert
        self.assertTrue(checklist.patient_identity.verified)
        self.assertTrue(checklist.procedure_name.verified)
        self.assertTrue(checklist.operative_site_side.verified)
        self.assertTrue(checklist.informed_consent.verified)
        self.assertTrue(checklist.allergies_reviewed.verified)
        self.assertTrue(checklist.antibiotic_prophylaxis.verified)
        self.assertTrue(checklist.essential_imaging.verified)
        self.assertTrue(checklist.all_roles_confirmed)
        self.assertTrue(checklist.incision_authorized)

    def test_evaluate_timeout_missing_site_not_authorized(self) -> None:
        # Arrange: Missing operative site and consent
        transcript = (
            "Time-Out for patient Jane Doe. "
            "Procedure is cholecystectomy. "
            "Antibiotics are in. Can we start?"
        )
        utterances = [
            Utterance(speaker="1", start_sec=0.0, end_sec=5.0, text=transcript),
        ]

        # Act
        checklist = self.engine.evaluate_timeout(transcript, utterances)

        # Assert
        self.assertTrue(checklist.patient_identity.verified)
        self.assertTrue(checklist.procedure_name.verified)
        self.assertFalse(checklist.operative_site_side.verified)
        self.assertFalse(checklist.informed_consent.verified)
        self.assertFalse(checklist.incision_authorized)

    def test_match_closed_loop_orders_confirmed(self) -> None:
        # Arrange
        utterances = [
            Utterance(
                speaker="1",
                start_sec=30.0,
                end_sec=33.0,
                text="Please push 5000 units Heparin intravenously.",
            ),
            Utterance(
                speaker="2",
                start_sec=34.0,
                end_sec=36.0,
                text="Heparin 5000 units IV pushed and confirmed.",
            ),
        ]

        # Act
        orders = self.engine.match_closed_loop_orders(utterances)

        # Assert
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].order_id, "ORD-001")
        self.assertEqual(orders[0].order_type, "Medication")
        self.assertEqual(orders[0].status, ClosedLoopStatus.CONFIRMED)
        self.assertTrue(orders[0].verified)
        self.assertIn("Heparin", orders[0].readback)

    def test_match_closed_loop_orders_unconfirmed_open(self) -> None:
        # Arrange: Directive given without any response
        utterances = [
            Utterance(
                speaker="1",
                start_sec=50.0,
                end_sec=53.0,
                text="Administer 100 mcg fentanyl now.",
            ),
            Utterance(
                speaker="1",
                start_sec=55.0,
                end_sec=58.0,
                text="Continuing dissection along the gallbladder bed.",
            ),
        ]

        # Act
        orders = self.engine.match_closed_loop_orders(utterances)

        # Assert
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].status, ClosedLoopStatus.OPEN)
        self.assertFalse(orders[0].verified)
        self.assertEqual(orders[0].readback, "")

    def test_generate_and_format_operative_report(self) -> None:
        # Arrange
        transcript = "Patient PT-100. Laparoscopic repair. Right side confirmed. Consent verified."
        utterances = [
            Utterance(speaker="1", start_sec=0.0, end_sec=5.0, text=transcript),
            Utterance(
                speaker="2", start_sec=5.1, end_sec=6.5, text="Confirmed and agreed."
            ),
        ]
        checklist = self.engine.evaluate_timeout(transcript, utterances)
        orders = self.engine.match_closed_loop_orders(utterances)

        # Act
        report = self.engine.generate_operative_report(
            checklist=checklist,
            orders=orders,
            transcript_text=transcript,
            summary_text="Patient underwent uneventful laparoscopic repair.",
            chapters=[{"headline": "Incision", "summary": "Initial trocar placement"}],
            entities=[{"text": "Trocar", "entity_type": "medical_device"}],
        )
        formatted_md = self.engine.format_report_markdown(report)

        # Assert
        self.assertIn("Operative Summary", formatted_md)
        self.assertIn("Universal Protocol Verification", formatted_md)
        self.assertIn("Clinical Briefing & Narrative", formatted_md)


if __name__ == "__main__":
    unittest.main()
# endregion
