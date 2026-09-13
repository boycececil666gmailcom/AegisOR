import unittest
from unittest.mock import MagicMock, patch

from src.models import Utterance
from src.ui.handlers import handle_intraop, handle_postop, handle_timeout


# region Integration Tests - Scribe Workflow
class TestScribeWorkflow(unittest.TestCase):
    def test_timeout_workflow_simulation(self) -> None:
        # Act
        status_banner, checklist_md, diar_log = handle_timeout(
            audio_file=None,
            audio_url=None,
            transcript_override=None,
        )

        # Assert
        self.assertIn("STATUS: INCISION AUTHORIZED", status_banner)
        self.assertIn("Patient Identity & MRN", checklist_md)
        self.assertIn("VERIFIED", checklist_md)
        self.assertIn("Speaker", diar_log)

    def test_intraop_workflow_simulation(self) -> None:
        # Act
        rows, summary, entities_md = handle_intraop(
            audio_file=None,
            audio_url=None,
            transcript_override=None,
        )

        # Assert
        self.assertGreater(len(rows), 0)
        self.assertIn("Total Orders Detected", summary)
        self.assertIn("Heparin", entities_md)

    def test_postop_workflow_simulation(self) -> None:
        # Act
        report_md = handle_postop(
            audio_file=None,
            audio_url=None,
            transcript_override=None,
        )

        # Assert
        self.assertIn("Operative Summary & Universal Protocol Audit Ledger", report_md)
        self.assertIn("Universal Protocol Verification", report_md)

    @patch("src.ui.handlers.assembly_service.transcribe")
    def test_timeout_with_mocked_assembly_service(
        self, mock_transcribe: MagicMock
    ) -> None:
        # Arrange
        mock_transcribe.return_value = {
            "transcript_text": "Time-Out for patient Jane Doe. Procedure is cholecystectomy. Right side marked. Consent signed. Allergies reviewed. Antibiotics in. Team agrees.",
            "utterances": [
                Utterance(
                    speaker="A",
                    start_sec=0.0,
                    end_sec=5.0,
                    text="Time-Out for patient Jane Doe. Procedure is cholecystectomy. Right side marked. Consent signed. Allergies reviewed. Antibiotics in.",
                ),
                Utterance(
                    speaker="B",
                    start_sec=5.5,
                    end_sec=7.0,
                    text="Team agrees, all confirmed.",
                ),
            ],
            "summary": "",
            "chapters": [],
            "entities": [],
            "error": None,
        }

        # Act
        status_banner, checklist_md, _diar_log = handle_timeout(
            audio_file="dummy_audio.wav",
            audio_url=None,
            transcript_override=None,
        )

        # Assert
        mock_transcribe.assert_called_once()
        self.assertIn("STATUS: INCISION AUTHORIZED", status_banner)
        self.assertIn("VERIFIED", checklist_md)


if __name__ == "__main__":
    unittest.main()
# endregion
