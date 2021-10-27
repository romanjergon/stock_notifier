import os
import smtplib

import requests
from dotenv import load_dotenv

load_dotenv()


def get_ticker_data(ticker: str, api_key: str):
    """Get data from alphavantage for given ticker."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": api_key,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["Time Series (Daily)"]
    daily_values = [value for (_, value) in data.items()]
    return daily_values


def calculate_difference_prc(daily_values: list, no_days: int):
    """
    Calculate the percentage of closing price difference between last trading day
    and trading day no_days ago.
    """
    last_trading_values = daily_values[0]
    past_day_values = daily_values[no_days]
    last_trading_close = last_trading_values["5. adjusted close"]
    past_day_close = past_day_values["5. adjusted close"]

    difference = float(last_trading_close) - float(past_day_close)
    diff_percent = round((difference / float(last_trading_close)) * 100)

    print(f"Calculation for time period of {no_days} days")
    print(f"Last trading day close {last_trading_close}")
    print(f"Beginning of timeperiod day close {past_day_close}")
    print(f"Difference in percentage rounded {diff_percent}")
    return diff_percent


def send_notif_mail(
    subject: str,
    body: str,
    notification_mailbox: str,
    mail_password: str,
    personal_mailbox: str,
):
    """Send notification mail from my notification mailbox to my personal mailbox"""

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(notification_mailbox, mail_password)
        connection.sendmail(
            notification_mailbox, personal_mailbox, msg=f"Subject:{subject}\n\n{body}"
        )


def main():
    TICKER = "VTI"  # Vanguard total stock market
    api_key_alpha = os.environ.get("KEY_APLHAVANTAGE")
    notification_mailbox = os.environ.get("NOTIFICATION_MAILBOX")
    mail_password = os.environ.get("MAIL_PASSWORD")
    personal_mailbox = os.environ.get("PERSONAL_MAILBOX")

    daily_values = get_ticker_data(TICKER, api_key=api_key_alpha)
    one_day_difference_prc = calculate_difference_prc(daily_values, 1)
    week_difference_prc = calculate_difference_prc(daily_values, 7)

    # notify
    if one_day_difference_prc < -1:
        send_notif_mail(
            "Market is going down 1 day info",
            f"{TICKER} is down by at least 1 percent since prev day.",
            notification_mailbox=notification_mailbox,
            mail_password=mail_password,
            personal_mailbox=personal_mailbox,
        )

    if week_difference_prc < -4:
        send_notif_mail(
            "Market is going down week info",
            f"{TICKER} is down by at least 4 percent since prev week.",
            notification_mailbox=notification_mailbox,
            mail_password=mail_password,
            personal_mailbox=personal_mailbox,
        )


if __name__ == "__main__":
    main()
