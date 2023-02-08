# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
airline_data =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv', 
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str})

airline_data.rename(columns={'OriginStateFips':'Passengers','OriginWac':'NoShow'}, inplace=True)

# Create a dash application
app = dash.Dash(__name__)

# Build dash app layout
app.layout = html.Div(children=[ html.H1('US Domestic Airline Flights Performance', 
                                style={'textAlign': 'center', 'color': '#503D36',
                                'font-size': 30}),

                                html.Div(
                                    [
                                    html.Div(
                                    ["Report Type: ",
                                    dcc.Dropdown(
                                            id='report_type',
                                            options=[
                                            {'label': 'Yearly airline performance report', 'value': 'performance'},
                                            {'label': 'Yearly average flight delay statistics', 'value': 'avgdelay'}
                                            ],
                                            value='performance'
                                            ),],),

                                    html.Div(
                                    ["Choose Year: ",
                                    dcc.Dropdown(
                                            id='input_year',
                                            options=[
                                            {'label': '2005', 'value': '2005'},
                                            {'label': '2006', 'value': '2006'},
                                            {'label': '2007', 'value': '2007'},
                                            {'label': '2008', 'value': '2008'},
                                            {'label': '2009', 'value': '2009'},
                                            {'label': '2010', 'value': '2010'},
                                            {'label': '2011', 'value': '2011'},
                                            {'label': '2012', 'value': '2012'},
                                            {'label': '2013', 'value': '2013'},
                                            {'label': '2014', 'value': '2014'},
                                            {'label': '2015', 'value': '2015'},
                                            {'label': '2016', 'value': '2016'},
                                            {'label': '2017', 'value': '2017'},
                                            {'label': '2018', 'value': '2018'},
                                            {'label': '2019', 'value': '2019'},
                                            {'label': '2020', 'value': '2020'}                                            
                                            ],
                                            value='2005'
                                            ),],),
                                    ],),
                                html.Br(),
                                html.Br(),
                                # Segment 1
                                html.Div(dcc.Graph(id='row0-plot'), style={'width':'80%'}),
                                # Segment 2
                                html.Div([
                                        html.Div(dcc.Graph(id='row1col2-plot')),
                                        html.Div(dcc.Graph(id='row1col2-plot'))
                                ], style={'display': 'flex'}),
                                # Segment 3
                                html.Div([
                                        html.Div(dcc.Graph(id='row2col1-plot')),
                                        html.Div(dcc.Graph(id='row2col2-plot'))
                                ], style={'display': 'flex'})
                                ])

# Callback decorator
@app.callback( [
               Output(component_id='row0-plot', component_property='figure'),
               Output(component_id='row1col1-plot', component_property='figure'),
               Output(component_id='row1col2-plot', component_property='figure'),
               Output(component_id='row2col1-plot', component_property='figure'),
               Output(component_id='row2col2-plot', component_property='figure')
               ],
               Input(component_id='input_year', component_property='value'))

def compute_info(airline_data, entered_report, entered_year):
    # Select data
    df =  airline_data[airline_data['Year']==int(entered_year)]

    if entered_report == "performance":
        df_subset_1 = df.groupby(['Month','Reporting_Airline'])['NoShow'].mean().reset_index()
        df_subset_2 = df.groupby(['Month','Reporting_Airline'])['Distance'].mean().reset_index()
        df_subset_3 = df.groupby(['DestState','Reporting_Airline'])['Passengers'].mean().reset_index()
        df_subset_4 = df.groupby(['Month','Reporting_Airline'])['DepDelayMinutes'].mean().reset_index()
        df_subset_5 = df.groupby(['Month','Reporting_Airline'])['ActualElapsedTime'].mean().reset_index()
    else:
        # Compute delay averages
        df_subset_1 = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
        df_subset_2 = df.groupby(['Month','Reporting_Airline'])['CarrierDelay'].mean().reset_index()
        df_subset_3 = df.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
        df_subset_4 = df.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
        df_subset_5 = df.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()

    return df_subset_1, df_subset_2, df_subset_3, df_subset_4, df_subset_5

# Computation to callback function and return graph
def get_graph(entered_report, entered_year):
    # Compute required information for creating graph from the data
    df_subset_1, df_subset_2, df_subset_3, df_subset_4, df_subset_5 = compute_info(airline_data, entered_report, entered_year)
    if entered_report == "performance":
        # Treemap
        fig1 = px.treemap(df_subset_1, path=["Month"], values="NoShow", color="Reporting_Airline",
                            color_discrete_sequence=px.colors.qualitative.Dark2)
        # Pie chart
        fig2 = px.pie(df_subset_2, values="Distance", names="Reporting_Airline")
        # USA Map
        fig3 = px.choropleth(df_subset_3, locations="DestState", color="Passengers",
                               color_continuous_scale=px.colors.sequential.Plasma,
                               locationmode="USA-states")
        # Bar chart
        fig4 = px.bar(df_subset_4, x='Month', y='DepDelayMinutes', color='Reporting_Airline')
        # Line chart
        fig5 = px.line(df_subset_5, x='Month', y='ActualElapsedTime', color='Reporting_Airline')
    else:
        # Line plot for late aircraft delay
        fig1 = px.line(df_subset_1, x='Month', y='LateAircraftDelay', color='Reporting_Airline', title='Average late aircraft delay time (minutes) by airline')
        # Line plot for carrier delay
        fig2 = px.line(df_subset_2, x='Month', y='CarrierDelay', color='Reporting_Airline', title='Average carrrier delay time (minutes) by airline')
        # Line plot for weather delay
        fig3 = px.line(df_subset_3, x='Month', y='WeatherDelay', color='Reporting_Airline', title='Average weather delay time (minutes) by airline')
        # Line plot for nas delay
        fig4 = px.line(df_subset_4, x='Month', y='NASDelay', color='Reporting_Airline', title='Average NAS delay time (minutes) by airline')
        # Line plot for security delay
        fig5 = px.line(df_subset_5, x='Month', y='SecurityDelay', color='Reporting_Airline', title='Average security delay time (minutes) by airline')

    return[fig1, fig2, fig3, fig4, fig5]

# Run the app
if __name__ == '__main__':
    app.run_server()