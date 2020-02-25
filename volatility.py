import pandas as pd 
import matplotlib.pyplot as plt
import statistics
import math

data = pd.read_csv("sp500_joined_closes.csv")
data = data.tail(730) # Last two years of data

POSITIVE_RETURN_PROBABILITY_FILENAME = "returns_decreasing_volatility.csv"
AVG_RETURN_FILENAME = "average_returns.csv"

# Get standard deviations for each stock given all existing data
stds = pd.DataFrame()
for col in data.columns:
    stds[col] = [data[col].std()]

# Plot prices and +- 1 standard deviation from 30 moving average for 1 stock
def plotSpread(ticker, timeFrame):
    plotting_points = pd.DataFrame()
    prev_stocks = []
    count = 0

    for row in data[ticker]:
        # Check to make sure value does not equal nan
        if not math.isnan(row):
            # Add initial stock's prices (until timeFrame is reached) to list
            if count < timeFrame:
                prev_stocks.append(row)
                count += 1
            else:
                stdev = statistics.stdev(prev_stocks)
                plotting_points = plotting_points.append({
                    "return": (row - prev_stocks[0])/prev_stocks[0], # return compared to first price of the time period
                    "spread": stdev/row, # percent of price that is equal to 1 standard deviation
                    }, ignore_index=True)
                # Remove index 0 of list and add current row
                prev_stocks.pop(0)
                prev_stocks.append(row)

    # Plot
    ax = plt.gca()
    plotting_points.reset_index().plot(kind='line',x='index',y='return',ax=ax)
    plotting_points.reset_index().plot(kind='line',x='index',y='spread', color='red', ax=ax)
    plt.show()

def calculatePercentProfitable(ticker, timeFrame, consecutiveDays):
    prev_stocks = []
    count = 0

    # List of lists containing prices for 30 days after volatility has decreased 4 days in a row
    bull_prospects = []
    days_decreasing_volatility = 0 # counter for consecutive days of decreasing volatility
    last_volatility = 0
    last_completed_index = 0

    for row in data[ticker]:
        # Check to make sure value does not equal nan
        if not math.isnan(row):
            # Add initial stock's prices (until timeFrame is reached) to list
            if count < timeFrame:
                prev_stocks.append(row)
                count += 1
            else:
                # Update most recent stocks in timeframe
                prev_stocks.pop(0)
                prev_stocks.append(row)

                # Get most recent standard deviation/volatility measurement
                stdev = statistics.stdev(prev_stocks)

                # Check if volatility is decreasing
                days_decreasing_volatility = days_decreasing_volatility + 1 if stdev < last_volatility else 0
                last_volatility = stdev
                # Start a new list with this price as index 0 in bull_prospects
                if days_decreasing_volatility >= consecutiveDays:
                    bull_prospects.append([row])
                # Append to lists that haven't reached days in timeframe in bull_prospects
                for index in range(last_completed_index, len(bull_prospects)):
                    if len(bull_prospects[index]) != timeFrame:
                        bull_prospects[index].append(row)
                        last_completed_index = index if len(bull_prospects[index]) == timeFrame else last_completed_index

    # Find percentage of times there is a positive return over next 30 days following 4 days of decreasing volatility
    count_positive_returns = 0
    for i in bull_prospects:
        count_positive_returns = count_positive_returns + 1 if i[len(i)-1] > i[0] else count_positive_returns
    return count_positive_returns/len(bull_prospects) if len(bull_prospects) != 0 else 0

def calculateAverageReturn(ticker, timeFrame, consecutiveDays):
    prev_stocks = []
    count = 0

    # List of lists containing prices for 30 days after volatility has decreased 4 days in a row
    returns = []
    bull_prospects = []
    days_decreasing_volatility = 0 # counter for consecutive days of decreasing volatility
    last_volatility = 0
    last_completed_index = 0

    for row in data[ticker]:
        # Check to make sure value does not equal nan
        if not math.isnan(row):
            # Add initial stock's prices (until timeFrame is reached) to list
            if count < timeFrame:
                prev_stocks.append(row)
                count += 1
            else:
                # Update most recent stocks in timeframe
                prev_stocks.pop(0)
                prev_stocks.append(row)

                # Get most recent standard deviation/volatility measurement
                stdev = statistics.stdev(prev_stocks)

                # Check if volatility is decreasing
                days_decreasing_volatility = days_decreasing_volatility + 1 if stdev < last_volatility else 0
                last_volatility = stdev
                # Start a new list with this price as index 0 in bull_prospects
                if days_decreasing_volatility >= consecutiveDays:
                    bull_prospects.append([row])
                # Append to lists that haven't reached days in timeframe in bull_prospects
                for index in range(last_completed_index, len(bull_prospects)):
                    if len(bull_prospects[index]) != timeFrame:
                        bull_prospects[index].append(row)
                        if len(bull_prospects[index]) == timeFrame:
                            # Add return of a completed list of prices (timeframe length long)
                            returns.append((bull_prospects[index][timeFrame-1] - bull_prospects[index][0])/bull_prospects[index][0])
                            # Dynamic programming to improve run time
                            last_completed_index = index

    # Find percentage of times there is a positive return over next 30 days following 4 days of decreasing volatility
    return 0 if len(returns) == 0 else sum(returns)/len(returns)

# Executes the function specified 6 times, each with different parameters, and then exports to a csv with given name
def execute(func, file_name):
    # Get percent positive returns for each stock - variable nomenclature --> 
    # [days to calc returna after conesecutive decreasing volatility days]_to_[days to have consecutive decreasing volatility]
    print("Starting algorithm please be patient...")
    thirty_to_three = []
    for col in data.columns:
        thirty_to_three.append(func(col, 30, 3))
    print("1/6")
    ten_to_three = []
    for col in data.columns:
        ten_to_three.append(func(col, 10, 3))
    print("2/6")
    thirty_to_five = []
    for col in data.columns:
        thirty_to_five.append(func(col, 30, 5))
    print("3/6")
    ten_to_five = []
    for col in data.columns:
        ten_to_five.append(func(col, 10, 5))
    print("4/6")
    thirty_to_seven = []
    for col in data.columns:
        thirty_to_seven.append(func(col, 30, 7))
    print("5/6")
    ten_to_seven = []
    for col in data.columns:
        ten_to_seven.append(func(col, 10, 7))
    print("6/6")

    percent_positive_returns = pd.DataFrame({
        "30-3": thirty_to_three,
        "10-3": ten_to_three,
        "30-5": thirty_to_five,
        "10-5": ten_to_five,
        "30-7": thirty_to_seven,
        "10-7": ten_to_seven
    }, index=data.columns)
    # Drop tickers called "Unnamed"
    percent_positive_returns = percent_positive_returns.drop("Unnamed: 0", axis=0)
    percent_positive_returns = percent_positive_returns.drop("Unnamed: 0.1", axis=0)
    # Sort from highest to lowest
    percent_positive_returns = percent_positive_returns.sort_values(by=['30-3'], ascending=False)
    # Export to csv
    percent_positive_returns.to_csv(file_name)

execute(calculateAverageReturn, AVG_RETURN_FILENAME)
