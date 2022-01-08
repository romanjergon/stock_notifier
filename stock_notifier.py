import os
import smtplib

import yfinance
from dotenv import load_dotenv

load_dotenv()


def get_ticker_daily_close(ticker: str) -> list[float]:
    print(ticker)
    yfinance_ticker = yfinance.Ticker(ticker)
    ticker_history = yfinance_ticker.history(period="1mo", interval="1d")
    return list(reversed(list(ticker_history["Close"])))


def calculate_difference_prc(daily_values: list, no_days: int) -> int:
    """
    Calculate the percentage of closing price difference between last trading day
    and trading day no_days ago.
    """
    last_trading_close: float = daily_values[0]
    past_day_close: float = daily_values[no_days]

    difference: float = float(last_trading_close) - float(past_day_close)
    diff_percent: int = round((difference / float(last_trading_close)) * 100)

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
    notification_mailbox = os.environ["NOTIFICATION_MAILBOX"]
    mail_password = os.environ["MAIL_PASSWORD"]
    personal_mailbox = os.environ["PERSONAL_MAILBOX"]

    daily_values: list(float) = get_ticker_daily_close(TICKER)
    one_day_difference_prc: int = calculate_difference_prc(daily_values, 1)
    week_difference_prc: int = calculate_difference_prc(daily_values, 7)

    # notify
    if one_day_difference_prc < -1:
        send_notif_mail(
            "Market is going down 1 day info",
            f"{TICKER} is down by {one_day_difference_prc} percent since prev day.",
            notification_mailbox=notification_mailbox,
            mail_password=mail_password,
            personal_mailbox=personal_mailbox,
        )

    if week_difference_prc < -4:
        send_notif_mail(
            "Market is going down week info",
            f"{TICKER} is down by {week_difference_prc} percent since prev week.",
            notification_mailbox=notification_mailbox,
            mail_password=mail_password,
            personal_mailbox=personal_mailbox,
        )


if __name__ == "__main__":
    main()
