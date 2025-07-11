import requests
from datetime import datetime, timedelta
import math
import csv
from fpdf import FPDF


CURRENCIES = [
    "inr", "eur", "btc", "jpy", "aud", "cad", "chf", "cny",
    "pkr", "nzd", "sek", "nok", "brl", "mxn", "zar"
]

BASE_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@"


def fetch_currency_data(days):
    """
    Fetch data from currency api

    parameter:
        - list of 15 different type of currency for which i want to get data
        - historical data for N number of days
    """

    today_date = datetime.today()
    start_date = today_date - timedelta(days=days)

    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

        try:
            url = f"{BASE_URL}{date}/v1/currencies/usd.json"
            response = requests.get(url)

            data = response.json()
            usd_rates = data.get("usd", {})
            filtered_rates = {cur: usd_rates.get(cur) for cur in CURRENCIES if usd_rates.get(cur) is not None}

            yield {
                "date": data["date"],
                "usd": filtered_rates
            }

        except Exception as e:
            return f"Error: {e}"


def standard_deviation(currencies_data):
    """
    Calulate the standard deviation of currenciec
    """
    n = len(currencies_data)
    mean = sum(currencies_data) / n
    var = sum((x - mean) ** 2 for x in currencies_data) / n
    return math.sqrt(var)


def rate_of_change(currency_values):
    """
    Calculate the rate of change of each currency
    """
    rate_change = []
    for i in range(1, len(currency_values)):
        change = (currency_values[i] - currency_values[i-1]) / currency_values[i-1]
        rate_change.append(change)

    avg_rate_change = (sum(rate_change) / len(rate_change)) * 100 if rate_change else 0
    return avg_rate_change


def moving_average(currency_values, window):
    """
    Calculate the moving average
    """
    averages = []
    for i in range(len(currency_values)):
        if i + 1 < window:
            averages.append(None)
        else:
            avg = sum(currency_values[i+1-window:i+1]) / window
            averages.append(avg)
    return averages


def process_currency_data(days):
    """
    Process currency data for analysis

    parameter:
        it recive the days ad a parameter to get currency N number of days

    return:
        Return the result dictionary having currency details which include al the metrices for each currency
    """

    historical_data = list(fetch_currency_data(days))

    currency_analysis = {currency: {"values": [], "dates": []} for currency in CURRENCIES}

    for day_data in historical_data:
        if day_data is None:
            continue
        for currency, rate in day_data["usd"].items():
            currency_analysis[currency]["values"].append(rate)
            currency_analysis[currency]["dates"].append(day_data["date"])

    results = {}

    for currency, data in currency_analysis.items():
        values = data["values"]
        initial_value = values[0]
        final_value = values[-1]
        percentage_change = ((final_value - initial_value) / initial_value) * 100

        volatility = standard_deviation(values)

        avg_rate_change = rate_of_change(values)

        short_term_ma = moving_average(values, 7)
        long_term_ma = moving_average(values, 30)

        results[currency] = {
            "percentage_change": percentage_change,
            "volatility": volatility,
            "rate_of_change": avg_rate_change,
            "short_term_ma": short_term_ma[-1] if short_term_ma else None,
            "long_term_ma": long_term_ma[-1] if long_term_ma else None,
            "initial_value": initial_value,
            "final_value": final_value,
            "values": values,
            "dates": data["dates"]
        }
    return results


def generate_csv(results, filename="currency_analysis.csv"):
    """
    Generate CSV file with analysis results
    """
    sorted_currencies = sorted(results.items(), key=lambda item: item[1]["percentage_change"], reverse=True)
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


def generate_pdf(results, filename="currency_analysis.pdf"):
    """
    Generate PDF report with analysis results.
    It include the 3 best-performing and bottom 3 worst-performing currencies
    and all the detail analysis of each currency.
    """

    sorted_currencies = sorted(results.items(), key=lambda item: item[1]["percentage_change"], reverse=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Currency Analysis Report", ln=1, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Top 3 Performing Currencies:", ln=1)
    pdf.set_font("Arial", size=10)
    for currency, data in sorted_currencies[:3]:
        pdf.cell(200, 10, txt=f"{currency.upper()}: {data['percentage_change']:.2f}% change", ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Bottom 3 Performing Currencies:", ln=1)
    pdf.set_font("Arial", size=10)
    for currency, data in sorted_currencies[-3:]:
        pdf.cell(200, 10, txt=f"{currency.upper()}: {data['percentage_change']:.2f}% change", ln=1)
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Detailed Currency Analysis:", ln=1)
    pdf.set_font("Arial", size=10)
    for currency, data in sorted_currencies:
        pdf.cell(200, 6, txt=f"{currency.upper()}:", ln=1)
        pdf.cell(200, 6, txt=f"  Volatility (Standard deviation): {data['volatility']:.6f}", ln=1)
        pdf.cell(200, 6, txt=f"  Average Rate of Change: {data['rate_of_change']:.2f}%", ln=1)
        pdf.cell(200, 6, txt=f"  7-Day Moving Average: {data['short_term_ma'] if data['short_term_ma'] else 'N/A'}", ln=1)
        pdf.cell(200, 6, txt=f"  30-Day Moving Average: {data['long_term_ma'] if data['long_term_ma'] else 'N/A'}", ln=1)
        pdf.ln(2)
    pdf.output(filename)
