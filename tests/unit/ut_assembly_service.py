import unittest

from src.assembly_service import SPECIALTY_PRESETS, AssemblyAIService


# region Unit Tests - AssemblyAIService Vocabulary
class TestAssemblyAIServiceVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AssemblyAIService(api_key="mock_key")

    def test_default_vocabulary_contains_surgical_terms(self) -> None:
        active = self.service.get_active_vocabulary()
        self.assertIn("Time-Out", active)
        self.assertIn("cholecystectomy", active)
        self.assertIn("heparin", active)

    def test_set_custom_vocabulary_updates_active_terms(self) -> None:
        # Act
        active = self.service.set_custom_vocabulary(
            ["robotics", "da Vinci", "endowrist"]
        )

        # Assert
        self.assertIn("robotics", active)
        self.assertIn("da Vinci", active)
        self.assertIn("endowrist", active)
        self.assertIn("cholecystectomy", active)

    def test_clear_custom_vocabulary_resets_terms(self) -> None:
        # Arrange
        self.service.set_custom_vocabulary(["temporary_term"])

        # Act
        active = self.service.clear_custom_vocabulary()

        # Assert
        self.assertNotIn("temporary_term", active)
        self.assertIn("Time-Out", active)

    def test_specialty_presets_exist(self) -> None:
        self.assertIn("General Surgery (Laparoscopy)", SPECIALTY_PRESETS)
        self.assertIn("Orthopedic Surgery (Arthroplasty)", SPECIALTY_PRESETS)
        self.assertIn("Cardiovascular Surgery", SPECIALTY_PRESETS)
        self.assertIn("Neurosurgery & Spine", SPECIALTY_PRESETS)


if __name__ == "__main__":
    unittest.main()
# endregion
