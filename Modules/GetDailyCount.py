import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ == "__main__":
    curr_dir = "Tweets_Sorted"
    pattern = r'[0-9][0-9][0-9][0-9]_[0-9]_[0-9][0-9]'
    count_day = {}
    for day in os.listdir(curr_dir):
        if re.match(pattern, day):
            if os.path.isdir(os.path.join(curr_dir, day)):
                count_day[day] = len(os.listdir(os.path.join(curr_dir, day))) * 5001
                print(day, count_day[day])
    df = pd.DataFrame.from_dict(count_day, orient = 'index')
    df = df.reset_index()
    df.columns = ['Date', 'Number of Tweets']
    df['Date'] = pd.to_datetime(df['Date'], format="%Y_%m_%d")
    df.set_index('Date', inplace = True)
    fig, ax = plt.subplots(figsize=(15,7))

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())

    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Tweets")
    ax.set_title("Daily Streams of Tweets")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    ax.bar(df.index, df["Number of Tweets"])

    plt.savefig("counts.png")
