from datetime import datetime
import gspread
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

gc = gspread.service_account(filename='service_account.json')


def plot_waypoints_by_date():
    sheet_name = os.getenv('GSHEET_NAME')  # Google Sheet name (required)
    if not sheet_name:
        raise ValueError("GSHEET_NAME environment variable must be set")
    ws_index = os.getenv('GSHEET_WORKSHEET', '1')  # Worksheet index/name
    data_start_row = os.getenv('GSHEET_DATA_START_ROW', '3')  # First row with data
    date_format = os.getenv('DATE_FORMAT', "%m/%d/%Y")  # Date format in sheet
    time_format = os.getenv('TIME_FORMAT', "%H:%M:%S")  # Time format in sheet

    sh = gc.open(sheet_name)
    ws = sh.worksheet(ws_index)
    sheet_rows = len(ws.get_all_values())
    range_of_cells = ws.get(f'A{data_start_row}:B{sheet_rows}')

    dates = [row[0] for row in range_of_cells]
    times = [row[1] for row in range_of_cells]

    x_dates = [datetime.strptime(date, date_format) for date in dates if date.strip()]
    y_times = [datetime.strptime(time, time_format) for time in times if time.strip()]

    y_seconds = [time.hour * 3600 + time.minute * 60 + time.second for time in y_times]

    date_time_dict = {}
    for date, time in zip(x_dates, y_seconds):
        if date in date_time_dict:
            date_time_dict[date]['total_time'] += time  # Cumulative waypoint time for date
            date_time_dict[date]['count'] += 1  # Number of waypoints on date
        else:
            date_time_dict[date] = {'total_time': time, 'count': 1}

    dates_list = []
    average_times = []
    sizes = []
    for date, data in date_time_dict.items():
        dates_list.append(date)
        average_times.append(data['total_time'] / data['count'])  # Average time per waypoint
        sizes.append(data['count'] * 100)  # Scale count by 100 for marker size

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor('#5f5f5f')
    fig.patch.set_facecolor('#3f3f3f')

    ax.scatter(dates_list, average_times, s=sizes, color='blue', alpha=0.2, label='Average Time per Day')  # Marker size scales with waypoint count

    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d/%Y'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())

    ax.set_title('Waypoint Activity by Date')
    ax.set_xlabel('Date')  # X-axis: calendar dates
    ax.set_ylabel('Time (seconds)')  # Y-axis: average time per waypoint

    plt.xticks(rotation=45)
    ax.grid(False)
    plt.tight_layout()

    plt.show()


if __name__ == '__main__':
    plot_waypoints_by_date()

