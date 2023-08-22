import dash
import pandas as pd
import numpy as np
import random
from dash.dependencies import Input, Output, State
from dash import html, dcc
from dash import dash_table
import dash_table
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import time
css_file_path = os.path.abspath('custom.css')
import pandas as pd
import random

# Generate mock data
n = 100  # number of rows

# Create random product strings
product_full_names = {
    'AN': 'Anesthesiology',
    'CV': 'Cardiovascular',
    'CH': 'Clinical Chemistry',
}
def generate_random_product_string():
    key = random.choice(list(product_full_names.keys()))
    return f"{key} - {product_full_names[key]}"
# Generate data
data = {
    'Company name': [f'Company_{i}' for i in range(n)],
    'Product Strings': [generate_random_product_string() for _ in range(n)],
    'Total Invested Equity': [random.uniform(0, 200) for _ in range(n)],
    'Pre-money Valuation': [random.uniform(100, 500) for _ in range(n)],
    'Post Valuation': [random.uniform(500, 1000) for _ in range(n)],
    'Founded Year': [random.randint(1980, 2020) for _ in range(n)],
    'Current Employees': [random.randint(1, 500) for _ in range(n)],
    'Total Patent Documents': [random.randint(1, 100) for _ in range(n)],
    'Company Website': [f'www.company_{i}.com' for i in range(n)]
}

# Create dataframe
df = pd.DataFrame(data)
print(df.head)

external_stylesheets = [
    {'href': 'https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css'},
    {'href': 'https://cdn.jsdelivr.net/npm/skeleton@2.0.4/dist/skeleton.min.css'}
]
# Read the data from the CSV file


colors = ["white", "lightgreen"]  # Change this to any colors you want
cmap = mcolors.LinearSegmentedColormap.from_list("", colors)
product_strings_list = list(product_full_names.keys())
current_year = 2023


df['Product Strings'] = df['Product Strings'].astype(str)
df = df.dropna(subset=['Product Strings'])
df = df.dropna(subset=['Total Invested Equity'])
def abbrev_to_full(product_list):
    return [product_full_names[i] if i in product_full_names else i for i in product_list]
df_graph = df.copy()
df['Sectors'] = df['Product Strings'].str.split(',').apply(abbrev_to_full).apply(', '.join)
df['Pre-money Valuation'] = pd.to_numeric(df['Pre-money Valuation'], errors='coerce')
df['Post Valuation'] = pd.to_numeric(df['Post Valuation'], errors='coerce')
df['Percentage Valuation Increase'] = ((df['Post Valuation'] - df['Pre-money Valuation']) / df['Pre-money Valuation']) * 100
df['Founded Year']=df['Founded Year'].astype(float)

df['Years in Operation'] = current_year - df['Founded Year']
df['Years in Operation'] = df['Years in Operation'].astype(float)

df['Valuation Increase Rate Over Time'] = df['Post Valuation'] / df['Years in Operation']
df['Valuation Increase Rate Over Time'] = df['Valuation Increase Rate Over Time'].round(2)
df = df.dropna(subset=['Percentage Valuation Increase'])
df = df.sort_values(by='Percentage Valuation Increase', ascending=False)
df = df.drop_duplicates(subset='Company name', keep='first')
df['Total Invested Equity per employee'] = df['Total Invested Equity'] / df['Current Employees']

df['Total Patent Documents'] = pd.to_numeric(df['Total Patent Documents'], errors='coerce').round(2)
df['Percentage Valuation Increase'] = df['Percentage Valuation Increase'].round(2)
df['Total Patent Documents'] = pd.to_numeric(
    df['Total Patent Documents'], errors='coerce').round(2)
df['Percentage Valuation Increase'] = df['Percentage Valuation Increase'].round(
    2)
df['Normalized Valuation Increase'] = df['Percentage Valuation Increase'] / \
    df['Percentage Valuation Increase'].max()
df['Normalized Current Employees'] = df['Current Employees'] / \
    df['Current Employees'].max()
df['Normalized Total Patent Documents'] = df['Total Patent Documents'] / \
    df['Total Patent Documents'].max()
# Compute the final rank
df['Rank'] = df['Normalized Valuation Increase'] + df['Normalized Current Employees'] + \
    df['Normalized Total Patent Documents']

df['Sectors'] = df['Sectors'].replace('nan', 'Not categorized')

min_rank = df['Rank'].min()
max_rank = df['Rank'].max()
def color_rank(x):
    if np.isnan(x):  # If rank is NaN, return white
        return mcolors.to_hex('white')
    else:
        return mcolors.to_hex(cmap((x - min_rank) / (max_rank - min_rank)))


df['Rank Color'] = df['Rank'].apply(color_rank)

df['Rank']= df['Rank'].round(2)
categories = sorted(product_full_names.values())
equity_buckets = ['1-5 Million', '5-10 Million',
                  '11-50 Million', '51-150 Million', '151-above Million']

df["Company Website"] = df["Company Website"].apply(lambda x: f"[{x}](http://{x})")
#Own function, because code didn't work
def equity_bucket_by_company(row):
    total_invested_equity = row['Total Invested Equity']
    if pd.notna(total_invested_equity):
        if total_invested_equity <= 5:
            return '1-5'
        elif 5 < total_invested_equity <= 10:
            return '5-10'
        elif 10 < total_invested_equity <= 50:
            return '11-50'
        elif 50 < total_invested_equity <= 150:
            return '51-150'
        else:
            return '151-above'
    else:
        return 'Unknown'

df['Equity Bucket'] = df.apply(equity_bucket_by_company, axis=1)

df_graph['Equity Bucket'] = df_graph.apply(equity_bucket_by_company, axis=1)
highest_valuation_df = df.groupby('Company name')['Post Valuation'].max().reset_index()
merged_df2 = highest_valuation_df.merge(df[['Company name', 'Years in Operation', 'Product Strings', 'Equity Bucket']], on='Company name', how='left').drop_duplicates()

df['Pre-money Valuation'] = pd.to_numeric(df['Pre-money Valuation'], errors='coerce')
df['Post Valuation'] = pd.to_numeric(df['Post Valuation'], errors='coerce')

df['Valuation Increase Percentage'] = -1 * (df['Pre-money Valuation'] - df['Post Valuation']) / df[
    'Pre-money Valuation']*100
app = dash.Dash(__name__)
desired_order = ['1-5','5-10', '11-50', '51-150', '151-above', 'Unknown']
dropdown_equity_options = [{'label': bucket, 'value': bucket} for bucket in desired_order]

dropdown_equity_default_value = desired_order[0]

def custom_sorting(data, sort_by):
    if not sort_by:
        return data.to_dict('records')

    for sort_val in sort_by:

        col_id = sort_val['column_id']
        ascending = sort_val['direction'] == 'asc'
        na_position = 'first' if ascending else 'last'
        if col_id == 'FDA':
            data = data.sort_values(
                by=['Regulatory_rank'], ascending=ascending, na_position=na_position)
        else:
            data = data.sort_values(
                by=[col_id], ascending=ascending, na_position=na_position)

    # return sorted(data, key=lambda x: x[col_id], reverse=not ascending)
    return data.to_dict('records')

def get_full_names(combined_abbreviations):
    abbreviations = combined_abbreviations.split(',')
    full_names = [product_full_names[abbreviation] for abbreviation in abbreviations if abbreviation in product_full_names]
    return ', '.join(full_names)

def get_unique_product_types(df):
    unique_product_types = set()
    for product_string in df['Product Strings']:
        if pd.notna(product_string)and product_string != 'nan':
            product_types = product_string.split(',')
            unique_product_types.update(product_types)
    return sorted(list(unique_product_types))

#dropdown_product_options = [{'label': product_full_names[product], 'value': product} for product in get_unique_product_types(df)]
#dropdown_product_options = [{'label': product_full_names[product], 'value': product_full_names[product]} for product in get_unique_product_types(df)]
dropdown_product_options = [{'label': product, 'value': product} for product in get_unique_product_types(df)]


dropdown_product_default_value = df['Product Strings'].unique()[0]
cmp = None

categories = list(product_full_names.values())
equity_buckets = desired_order

expanded_rows = []

for idx, row in df.iterrows():
    sectors = row['Sectors'].split(', ')
    for sector in sectors:
        new_row = row.copy()
        new_row['Sectors'] = sector
        expanded_rows.append(new_row)

df_expanded = pd.DataFrame(expanded_rows)

df_expanded['Label'] = df_expanded['Company name'] + "<br>" + df_expanded['Total Invested Equity'].astype(str)

sector_aggregate = df_expanded.groupby('Sectors')['Total Invested Equity'].sum().reset_index()

sector_aggregate_dict = sector_aggregate.set_index('Sectors').to_dict()['Total Invested Equity']

df_expanded['Sectors'] = df_expanded['Sectors'].map(lambda x: f"{x} {sector_aggregate_dict[x]:.2f}")

fig2 = px.treemap(df_expanded, path=['Sectors', 'Label'], values='Total Invested Equity')
fig2.update_traces(textfont=dict(color='black'))
fig2.update_layout(
    autosize=True,
    margin=dict(t=0, b=0, l=0, r=0)
)

app.layout = html.Div([

    html.Div(id='table-overlay', style={'position': 'absolute', 'top': '225px', 'left': '120px'}),
    html.Div(style={'height': '3px'}),
    dcc.Dropdown(
        id='product-dropdown',
        options=dropdown_product_options,
        value=dropdown_product_default_value
    ),
    
    html.Div(style={'height': '12px'}),
    html.Label("Select Total Money Raised: $ Millions "),
    html.Div(style={'height': '3px'}),
    dcc.Dropdown(
        id='bucket-dropdown',
        options=dropdown_equity_options,
        value=dropdown_equity_default_value
    ),
    html.Div(style={'height': '12px'}),
    html.Div(style={'height': '20px'}),
    html.Div(id='company-info'),
    html.Div(id='last-clicked', style={'display': 'none'}),

    html.P(f'Valuation Table of the selected sector'),
dash_table.DataTable(
    id='valuation-table',
    style_table={'overflowX': 'auto', 'border': '1px solid #ddd',
                 'borderCollapse': 'collapse', 'width': '100%', 'margin': 'auto'},
    style_cell={'fontFamily': 'Arial, sans-serif', 'textAlign': 'left', 'padding': '6px',
                'border': '1px solid #ddd', 'backgroundColor': '#f2f2f2', 'transition': 'background-color 0.2s ease-in-out', 'textAlign': 'center', 'verticalAlign': 'middle'},
    style_header={'backgroundColor': '#333', 'color': 'white',
                  'fontWeight': 'bold', 'border': '1px solid #ddd','whiteSpace': 'normal','height': 'auto', 'textAlign': 'justify','verticalAlign': 'top'},
    columns=[
        {"name": "Company name", "id": "Company name"},
        {"name": "Operating Duration", "id": "Years in Operation"},
        {"name": "Total Money Raised", "id": "Raised to Date"},
        {"name": "Valuation Increase Rate ($ Million/ year )", "id": "Valuation Increase Rate Over Time"},
        {"name": "Rank", "id": "Rank", "type": 'numeric'},
        # {"name": "Test", "id": "test_null"},
    ],
    data=df.to_dict('records'),
    style_data_conditional=style_data,  # Add this line to include the style data
    sort_action='custom',  
    sort_mode='multi',
),

], style={'backgroundColor': 'white'})

app.css.append_css({
    'external_url': css_file_path
})
# Define callback to update the graph based on selected bucket and product category

@app.callback(
    Output('valuation-table', 'data'),
    Input('product-dropdown', 'value'),
    Input('bucket-dropdown', 'value'),
    Input('valuation-table', 'sort_by'),
    State('product-dropdown', 'value'),
    State('bucket-dropdown', 'value')
)
def update_table(selected_product, selected_bucket, sort_by, persisted_product, persisted_bucket):
    # If no product is selected, use the persisted product state
    if not selected_product:
        selected_product = persisted_product

    # If no bucket is selected, use the persisted bucket state
    if not selected_bucket:
        selected_bucket = persisted_bucket

    # Filter data
    filtered_df = df[(df['Equity Bucket'] == selected_bucket) & (df['Product Strings'].str.contains(selected_product))]

    # Sorting mechanism
    sorted_df = custom_sorting(filtered_df, sort_by)
    
    # Update the styles based on the Rank Color column
    style_data = [
        {
            'if': {'row_index': i},
            'backgroundColor': color
        } for i, color in enumerate(sorted_df['Rank Color'])
    ]
    
    return sorted_df, style_data

if __name__ == '__main__':
    app.run_server(debug=True,port=8533)
    