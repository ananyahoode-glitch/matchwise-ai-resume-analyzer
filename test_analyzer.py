import unittest

from src.analyzer import analyze, extract_skills


class AnalyzerTests(unittest.TestCase):
    def test_aliases_are_normalized(self):
        self.assertEqual(extract_skills("Built ML APIs using sklearn and ReactJS."), ["machine learning", "react", "scikit-learn"])

    def test_analysis_reports_gaps_without_inventing_skills(self):
        report = analyze(
            "Ada Lovelace\nada@example.com\nSkills: Python, SQL, machine learning.\nProjects: Built analysis tools that improved a report by 20%.",
            "We need a Python and SQL engineer with machine learning and Docker experience.",
        )
        self.assertIn("docker", report["missing_skills"])
        self.assertIn("python", report["matching_skills"])
        self.assertGreater(report["components"]["coverage"], 0)
        self.assertIn("not an ATS score", report["disclaimer"])


if __name__ == "__main__":
    unittest.main()
