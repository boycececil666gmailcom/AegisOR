import unittest

from src.models import (
    ChecklistItem,
    ClosedLoopOrder,
    ClosedLoopStatus,
    OperativeReport,
    TimeOutChecklist,
)


# region Unit Tests - Models
class TestModels(unittest.TestCase):
    def test_checklist_item_serialization(self) -> None:
        # Arrange
        item = ChecklistItem(
            key="patient_identity",
            label="Patient Identity & MRN",
            verified=True,
            details="John Doe MRN-12345",
            confirmed_by=["Surgeon", "Nurse"],
        )

        # Act
        serialized = item.to_dict()

        # Assert
        self.assertEqual(serialized["key"], "patient_identity")
        self.assertTrue(serialized["verified"])
        self.assertEqual(serialized["details"], "John Doe MRN-12345")
        self.assertEqual(len(serialized["confirmed_by"]), 2)

    def test_timeout_checklist_completion_percentage(self) -> None:
        # Arrange
        checklist = TimeOutChecklist()

        # Act & Assert
        self.assertEqual(checklist.completion_percentage(), 0.0)

        checklist.patient_identity.verified = True
        checklist.procedure_name.verified = True
        self.assertAlmostEqual(
            checklist.completion_percentage(), (2 / 7) * 100.0, places=1
        )

    def test_closed_loop_order_row_format(self) -> None:
        # Arrange
        order = ClosedLoopOrder(
            order_id="ORD-001",
            timestamp_sec=45.2,
            order_type="Medication",
            directive="Administer 5000 units Heparin",
            directed_by="Speaker 1",
            readback="5000 units Heparin pushed",
            readback_by="Speaker 2",
            status=ClosedLoopStatus.CONFIRMED,
            verified=True,
        )

        # Act
        row = order.to_row()

        # Assert
        self.assertEqual(row[0], "ORD-001")
        self.assertEqual(row[1], "45.2s")
        self.assertEqual(row[2], "Medication")
        self.assertEqual(row[7], ClosedLoopStatus.CONFIRMED.value)

    def test_operative_report_creation(self) -> None:
        # Arrange & Act
        report = OperativeReport(
            patient_id="PT-901",
            procedure="Laparoscopic Cholecystectomy",
            timeout_completed=True,
            incision_authorized=True,
        )

        # Assert
        self.assertEqual(report.patient_id, "PT-901")
        self.assertTrue(report.timeout_completed)
        self.assertTrue(report.incision_authorized)
        self.assertEqual(len(report.closed_loop_orders), 0)


if __name__ == "__main__":
    unittest.main()
# endregion
