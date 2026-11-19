"""Unit tests for the Job Match algorithm. Run with:  python -m unittest"""
import unittest

from matching import calculate_match, normalize, parse_skill_input, rank_jobs


class TestMatching(unittest.TestCase):

    def test_spec_example_full_match(self):
        pct, matched, missing = calculate_match(["Python", "SQL", "Flask"], ["Python", "SQL", "Flask"])
        self.assertEqual(pct, 100)
        self.assertEqual(missing, [])

    def test_spec_example_partial_match(self):
        pct, matched, missing = calculate_match(["Python", "SQL", "Flask"], ["Python", "SQL", "Tableau"])
        self.assertEqual(pct, 67)
        self.assertEqual(matched, ["Python", "SQL"])
        self.assertEqual(missing, ["Tableau"])

    def test_case_and_spaces_ignored(self):
        pct, _, _ = calculate_match(["  python ", "sql"], ["Python", "SQL"])
        self.assertEqual(pct, 100)

    def test_aliases(self):
        self.assertEqual(normalize("JS"), "javascript")
        pct, _, _ = calculate_match(["js"], ["JavaScript"])
        self.assertEqual(pct, 100)

    def test_job_with_no_skills(self):
        self.assertEqual(calculate_match(["Python"], []), (0, [], []))

    def test_parse_input_drops_blanks_and_duplicates(self):
        self.assertEqual(parse_skill_input("Python, , SQL, python,"), ["Python", "SQL"])

    def test_ranking_order_and_zero_filter(self):
        jobs = [
            {"job_title": "Data Analyst", "skills": ["Python", "SQL", "Tableau"]},
            {"job_title": "Software Developer", "skills": ["Python", "SQL", "Flask"]},
            {"job_title": "Designer", "skills": ["Figma"]},
            {"job_title": "Mystery", "skills": []},
        ]
        results, to_learn = rank_jobs(["Python", "SQL", "Flask"], jobs)
        self.assertEqual([r["job_title"] for r in results], ["Software Developer", "Data Analyst"])
        self.assertEqual(to_learn, [("Tableau", 1)])

        results, _ = rank_jobs(["Python", "SQL", "Flask"], jobs, include_zero=True)
        self.assertEqual(len(results), 3)  # Designer included, Mystery (no skills) still skipped


if __name__ == "__main__":
    unittest.main()