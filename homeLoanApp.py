import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import date


def user_input_features():
    mortgage = st.sidebar.number_input('Loan Amount', 250_000, 5_000_000, 1_250_000)
    interest = st.sidebar.number_input('Interest Rate %', 0.0, 20.0, 9.5)
    years = st.sidebar.slider('Term of Loan', 5, 30, 20)
    start_date = st.sidebar.date_input('Purchase Date')
    data = {
        'mortgage':mortgage, 
        'interest':interest,
        'years': years,
        'start_date': start_date}
    features = pd.DataFrame(data, index=[0])
    return features

st.sidebar.header('Mortgage Parameters')

parameters = user_input_features()

mortgage = parameters.mortgage[0]
interest = parameters.interest[0]/100
years = parameters.years[0]
start_date = parameters.start_date[0]

# Mortgage Calculator Variables

# interest = 0.084
# years = 30
payments_year = 12
# mortgage = 2000000
# start_date = (date(2021, 1, 1))
cumulative_interest = 0

# Monthly Payment
pmt = -1 * npf.pmt(interest/12, years*payments_year, mortgage)

# Interest Payment
ipmt = -1 * npf.ipmt(interest/payments_year, 1, years * payments_year, mortgage)

# Principal Payment
ppmt = -1 * npf.ppmt(interest/payments_year, 1, years * payments_year, mortgage)

# Creating Dataframe

rng = pd.date_range(start_date, periods=years * payments_year, freq='MS')
rng.name = "Payment Date"

df = pd.DataFrame(index=rng,
                  columns=['Payment',
                           'Principal Paid',
                           'Interest Paid',
                           'Ending Balance'],
                  dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"

df["Payment"] = -1 * npf.pmt(interest/payments_year, years * payments_year, mortgage)
df["Principal Paid"] = -1 * npf.ppmt(interest/payments_year, df.index, years * payments_year, mortgage)
df["Interest Paid"] = -1 * npf.ipmt(interest/payments_year, df.index, years * payments_year, mortgage)
df = df.round(2)

df["Ending Balance"] = 0
df.loc[1, "Ending Balance"] = mortgage - df.loc[1, "Principal Paid"]


for period in range(2, len(df)+1):
    previous_balance = df.loc[period-1, 'Ending Balance']
    principal_paid = df.loc[period, 'Principal Paid']

    if previous_balance == 0:
        df.loc[period,
               ['Payment',
                'Principal Paid',
                'Interest Paid',
                'Ending Balance'
                'Cumulative Interest']
               ] == 0
        continue
    elif principal_paid <= previous_balance:
        df.loc[period, 'Ending Balance'] = previous_balance - principal_paid

df["Cumulative Interest"] = 0
df.loc[1, "Cumulative Interest"] = cumulative_interest + df.loc[1, 'Interest Paid']

for period in range(2, len(df)+1):
    previous_cumulative = df.loc[period-1, "Cumulative Interest"]
    interest_paid = df.loc[period, "Interest Paid"]
    final_principal_paid = df.loc[period, "Principal Paid"]
    

    if previous_cumulative == 0:
        df.loc[period,
               ['Payment',
                'Principal Paid',
                'Interest Paid',
                'Ending Balance'
                'Cumulative Interest']
               ] == 0
        continue
    elif interest_paid <= previous_cumulative:
        df.loc[period, "Cumulative Interest"] = previous_cumulative + interest_paid

st.write("""
# Mortgage Calculator
Work out your **monthly payment** and ***cost of credit*** on a personal or business mortgage loan!
""")

st.header('Mortgage Parameters')

st.write('''
| Loan Amount               | Interest Rate %                       | Term of Loan in Years | Start Date                |
| ------------------------- |:-------------------------------------:|:---------------------:|:-------------------------:|
| ''' + str(mortgage) + ''' |''' + str(parameters.interest[0]) + '''|''' + str(years) + ''' |''' + str(start_date) + '''|
''')

st.header('Cost of Credit')

st.line_chart(df[["Ending Balance", "Cumulative Interest"]])

st.write('''
| Capital Borrowed          | Cumulative Interest                       |
| --------------------------|:-----------------------------------------:|
| ''' + str(mortgage) + ''' |''' + str(int(previous_cumulative)) + '''  |
''')

st.header('Monthly Payment Breakdown')

st.line_chart(df[["Payment", "Principal Paid", "Interest Paid"]])

st.write('''
| Component                 | First                     | Final                                |
| --------------------------|:-------------------------:| ------------------------------------:|
| Monthly Mortgage Payment  |''' + str(int(pmt)) + '''  | ''' + str(int(pmt)) + '''                 |
| Interest Payment          |''' + str(int(ipmt)) + ''' | ''' + str(int(interest_paid)) + '''       |
| Principle Payment         |''' + str(int(ppmt)) + ''' | ''' + str(int(final_principal_paid)) + '''|
''')


st.header("Amortization Table")
st.write(df)


