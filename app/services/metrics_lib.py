from app.services.json_service import add_operation_to_json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from app.services.database_service import create_strategy_record, create_operation, updateInvestmentProfileStrategy

class Metrics:
  def __init__(self, initial_capital, monthly_contribution, strategy_id, profile_id, comission):
    self.initial_capital = initial_capital
    self.monthly_contribution = monthly_contribution
    self.strategy_id = strategy_id
    self.profile_id = profile_id
    self.comission = comission
  
  ### Operations in the db
  def InitStrategy(self, name, description, model):
    create_strategy_record(name, description, model)
    
  ## Saving Operation in the db
  def CreateOperation(self, init, end, price, total, profit, period):
    data = {'init': init, 'end': end, 'price': price, 'total': total, 'profit': profit, 'period': period}
    create_operation(self.strategy_id, self.profile_id, data)
    
  def UpdateInvestmentProfileStrategy(self, total_returns, volatility_values, max_loss_values, sharpe_ratio_values, sortino_ratio_values, alphas, betas, information_ratio_data, success_rate, portfolio_concentration_rate):
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
    updateInvestmentProfileStrategy(self.strategy_id, self.profile_id, data)
    

  ## This method calculate the total return of one active
  def TotalReturn(self, df_timeline, period, initial_capital=None):
    if (initial_capital is None): initial_capital = self.initial_capital
    operations = pd.DataFrame(columns=['Date', 'Price', 'Total'])
    total_return = initial_capital - (initial_capital * self.comission / 100)
    for _, row in df_timeline.iterrows():
      # Prive movement. 1 -> 100% and -1 -> -100%
      movement = (row['Close'] - row['Open']) / row['Open']
      total_return += total_return * movement
      total_return += self.monthly_contribution - (self.monthly_contribution * self.comission / 100)
      if not pd.isna(row['Dividends']):
        total_return += total_return * row['Dividends'] / 100 
      # Operation
      operations.loc[len(operations)] = {
        'Date': row['Date'],
        'Price': row['Open'],
        'Total': total_return,
        'Period': period
      }
      self.CreateOperation(
        str(row['Date']),
        '',
        str(row['Open']),
        total_return,
        '',
        period
      )
    return {
      'total': total_return,
      'operations': operations
    }
    
  ## This function show the acive performance 
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
    

  ## This method calculate the annualized return of one active
  def AnnualizedReturn(self, df, start_year, end_year, period):
    total_annual_profit = []
    capital = self.initial_capital + self.monthly_contribution * 12
    for year in range(start_year, end_year + 1):
      filtered_data = df.loc[df['Date'].dt.year == year]
      total_return_after_one_year = self.TotalReturn(filtered_data, period, capital)
      capital += self.monthly_contribution * 12
      variation = (total_return_after_one_year['total'] - capital) / capital * 100
      capital = total_return_after_one_year['total']
      total_annual_profit.append({
        'year': year,
        'variation': variation
      })
    return total_annual_profit

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
    