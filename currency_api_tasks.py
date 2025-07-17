"""
currency_api_tasks.py

This module defines the CurrencyApiTask class, which fetches, analyzes, and reports
historical currency exchange rate data.

Features:
- Fetches exchange rates for USD against multiple currencies.
- Calculates percentage change, volatility, rate of change, and moving averages.
- Generates CSV and PDF reports.
"""

import requests
import math
import csv
from datetime import datetime, timedelta
from fpdf import FPDF


class CurrencyApiTask:
    """
    Class to perform currency data analysis and generate reports.
    """

    CURRENCIES = [
        "inr", "eur", "btc", "jpy", "aud", "cad", "chf", "cny",
        "pkr", "nzd", "sek", "nok", "brl", "mxn", "zar"
    ]

    BASE_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@"

    def fetch_currency_data(self, days):
        """
        Generator that fetches historical currency data.

        Args:
            days (int): Number of days to fetch data.

        Yields:
            dict: Contains date and filtered USD currency rates.
        """
        today_date = datetime.today()
        start_date = today_date - timedelta(days=days)

        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

            try:
                print(f"Fetching data for {date}...")
                url = f"{self.BASE_URL}{date}/v1/currencies/usd.json"
                response = requests.get(url)

                data = response.json()
                usd_rates = data.get("usd", {})
                filtered_rate = {
                    currency: usd_rates.get(currency)
                    for currency in self.CURRENCIES
                    if usd_rates.get(currency) is not None
                }
                yield {"date": data["date"], "usd": filtered_rate}
            except Exception as e:
                print(f"Error fetching data for {date}: {e}")
                continue

    def show_today_currency_data(self):
        """
        Fetch and display today's currency exchange rates for all tracked currencies.
        """
        today = datetime.today().strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}{today}/v1/currencies/usd.json"
        print(f"Fetching today's currency data ({today})...")

        try:
            response = requests.get(url)
            data = response.json()
            usd_rates = data.get("usd", {})
            print("Today's USD Exchange Rates:")
            print(f"{'Currency':<10} | {'Rate'}")
            print("-" * 25)

            for currency in sorted(self.CURRENCIES):
                rate = usd_rates.get(currency)
                if rate:
                    print(f"{currency.upper():<10} | {rate}")
        except Exception as e:
            print(f"Error fetching today's data: {e}")


    def standard_deviation(self, values):
        """
        Compute standard deviation.

        Args:
            values (list): List of numeric values.

        Returns:
            float: Standard deviation of values.
        """
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        return math.sqrt(variance)

    def rate_of_change(self, currency_values):
        """
        Compute average rate of change.

        Args:
            values (list): List of values.

        Returns:
            float: Average rate of change (%).
        """
        rate_change = []
        for i in range(1, len(currency_values)):
            previous = currency_values[i - 1]
            if previous != 0:
                change = (currency_values[i] - previous) / previous
                rate_change.append(change)

        return (sum(rate_change) / len(rate_change)) * 100 if rate_change else 0

    def moving_average(self, currency_values, window):
        """
        Compute moving average over a window.

        Args:
            values (list): List of values.
            window (int): Window size.

        Returns:
            list: Moving average list.
        """
        moving_average = []
        for i in range(len(currency_values)):
            if i + 1 < window:
                moving_average.append(None)
            else:
                average = sum(currency_values[i+1-window:i+1]) / window
                moving_average.append(average)
        return moving_average

    def process_currency_data(self, days):
        """
        Fetch and analyze currency data.

        Args:
            days (int): Number of days to analyze.

        Returns:
            dict: Analysis results.
        """
        currencies_data = list(self.fetch_currency_data(days))
        currency_analysis = {currency: {"values": [], "dates": []} for currency in self.CURRENCIES}

        for day_data in currencies_data:
            if not day_data:
                continue
            for currency, rate in day_data["usd"].items():
                currency_analysis[currency]["values"].append(rate)
                currency_analysis[currency]["dates"].append(day_data["date"])

        results = {}

        for currency, data in currency_analysis.items():
            values = data["values"]

            initial_value = values[0]
            final_value = values[-1]
            percentage_change = ((final_value - initial_value) / initial_value) * 100 if initial_value else 0
            volatility = self.standard_deviation(values)
            average_rate_change = self.rate_of_change(values)
            short_term_moving_average = self.moving_average(values, 7)
            long_term_moving_average = self.moving_average(values, 30)

            results[currency] = {
                "percentage_change": percentage_change,
                "volatility": volatility,
                "rate_of_change": average_rate_change,
                "short_term_ma": short_term_moving_average[-1] if len(short_term_moving_average) >= 7 else None,
                "long_term_ma": long_term_moving_average[-1] if len(long_term_moving_average) >= 30 else None,
                "initial_value": initial_value,
                "final_value": final_value,
                "values": values,
                "dates": data["dates"]
            }

        return results

    def generate_csv(self, results, filename="currency_analysis.csv"):
        """
        Generate CSV report.

        Args:
            results (dict): Analysis results.
            filename (str): Output filename.
        """
        sorted_currencies = sorted(
            results.items(),
            key=lambda item: item[1]["percentage_change"],
            reverse=True
        )
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Currency", "Initial Value", "Final Value", "Percentage Change",
                "Volatility", "Avg Rate of Change", "7-Day MA", "30-Day MA"
            ])
            for currency, data in sorted_currencies:
                writer.writerow([
                    currency.upper(),
                    data["initial_value"],
                    data["final_value"],
                    f"{data['percentage_change']:.2f}%",
                    data["volatility"],
                    f"{data['rate_of_change']:.2f}%",
                    data["short_term_ma"],
                    data["long_term_ma"]
                ])

    def generate_pdf(self, results, filename="currency_analysis.pdf"):
        """
        Generate PDF report.

        Args:
            results (dict): Analysis results.
            filename (str): Output filename.
        """
        sorted_currencies = sorted(
            results.items(),
            key=lambda item: item[1]["percentage_change"],
            reverse=True
        )
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Currency Analysis Report", ln=1, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, "Top 3 Performing Currencies:", ln=1)
        pdf.set_font("Arial", size=10)
        for currency, data in sorted_currencies[:3]:
            pdf.cell(200, 10, f"{currency.upper()}: {data['percentage_change']:.2f}% change", ln=1)
        pdf.ln(5)

        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, "Bottom 3 Performing Currencies:", ln=1)
        pdf.set_font("Arial", size=10)
        for currency, data in sorted_currencies[-3:]:
            pdf.cell(200, 10, f"{currency.upper()}: {data['percentage_change']:.2f}% change", ln=1)
        pdf.ln(10)

        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, "Detailed Currency Analysis:", ln=1)
        pdf.set_font("Arial", size=10)
        for currency, data in sorted_currencies:
            pdf.cell(200, 6, f"{currency.upper()}:", ln=1)
            pdf.cell(
                200, 6,
                f"  Volatility: {data['volatility']:.6f}", ln=1
            )
            pdf.cell(
                200, 6,
                f"  Avg Rate of Change: {data['rate_of_change']:.2f}%", ln=1
            )
            pdf.cell(
                200, 6,
                f"  7-Day MA: {data['short_term_ma'] or 'N/A'}", ln=1
            )
            pdf.cell(
                200, 6,
                f"  30-Day MA: {data['long_term_ma'] or 'N/A'}", ln=1
            )
            pdf.ln(2)

        pdf.output(filename)
