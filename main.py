import argparse
from currency_api_tasks import process_currency_data, generate_csv, generate_pdf


def main():
    parser = argparse.ArgumentParser(description="Currency Analysis Tool")
    parser.add_argument("--days", type=int, default=50, help="Number of days for historical data")
    args = parser.parse_args()

    print(f"Processing currency data for {args.days} days.")
    results = process_currency_data(args.days)

    print("Generating CSV report.")
    generate_csv(results)

    print("Generating PDF report.")
    generate_pdf(results)

    print("Analysis complete. Reports generated: currency_analysis.csv and currency_analysis.pdf")


if __name__ == "__main__":
    main()
