from app.services.json_service import add_operation_to_json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from app.services.json_service import add_object_to_json, add_operation_to_json, update_json_values

class Metrics:
  def __init__(self, initial_capital, monthly_contribution, strategy_id, profile_id, comission):
    self.initial_capital = initial_capital
    self.monthly_contribution = monthly_contribution
    self.strategy_id = strategy_id
    self.profile_id = profile_id
    self.comission = comission
  
  ### Operations in the db
  def InitStrategy(self, name, description, model):
    filename = '../data/strategies.json'
    add_object_to_json(name, description, model, filename)
    
  ## Saving Operation in the db
  def CreateOperation(self, asset, operation_date, operation_type, amount, unit_price, total_return, period):
    filename = '../data/operation.json'
    add_operation_to_json(operation_type, asset, operation_date, amount, unit_price, total_return, period, filename)
    
    
  def UpdateInvestmentProfileStrategy(self, total_returns, volatility_values, max_loss_values, sharpe_ratio_values, sortino_ratio_values, alphas, betas, information_ratio_data, success_rate, portfolio_concentration_rate):
    filename = '../data/result.json'
    data = {
      'total_profitability': np.mean(total_returns),
      'volatility': np.mean(volatility_values),
      'maximum_loss': np.mean(max_loss_values),
      'sharpe': np.mean(sharpe_ratio_values),
      'sortino': np.mean(sortino_ratio_values),
      'alpha': np.mean(alphas),
      'beta': np.mean(betas),
      'information_ratio': np.mean(information_ratio_data),
      'success_rate': success_rate,
      'portfolio_concentration_ratio': portfolio_concentration_rate,
    }
    update_json_values(data, filename)

  # This method sets the date to be month and year.
  def dividendByYearAndMonth(self, data):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df.index)
    df.set_index('Date', inplace=True)
    df.index = df.index.strftime('%Y-%m')
    return df

  # This method joins the ETF data with its dividends.
  def joinDataAndDividends(self, data, dividends):
    dividends = self.dividendByYearAndMonth(dividends)
    dividends = dividends.reset_index()
    dividends['Date'] = pd.to_datetime(dividends['Date'])
    dividends['Year_Month'] = dividends['Date'].dt.to_period('M')
    data.index = pd.to_datetime(data.index)
    data['Year_Month'] = data.index.to_period('M')
    merged_df = pd.merge(data, dividends, on='Year_Month', how='left')
    merged_df.drop('Date', axis=1, inplace=True)
    merged_df.rename(columns={'Year_Month': 'Date'}, inplace=True)
    return merged_df
  

  def AnnualInflation(self, url):
    # Map the month name to the number
    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12"
    }

    # Request
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        series_data = data['Results']['series'][0]['data']
        data_list = [{'year': point['year'], 'period': point['periodName'], 'value': point['value']} for point in series_data]
        df = pd.DataFrame(data_list)
        df['date'] = pd.to_datetime(df['year'] + '-' + df['period'].apply(lambda x: month_map[x]), format='%Y-%m')
        df.drop(columns=['year', 'period'], inplace=True)
        df = df[::-1]
        annual_inflation = df.groupby(df['date'].dt.year)['value'].agg(['first', 'last']).rename(columns={'first': 'cpi_start', 'last': 'cpi_end'})
        annual_inflation[['cpi_start', 'cpi_end']] = annual_inflation[['cpi_start', 'cpi_end']].apply(pd.to_numeric)
        annual_inflation['inflation_rate'] = ((annual_inflation['cpi_end'] - annual_inflation['cpi_start']) / annual_inflation['cpi_start']) * 100
        return annual_inflation
    else:
        print("Error en la solicitud:", response.status_code)

    
  ## This method show the acive performance 
  def ShowTimelineTotalReturn(self, data):
    fig = plt.figure(figsize=(10, 6*len(data)))
    for i, item in enumerate(data):
        operations = item['operations']
        operations['Date'] = operations['Date'].dt.to_timestamp()
        dates = operations['Date']
        total = operations['Total']
        ax = fig.add_subplot(len(data), 1, i+1)
        ax.plot(dates, total)
        ax.set_ylabel('Price')
        ax.set_title(f'Total Return: {item["total"]}')
        ax.set_xlim(min(dates), max(dates))
        ax.tick_params(axis='x', rotation=45)

    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

  ## Get inflaction rate from the dataset
  def GetInflationRate(self, year, annual_inflation):
    return annual_inflation.loc[year, 'inflation_rate']

  def CalculateAccumulatedValue(self, num_months, annual_inflation, start_year):
    accumulated_values = [self.initial_capital]
    for month in range(1, num_months):
      
      accumulated_value = accumulated_values[-1] + self.monthly_contribution
      if month % 12 == 0:
        current_year = int(start_year) + (month // 12) - 1
        inflation_rate = self.GetInflationRate(current_year, annual_inflation)
        accumulated_value = accumulated_value - (accumulated_value * inflation_rate) / 100
      accumulated_values.append(accumulated_value)
    return accumulated_values

  ## Grapgic comparision between our active performace and the savings performance
  def showComparisonBetweenActiveAndSavings(self, data, annual_inflation, start_year):
    fig = plt.figure(figsize=(10, 6*len(data)))

    for i, item in enumerate(data):
        operations = item['operations']
        dates = operations['Date']
        total = operations['Total']
        num_months = len(dates)
        accumulated_values = self.CalculateAccumulatedValue(num_months, annual_inflation, start_year)
        ax = fig.add_subplot(len(data), 1, i+1)
        ax.plot(dates, accumulated_values, label='Accumulated Money', color='red')
        ax.plot(dates, total, label='Investment', color='blue')
        ax.set_ylabel('Value')
        ax.set_title(f'Total Return: {item["total"]}')
        ax.set_xlim(min(dates), max(dates))
        ax.tick_params(axis='x', rotation=45)
        ax.legend()

    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

  ## This method calculate the mean anunualized return of one active
  def MeanAnnualizedReturn(self, annual_returns): 
    variations = [entry['variation'] for entry in annual_returns]
    return np.mean(variations)

  ## This method represent the annualized return
  def AnnualizadReturnGraphic(self, annual_returns):
    years = [entry['year'] for entry in annual_returns]
    variations = [entry['variation'] for entry in annual_returns]

    positive_variations = [max(v, 0) for v in variations]
    negative_variations = [min(v, 0) for v in variations]

    plt.bar(years, positive_variations, color='green')
    plt.bar(years, negative_variations, color='red', alpha=0.7)
    
    plt.xlabel('Year')
    plt.ylabel('Variation (%)')
    plt.title('Annual Return')
    plt.grid(True)
    plt.show()
    

  ## This method calculate the expected grow rate values
  def experatedGrowRateValues(self, grow_rate, years):
    values = []
    monthly_grow_rate = grow_rate / 12
    total = self.initial_capital
    for i in range(1, years * 12 + 1):
      total += total * (monthly_grow_rate / 100) + self.monthly_contribution
      values.append(total)
    return values

  ## This method show the graphic of the expected grow rate
  def showScatterPlot(self, index, annual_returns, years, data):
      fig = plt.figure(figsize=(10, 6*len(data)))

      operations = data[index]['operations']
      dates = operations['Date']
      total = operations['Total']

      ax = fig.add_subplot(len(data), 1, index + 1)
      ax.plot(dates, self.experatedGrowRateValues(self.MeanAnnualizedReturn(annual_returns), years), label='Expecting grow rate', color='red')
      ax.plot(dates, total, label='Investment', color='blue')
      ax.set_ylabel('Value')
      ax.set_title(f'Total Return: {data[index]["total"]}')
      ax.set_xlim(min(dates), max(dates))
      ax.tick_params(axis='x', rotation=45)
      ax.legend()

      plt.xlabel('Date')
      plt.tight_layout()
      plt.show()
      

  ## This method calculate the volatility of the diferent timeline
  def CalculateVolatility(self, data, names): 
    volatility_values = []
    array_volatility = []

    for index, item in enumerate(data):
        returns = item['operations']['Total'].pct_change()
        volatility = returns.std() * 100
        volatility_values.append(volatility)
        array_volatility.append({"name": names[index], "volatility (%)": volatility})
        
    return [array_volatility, volatility]

  def CalculateMaximunLoss(self, data):
    max_loss_values = []
    for item in data:
      operations = item['operations']
      price_diff = operations['Price'].diff()
      max_loss_values.append(np.min(price_diff))
      
    return [price_diff, max_loss_values]
      

  ## This method show the maximunLossGraphic
  def showMaximunLossGraphic(self, data, price_diff):
      plt.figure(figsize=(10, 6))

      for index, item in enumerate(data):
          plt.plot(price_diff, label=f'Total Return: {item["total"]}')

      plt.xlabel('Operation Number')
      plt.ylabel('Variations')
      plt.title('Price Variation Comparison')

      plt.legend()
      plt.grid(True)
      plt.tight_layout()
      plt.show()
      
      
  ## This method show in a dataframe the maximun loss values    
  def displayMaximunLossDataFrame(self, names, data, max_loss_values):
    values = []
    for index, item in enumerate(data):
        values.append({"name": names[index], "maximun_loss (%)": max_loss_values[index]})

    df_maximun_loss = pd.DataFrame(values)
    display(df_maximun_loss)

    maximun_losses = [entry['maximun_loss (%)'] for entry in values]
    print("Average maximum loss: ", np.mean(maximun_losses))
    
  ## This method calulate the sharpe ratio value
  def SharpeRatio(self, risk_free_rate, annualized_return, volatility):
    return (annualized_return - risk_free_rate) / volatility

  def displayRatios(self, name, ratio_values):
    values = []
    for index, item in enumerate(ratio_values):
      values.append({"Period": index + 1, f"{name} ratio value": item})
    
    df = pd.DataFrame(values)
    display(df)
    print(f'{name} ratio mean: ', np.mean(ratio_values))
    
    
  ## This method calulate the sortino ratio value
  def SortinoRatio(self, returns, risk_free_rate, target_return=0):
      downside_returns = np.minimum(returns - target_return, 0)
      downside_std = np.std(downside_returns)
      
      if downside_std == 0:
          return np.nan
      
      return (returns.mean() - risk_free_rate) / downside_std

  def CalculateAccumulatedTotalReturn(self, num_months, start_year, annual_inflation):
    total = self.initial_capital
    for month in range(1, num_months):
      
      total = total + self.monthly_contribution
      if month % 12 == 0:
        current_year = int(start_year) + (month // 12) - 1
        inflation_rate = self.GetInflationRate(current_year, annual_inflation)
        total = total - (total * inflation_rate) / 100
    return total

  def CalculateBetasAplhas(self, annualized_return, risk_free_rate, array_volatility, df_timelines, start_year, data, annual_inflation):
    betas = []
    alphas = []
    for index, strategy_return in enumerate(annualized_return):
      cov = strategy_return - risk_free_rate
      var_market = array_volatility[0]['volatility (%)'] ** 2
      beta = cov / var_market
      capital = self.CalculateAccumulatedTotalReturn(len(data[index]['operations']['Date']), start_year, annual_inflation)
      total_return = self.TotalReturn(df_timelines[index], f'Period {index}')['total']
      profit = (total_return - capital) / total_return * 100
      alpha = profit - (risk_free_rate + beta * (strategy_return - risk_free_rate))
      betas.append(beta)
      alphas.append(alpha)
      
    return [betas, alphas]


  ### This method calculated the porfolio concentration
  def CalculatePorfolioConcentratio(self, fund_percentage_change):
    largest_investments = sorted(fund_percentage_change, reverse=True)[:5]
    total_largest_investments = sum(largest_investments)
    total_fund_value = sum(fund_percentage_change)
    return (total_largest_investments / total_fund_value) * 100
    