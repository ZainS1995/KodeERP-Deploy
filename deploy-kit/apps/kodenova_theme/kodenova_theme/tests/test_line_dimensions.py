"""Unit tests for the line dimension sync rule. Run without a site:
    env/bin/python -m unittest apps/kodenova_theme/kodenova_theme/tests/test_line_dimensions.py
"""
import unittest

from kodenova_theme.accounting.line_dimensions import apply_to_rows, header_cost_center, pick

HO, OLAYA, MALQA = "Head Office - NJB", "Olaya Branch - NJB", "Malqa Branch - NJB"


class Row(dict):
	get = dict.get

	def set(self, k, v):
		self[k] = v


class TestPick(unittest.TestCase):
	def test_empty_line_takes_header(self):
		self.assertEqual(pick(None, OLAYA, HO), OLAYA)

	def test_default_line_moves_to_branch_header(self):
		self.assertEqual(pick(HO, OLAYA, HO), OLAYA)

	def test_deliberate_other_branch_kept(self):
		self.assertIsNone(pick(MALQA, OLAYA, HO))

	def test_head_office_header_keeps_lines(self):
		self.assertIsNone(pick(HO, HO, HO))
		self.assertIsNone(pick(MALQA, HO, HO))

	def test_no_header_no_change(self):
		self.assertIsNone(pick(None, None, HO))
		self.assertIsNone(pick(HO, None, HO))

	def test_no_company_default(self):
		self.assertEqual(pick(None, OLAYA, None), OLAYA)
		self.assertIsNone(pick(HO, OLAYA, None))


class TestRows(unittest.TestCase):
	def test_items_and_taxes(self):
		rows = [Row(idx=1, cost_center=HO, branch=None), Row(idx=2, cost_center=MALQA, branch="Malqa"), Row(idx=3, cost_center=None, branch=None)]
		ch = apply_to_rows(rows, {"cost_center": OLAYA, "branch": "Olaya"}, {"cost_center": HO, "branch": None})
		self.assertEqual([r["cost_center"] for r in rows], [OLAYA, MALQA, OLAYA])
		self.assertEqual([r["branch"] for r in rows], ["Olaya", "Malqa", "Olaya"])
		self.assertEqual(len(ch), 4)


class TestHeaderFromBranch(unittest.TestCase):
	MAP = {"Olaya": OLAYA, "Malqa": MALQA, "Head Office": HO}

	def test_empty_header_takes_branch_cc(self):
		self.assertEqual(header_cost_center("Olaya", None, HO, self.MAP), OLAYA)

	def test_default_header_takes_branch_cc(self):
		self.assertEqual(header_cost_center("Malqa", HO, HO, self.MAP), MALQA)

	def test_deliberate_other_branch_cc_kept(self):
		self.assertIsNone(header_cost_center("Olaya", MALQA, HO, self.MAP))

	def test_already_right(self):
		self.assertIsNone(header_cost_center("Olaya", OLAYA, HO, self.MAP))

	def test_unmapped_or_no_branch(self):
		self.assertIsNone(header_cost_center("Unknown", None, HO, self.MAP))
		self.assertIsNone(header_cost_center(None, None, HO, self.MAP))
		self.assertIsNone(header_cost_center("Olaya", None, HO, {}))

	def test_head_office_branch(self):
		self.assertIsNone(header_cost_center("Head Office", HO, HO, self.MAP))


if __name__ == "__main__":
	unittest.main()
