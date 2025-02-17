import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import date

def user_input_features():
    mortgage = st.sidebar.number_input('Loan Amount', 50_000, 50_000_000, 1_250_000)
    interest = st.sidebar.number_input('Interest Rate %', 0.0, 20.0, 9.5)
    years = st.sidebar.slider('Term of Loan', 5, 30, 20)
    start_date = st.sidebar.date_input('Purchase Date')
    data = {
        'mortgage': mortgage, 
        'interest': interest,
        'years': years,
        'start_date': start_date}
    features = pd.DataFrame(data, index=[0])
    return features

st.sidebar.header('Mortgage Parameters')

parameters = user_input_features()

mortgage = parameters.mortgage[0]
interest = parameters.interest[0] / 100
years = parameters.years[0]
start_date = parameters.start_date[0]

# Mortgage Calculator Variables
payments_year = 12
cumulative_interest = 0

# Monthly Payment
pmt = -1 * npf.pmt(interest / 12, years * payments_year, mortgage)

# Creating DataFrame
rng = pd.date_range(start_date, periods=years * payments_year, freq='MS')
rng.name = "Payment Date"

df = pd.DataFrame(index=rng,
                  columns=['Payment',
                           'Principal Paid',
                           'Interest Paid',
                           'Ending Balance',
                           'Cumulative Interest'],
                  dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"

# Ensure columns are float64 before assignments
df["Ending Balance"] = df["Ending Balance"].astype(float)
df["Cumulative Interest"] = df["Cumulative Interest"].astype(float)

df["Payment"] = -1 * npf.pmt(interest / payments_year, years * payments_year, mortgage)
df["Principal Paid"] = -1 * npf.ppmt(interest / payments_year, df.index, years * payments_year, mortgage)
df["Interest Paid"] = -1 * npf.ipmt(interest / payments_year, df.index, years * payments_year, mortgage)
df = df.round(2)

df.loc[1, "Ending Balance"] = mortgage - df.loc[1, "Principal Paid"]

def handle_zero_balance(period):
    df.loc[period, ['Payment', 'Principal Paid', 'Interest Paid', 'Ending Balance', 'Cumulative Interest']] = 0

for period in range(2, len(df) + 1):
    previous_balance = df.loc[period - 1, 'Ending Balance']
    principal_paid = df.loc[period, 'Principal Paid']

    if previous_balance == 0:
        handle_zero_balance(period)
        continue
    elif principal_paid <= previous_balance:
        df.loc[period, 'Ending Balance'] = previous_balance - principal_paid

df.loc[1, "Cumulative Interest"] = cumulative_interest + df.loc[1, 'Interest Paid']

for period in range(2, len(df) + 1):
    previous_cumulative = df.loc[period - 1, "Cumulative Interest"]
    interest_paid = df.loc[period, "Interest Paid"]

    if previous_cumulative == 0:
        handle_zero_balance(period)
        continue
    elif interest_paid <= previous_cumulative:
        df.loc[period, "Cumulative Interest"] = previous_cumulative + interest_paid

st.write("""
# Mortgage Calculator
Work out your **monthly payment** and ***cost of credit*** on a personal or business mortgage loan!
""")

st.header('Mortgage Parameters')
st.write(f"""
| Loan Amount               | Interest Rate %                   | Term of Loan in Years | Start Date                |
| ------------------------- |:---------------------------------:|:---------------------:|:-------------------------:|
| {mortgage} | {parameters.interest[0]} | {years} | {start_date} |
""")

st.header('Monthly Payment Breakdown')
st.line_chart(df[["Payment", "Principal Paid", "Interest Paid"]])

st.write(f"""
| Component                 | First                     | Final                              |
| --------------------------|:-------------------------:| ----------------------------------:|
| Monthly Mortgage Payment  | {int(pmt)}  | {int(pmt)}          |
| Interest Payment          | {int(df['Interest Paid'].iloc[0])} | {int(df['Interest Paid'].iloc[-1])} |
| Principal Payment         | {int(df['Principal Paid'].iloc[0])} | {int(df['Principal Paid'].iloc[-1])} |
""")

st.header('Cost of Credit')
st.line_chart(df[["Ending Balance", "Cumulative Interest"]])

st.write(f"""
| Capital Borrowed          | Cumulative Interest                | Total Repayment                       |
| --------------------------|:---------------------------------:|:------------------------------------:|
| {mortgage} | {int(df['Cumulative Interest'].iloc[-1])}  | {int(mortgage + df['Cumulative Interest'].iloc[-1])} |
""")

st.header("Amortization Table")
st.write(df)
