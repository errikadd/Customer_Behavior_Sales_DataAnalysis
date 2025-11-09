from dash import Dash, html, dcc, Input, Output, Patch, clientside_callback, callback
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
import requests
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template



# Loading the data using pandas
data = pd.read_csv('../data\\EcommData_CSV_cleaned.csv', delimiter = ',')

# Initializing the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME])
server = app.server  # Flask server

# Allow iframe embedding
@server.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

# Dashboard Title
app.title = "Customer Behavior and Sales Dashboard"

# Loading the "sketchy" template and setting it as the default
load_figure_template("cyborg") 

# List of years 
year_list = [i for i in range(2022, 2025, 1)]

# Color palette base: px.colors.sequential.Plasma
palette=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921']


#---------------------------------------------------------------------------------------

# --- Dropdown menu options ---
dropdown_options = [
    {'label': 'Customer Behavior Report', 'value': 'Customer Behavior Report'}, 
    {'label': 'Sales Report', 'value': 'Sales Report'} 
]


#---------------------------------------------------------------------------------------

# --- App Layout ---
app.layout = dbc.Container([ 
    # --- Dashboard Title ---
    dbc.Row([
        dbc.Col(
            html.H1('Customer Behavior and Sales Dashboard', className='text-center my-4', style={'color': '#4000c1', 'font-weight': 'regular'}),
            width=12
        )
    ]),

    # --- Dropdown Section ---
    dbc.Row([
        # Report selection dropdown
        dbc.Col([
            dbc.Label('Select Report:', className='fw-bold text-secondary mb-2', style={'fontSize': '20px'}),
            dcc.Dropdown(
                id='dropdown-report',
                options=[
                    {'label': 'Customer Behavior Report', 'value': 'Customer Behavior Report'},
                    {'label': 'Sales Report', 'value': 'Sales Report'}
                ],
                value='Select Report',
                placeholder='Select a report type',
                className='mb-4',
                style={'fontSize': '20px'}
            )
        ], md=4),

        # Year selection dropdown
        dbc.Col([
            dbc.Label('Select Year:', className='fw-bold text-secondary mb-2', style={'fontSize': '20px'}),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': i, 'value': i} for i in year_list],
                value='Select-year',
                placeholder='Select year',
                className='mb-4',
                style={'fontSize': '20px'}
            )
        ], md=4),
    ], className='justify-content-center'),

    html.Hr(),
    
    # --- Output Section ---
  
    dbc.Row([
        dbc.Col(
            html.Div(id='output-container', className='p-3 border rounded shadow-sm'),
            width=12
        )
    ])
 

], fluid=True, className='p-4')


#---------------------------------------------------------------------------------------
# Callback for plotting: update the output container based on the selected report
@app.callback(
    Output('output-container', 'children'),
    Input('dropdown-report', 'value'),
    Input('select-year', 'value'),
    prevent_initial_call=True  # prevents callback from firing before user interacts
    )

def update_output_container(selected_report, input_year):
    # Case 1: No report selected
    if not selected_report or selected_report == 'Select Report':
        return html.Div(
            'Please select a report type to begin.',
            style={'textAlign': 'center', 'color': '#959595', 'fontSize': 24, 'margin': '50px'}
        )

    # Case 2: Report selected, no year selected
    if not input_year or input_year == 'Select-year':
        return html.Div(
            'Please select a year to view the data.',
            style={'textAlign': 'center', 'color': '#959595', 'fontSize': 24, 'margin': '50px'}
        )
    

    # Check the input year
    yearly_data = data[data['Year'] == input_year]


    # ---------- Customer Behavior Report ---------- 
    if selected_report=='Customer Behavior Report':

# Customer Behavior Report Graphs:
        # ---------- KPI CARDS ----------
        # Calculating key metrics
        total_unique_customers = yearly_data['Customer ID'].nunique()
        avg_purchase = yearly_data['Purchase Amount (USD)'].mean()

        # Formatting the numbers
        total_customers_fmt = f'{total_unique_customers:,}'  # comma as thousands separator
        avg_purchase_fmt = f'${avg_purchase:,.2f}'

        # Creating KPI summary cards
        kpi_cards1 = html.Div([
            html.Div([
                html.H5(f'Total Customers in {input_year}', 
                        style={'color': '#ffffff', 'font-weight': 'bold', 'margin-bottom': '5px', 'font-size': '18px'}),
                html.H2(total_customers_fmt, 
                        style={'color': '#4000c1', 'font-weight': 'bold', 'font-size': '60px'})
            ], className='kpi_cards_inner'),

            html.Div([
                html.H5(f'Average Purchase Value in {input_year}', 
                        style={'color': '#ffffff', 'font-weight': 'bold', 'margin-bottom': '5px', 'font-size': '18px'}),
                html.H2(avg_purchase_fmt, 
                        style={'color': '#4000c1', 'font-weight': 'bold', 'font-size': '60px'})
            ], className='kpi_cards_inner')
        ], className='kpi_cards_outer')


# 1) Number of Total Customers Vs Subscribed Customers
        # Total unique customers
        total_customers = yearly_data['Customer ID'].nunique()

        # Unique subscribed customers
        subscribed_customers = yearly_data[yearly_data['Subscription Status'] == 1]['Customer ID'].nunique()

        # DataFrame
        df_pie = pd.DataFrame({'Customer Type': ['Subscribed', 'Not Subscribed'], \
                               'Count': [subscribed_customers, total_customers - subscribed_customers]})
        
        # Pie chart
        fig1 = px.pie(
            df_pie,
            values='Count',
            names='Customer Type',
            color='Customer Type',
            color_discrete_sequence=['#bd3786', '#46039f']
        )
        
        fig1.update_layout(title={
            'text': 'Total Customers vs Subscribed Customers in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff'))
        
        customers_chart1 = dcc.Graph(figure=fig1)


# 2) Promo Code Usage (Ever Used vs Never Used)
        # Total unique customers
        total_customers = yearly_data['Customer ID'].nunique()

        # Customers who used promo code
        promo_used_customers = yearly_data[yearly_data['Promo Code Used'] == 1]['Customer ID'].nunique()

        # DataFrame
        df_bar = pd.DataFrame({'Customer Type': ['Promo Code Used', 'Promo Code Not Used'], \
                               'Count': [promo_used_customers, total_customers - promo_used_customers]})
        
        # Bar chart
        fig2 = px.bar(
            df_bar,
            x='Customer Type',
            y='Count',
            labels={'Customer Type': 'Customer Type', 'Count': 'Number of Customers'},
            color = 'Customer Type',
            color_discrete_sequence = ['#46039f', '#bd3786']
        )

        fig2.update_layout(title={
            'text': 'Promo Code Usage by Unique Customers in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff'),
            plot_bgcolor='#282828'
        )

        customers_chart2 = dcc.Graph(figure=fig2)


# 3) Customer Distribution by Location
        # Unique customers by location
        location_unique = (
            yearly_data.groupby(['Location', 'Latitude', 'Longitude'])['Customer ID']
            .nunique()
            .reset_index(name='Unique Customers')
        )

        # Geo scatter plot
        fig3 = px.scatter_geo(
            data_frame=location_unique,
            lat='Latitude',
            lon='Longitude',
            size='Unique Customers',
            hover_name='Location',
            color='Unique Customers',
            projection='natural earth',
            color_continuous_scale=palette
        )

        fig3.update_traces(marker=dict(opacity=0.7))
        fig3.update_geos(scope='usa', projection_type='albers usa', bgcolor='#282828')
        fig3.update_layout(title={
                'text': 'Customer Distribution by Location in {}'.format(input_year),
                'x': 0.5,                
                'xanchor': 'center', 
                'y': 0.95,             
                'yanchor': 'top'},
                title_font=dict(size=18, weight='bold', color='#ffffff')
        )
        
        customers_chart3 = dcc.Graph(figure=fig3)


# 4) Customer Review Rates Distribution
        df_review_rates = yearly_data.groupby('Review Rating').size().reset_index(name='Count')
        
        # Converting the Review Rating column to a categorical type with custom order
        review_rates_order = ['5.0', '4.5', '4.0', '3.5', '3.0', '2.5', '2.0', '1.5', '1.0']
        df_review_rates['Review Rating'] = df_review_rates['Review Rating'].astype(str)
        df_review_rates['Review Rating'] = pd.Categorical(
        df_review_rates['Review Rating'],
        categories=review_rates_order,
        ordered=True
        )
        df_review_rates = df_review_rates.sort_values('Review Rating')

        # Pie chart
        fig4 = px.pie(
            df_review_rates,
            values='Count',
            names='Review Rating',
            color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'],
            category_orders={'Review Rating': review_rates_order}
        )
        
        fig4.update_layout(title={
            'text': 'Customer Review Rates Distribution in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff')
        )
        
        customers_chart4 = dcc.Graph(figure=fig4)


        return [
            # KPI cards row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(kpi_cards1)
                    ], className='shadow-sm border-0'),
                    md=12, xs=12, className='mb-4'
                )
            ], className='g-4'),

            # Charts: first row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(customers_chart1)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(customers_chart2)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                )
            ], className='g-4'),

            # Charts: second row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(customers_chart3)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(customers_chart4)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                )
            ], className='g-4')
        ]





    # ---------- Sales Report ----------                             
    elif selected_report=='Sales Report':

# Sales Report Graphs:
        # ---------- KPI CARDS ----------
        # Calculating key metrics
        total_sales = yearly_data['Purchase Amount (USD)'].sum()
        avg_purchase = yearly_data['Purchase Amount (USD)'].mean()

        # Formatting the numbers
        total_sales_fmt = f'${total_sales:,.2f}'
        avg_purchase_fmt = f'${avg_purchase:,.2f}'

        # Creating KPI summary cards
        kpi_cards2 = html.Div([
            html.Div([
                html.H5(f'Total Sales in {input_year}', 
                        style={'color': '#ffffff', 'font-weight': 'bold', 'margin-bottom': '5px', 'font-size': '18px'}),
                html.H2(total_sales_fmt, 
                        style={'color': '#4000c1', 'font-weight': 'bold', 'font-size': '60px'})
            ], className='kpi_cards_inner'),

            html.Div([
                html.H5(f'Average Order Value in {input_year}', 
                        style={'color': '#ffffff', 'font-weight': 'bold', 'margin-bottom': '5px', 'font-size': '18px'}),
                html.H2(avg_purchase_fmt, 
                        style={'color': '#4000c1', 'font-weight': 'bold', 'font-size': '60px'})
            ], className='kpi_cards_inner')
        ], className='kpi_cards_outer')


# 5) Total Monthly Sales
        monthly_sales = yearly_data.groupby('Month')['Purchase Amount (USD)'].sum().reset_index()

        # Custom month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Line chart
        fig5 = px.line(
            monthly_sales,
            x='Month',
            y='Purchase Amount (USD)',
            labels={'Month': 'Month', 'Purchase Amount (USD)': 'Sales (USD)'},
            markers=True  # circle markers
        )

        fig5.update_traces(line=dict(color='#0d0887', width=3), marker=dict(size=8, symbol='circle'))
        fig5.update_xaxes(showgrid=False) # removes vertical grid lines
        fig5.update_layout(
            title={
            'text': 'Total Monthly Sales in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff'), 
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),  
                ticktext=month_labels),
            yaxis_title='Sales (USD)',
            xaxis_title='Month',
            plot_bgcolor='#282828',
            hovermode='x unified'
        )

        sales_chart1 = dcc.Graph(figure=fig5)


# 6) Seasonal Trends
        seasonal_sales = yearly_data.groupby('Season')['Purchase Amount (USD)'].sum().reset_index()
        
        # Converting the Season column to a categorical type with custom order
        season_order = ['Winter', 'Spring', 'Summer', 'Fall']
        seasonal_sales['Season'] = pd.Categorical(seasonal_sales['Season'],categories=season_order,ordered=True)
        seasonal_sales = seasonal_sales.sort_values('Season')

        # Line chart 
        fig6 = px.line(
            seasonal_sales,
            x='Season',
            y='Purchase Amount (USD)',
            labels={'Season': 'Season', 'Purchase Amount (USD)': 'Sales (USD)'},
            category_orders={'Season': season_order},  # correct order
            markers=True  # circle markers
        )

        fig6.update_traces(line=dict(color='#0d0887', width=3), marker=dict(size=8, symbol='circle'))
        fig6.update_xaxes(showgrid=False) # removes vertical grid lines
        fig6.update_layout(
            title={
            'text': 'Total Seasonal Sales in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff'),
            yaxis_title='Sales (USD)',
            xaxis_title='Season',
            plot_bgcolor='#282828',
            hovermode='x unified'
        )

        sales_chart2 = dcc.Graph(figure=fig6)


# 7) Total Sales by State
        # Loading US states GeoJSON
        url = 'https://r2.datahub.io/clt98p6iw000fjm08obqajter/main/raw/data/admin1-us.geojson'
        geojson = requests.get(url).json() 

        # Grouping purchase amount per state and calculating the sum
        sales_by_state = yearly_data.groupby('Location', as_index=False)['Purchase Amount (USD)'].sum()

        # Choropleth plot
        fig7 = px.choropleth(
            sales_by_state,
            geojson=geojson,
            locations='Location', 
            featureidkey='properties.name', # key in the geojson
            color='Purchase Amount (USD)',
            color_continuous_scale=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'], 
            scope='usa',
        )

        fig7.update_geos(scope='usa', fitbounds='locations', visible=False, bgcolor='#282828')
        fig7.update_layout(title={
            'text': 'Total Sales by State in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff'),
            coloraxis_colorbar=dict(
            title='Total Sales (USD)')
        )

        sales_chart3 = dcc.Graph(figure=fig7)


# 8) Products and Their Categories
        top_products = yearly_data.groupby(['Category', 'Item Purchased'], as_index=False)['Purchase Amount (USD)'].sum()
        top_products_sorted = top_products.sort_values(
            by=['Category', 'Item Purchased'],
            ascending=[True, False]
        )

        # Sunburst plot
        fig8 = px.sunburst(
            top_products_sorted,
            path=['Category', 'Item Purchased'],   
            values='Purchase Amount (USD)',
            color_discrete_sequence=['#0d0887', '#9c179e', '#ed7953', '#f0f921']
        )

        fig8.update_layout(title={
            'text': 'Products and Their Categories in {}'.format(input_year), 
            'x': 0.5, 
            'xanchor': 'center',
            'y': 0.95, 
            'yanchor': 'top'}, 
            title_font=dict(size=18, weight='bold', color='#ffffff')
        )

        sales_chart4 = dcc.Graph(figure=fig8)


        return [
            # KPI cards row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(kpi_cards2)
                    ], className='shadow-sm border-0'),
                    md=12, xs=12, className='mb-4'
                )
            ], className='g-4'),

            # Charts: first row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(sales_chart1)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(sales_chart2)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                )
            ], className='g-4'),

            # Charts: second row
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(sales_chart3)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(className='fw-bold'),
                        dbc.CardBody(sales_chart4)
                    ], className='shadow-sm border-0'),
                    md=6, xs=12, className='mb-4'
                )
            ], className='g-4')
        ]


    

    # ---------- Fallback ----------
    else:
        return html.Div('Please select a report and year to view the data.', 
                    style={'textAlign': 'center', 'color': '#959595', 'fontSize': 24, 'margin': '50px'})







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)