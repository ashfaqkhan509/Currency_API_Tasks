import argparse
from currency_api_tasks import CurrencyApiTask


def main():
    """
    Command-line interface to run currency analysis or show today's currency data.
    """
    parser = argparse.ArgumentParser(description="Currency Analysis Tool")
    parser.add_argument(
        "--days",
        type=int,
        default=50,
        help="Number of days for historical data"
    )
    parser.add_argument(
        "--today",
        action="store_true",
        help="Show only today's currency exchange data"
    )

    args = parser.parse_args()
    task = CurrencyApiTask()

    if args.today:
        task.show_today_currency_data()
    else:
        print(f"Processing data for {args.days} days...")
        results = task.process_currency_data(args.days)

        print("Generating CSV report.")
        task.generate_csv(results)

        print("Generating PDF report.")
        task.generate_pdf(results)

        print("Analysis complete. Reports generated: "
              "currency_analysis.csv and currency_analysis.pdf")


if __name__ == "__main__":
    main()
