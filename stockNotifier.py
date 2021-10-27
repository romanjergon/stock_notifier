import requests
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()
TICKER = "VTI"  # Vanguard total stock market
API_KEY_APLHA = os.environ.get("KEY_APLHAVANTAGE")
NOTIFICATION_MAILBOX = os.environ.get("NOTIFICATION_MAILBOX")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
PERSONAL_MAILBOX = os.environ.get("PERSONAL_MAILBOX")


def get_ticker_data(ticker: str):
    """Get data from alphavantage for given ticker."""
    url = 'https://www.alphavantage.co/query'
    params = {'function': 'TIME_SERIES_DAILY_ADJUSTED',
              'symbol': ticker,
              'apikey': API_KEY_APLHA,
              }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()['Time Series (Daily)']
    daily_values = [value for (key, value) in data.items()]
    return daily_values


def calculate_difference_prc(daily_values: list, no_days: int):
    """Calculate the percentage of closing price difference between last trading day and trading day no_days ago."""
    last_trading_values = daily_values[0]
    past_day_values = daily_values[no_days]
    last_trading_close = last_trading_values['5. adjusted close']
    past_day_close = past_day_values['5. adjusted close']

    difference = float(last_trading_close) - float(past_day_close)
    diff_percent = round((difference / float(last_trading_close)) * 100)

    print(f'Calculation for time period of {no_days} days')
    print(f'Last trading day close {last_trading_close}')
    print(f'Beginning of timeperiod day close {past_day_close}')
    print(f'Difference in percentage rounded {diff_percent}')
    return diff_percent


def send_notif_mail(subject: str, body: str):
    """Send notification mail from my notification mailbox to my personal mailbox"""

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(NOTIFICATION_MAILBOX, MAIL_PASSWORD)
        connection.sendmail(NOTIFICATION_MAILBOX, PERSONAL_MAILBOX,
                            msg=f'Subject:{subject}\n\n{body}')


daily_values = get_ticker_data(TICKER)
one_day_difference_prc = calculate_difference_prc(daily_values, 1)
week_difference_prc = calculate_difference_prc(daily_values, 7)

# notify
if one_day_difference_prc < -1:
    send_notif_mail(f'Market is going down 1 day info', f'{TICKER} is down by at least 1 percent since prev day.')

if week_difference_prc < -4:
    send_notif_mail(f'Market is going down week info', f'{TICKER} is down by at least 4 percent since prev week.')
