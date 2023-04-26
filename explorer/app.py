from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/budget-data')
def budget_data():
    # Read budget data from a CSV or JSON file using pandas
    years = [2019,2020,2021,2022]
    budget_df = pd.DataFrame()
    for y in years:
        temp_df = pd.read_csv(f'data/menu-postings/{y}.csv')
        temp_df['year'] = y
        budget_df = budget_df.append(temp_df)

    budget_df['cost'] = budget_df['cost'].str.replace(',', '').str.replace('$', '')
    budget_df['cost'] = pd.to_numeric(budget_df['cost'])

    budget_df = budget_df[['ward','item','cost','year']]
    budget_df = budget_df.reset_index().drop('index',axis=1)
    budget_df.reset_index(inplace=True)

    # Convert the DataFrame to JSON and return it as a response
    budget_json = jsonify(budget_df.to_dict(orient='records'))
    print(budget_json)
    return budget_json

if __name__ == '__main__':
    app.run(debug=True)