import unittest
import os
import csv
from currency_api_tasks import CurrencyApiTask


class TestCurrencyAPITask(unittest.TestCase):

    def setUp(self):
        self.task = CurrencyApiTask()
        self.test_data = [
            234.4, 394.53, 12.45, 65.3, 89.3, 35.8, 91.23, 142.5, 58.2, 99.3
        ]

    def test_std_deviation(self):
        """
        Test the standard deviation function.
        """
        expected_result = 107.9694634098
        result = self.task.standard_deviation(self.test_data)
        self.assertAlmostEqual(result, expected_result, places=4)

    def test_rate_of_change_normal(self):
        """
        Test the rate_of_change function with increasing values.
        """
        values = [100, 110, 121]
        expected = ((0.10 + 0.10) / 2) * 100
        result = self.task.rate_of_change(values)
        self.assertAlmostEqual(result, expected, places=5)

    def test_moving_average_normal(self):
        """
        Test moving average with standard input and window size 3.
        """
        values = [10, 20, 30, 40, 50]
        window = 3
        expected = [None, None, 20.0, 30.0, 40.0]
        result = self.task.moving_average(values, window)
        self.assertEqual(result, expected)

    def test_moving_average_window_1(self):
        """
        Test moving average with window size of 1.
        """
        values = [5, 10, 15]
        expected = [5.0, 10.0, 15.0]
        result = self.task.moving_average(values, 1)
        self.assertEqual(result, expected)

    def test_moving_average_large_window(self):
        """
        Test moving average when window size is larger than data.
        """
        values = [1, 2]
        window = 5
        expected = [None, None]
        result = self.task.moving_average(values, window)
        self.assertEqual(result, expected)

    def test_generate_csv(self):
        """
        Test CSV report generation and structure validation.
        """
        test_results = {
            'eur': {
                "initial_value": 1.0,
                "final_value": 1.2,
                "percentage_change": 20.0,
                "volatility": 0.05,
                "rate_of_change": 10.0,
                "short_term_ma": 1.15,
                "long_term_ma": 1.1
            },
            'gbp': {
                "initial_value": 2.0,
                "final_value": 2.4,
                "percentage_change": 20.0,
                "volatility": 0.08,
                "rate_of_change": 9.5,
                "short_term_ma": 2.3,
                "long_term_ma": 2.1
            }
        }

        filename = "test_currency_analysis.csv"
        self.task.generate_csv(test_results, filename)
        self.assertTrue(os.path.exists(filename))

        with open(filename, newline='') as file:
            reader = list(csv.reader(file))
            expected_header = [
                "Currency", "Initial Value", "Final Value", "Percentage Change",
                "Volatility", "Avg Rate of Change", "7-Day MA", "30-Day MA"
            ]
            self.assertEqual(reader[0], expected_header)
            self.assertEqual(len(reader), 3)
            self.assertEqual(reader[1][0], 'EUR')
            self.assertEqual(reader[2][0], 'GBP')

        os.remove(filename)

    def test_generate_pdf(self):
        """
        Test PDF report generation and file creation.
        """
        test_results = {
            'eur': {
                "initial_value": 1.0,
                "final_value": 1.2,
                "percentage_change": 20.0,
                "volatility": 0.05,
                "rate_of_change": 10.0,
                "short_term_ma": 1.15,
                "long_term_ma": 1.1,
            },
            'pkr': {
                "initial_value": 2.0,
                "final_value": 2.4,
                "percentage_change": 19.0,
                "volatility": 0.06,
                "rate_of_change": 9.0,
                "short_term_ma": 2.3,
                "long_term_ma": 2.2,
            },
            'jpy': {
                "initial_value": 100.0,
                "final_value": 110.0,
                "percentage_change": 10.0,
                "volatility": 0.02,
                "rate_of_change": 4.0,
                "short_term_ma": 108.0,
                "long_term_ma": 106.0,
            },
            'inr': {
                "initial_value": 80.0,
                "final_value": 76.0,
                "percentage_change": -5.0,
                "volatility": 0.01,
                "rate_of_change": -2.5,
                "short_term_ma": 77.5,
                "long_term_ma": 78.0,
            },
        }

        filename = "test_currency_analysis.pdf"
        self.task.generate_pdf(test_results, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)


if __name__ == '__main__':
    unittest.main(verbosity=2)
