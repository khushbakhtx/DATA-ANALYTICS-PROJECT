import dash
from dash import Dash, dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from etl import get_data
from datetime import datetime as dtime
#-------------------------
import os
from dash.exceptions import PreventUpdate
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

first = get_data('1')
second = get_data('2')
third = get_data('3')
fourth = get_data('4')
fifth = get_data('5')
sixth = get_data('6')
product_df = pd.read_csv("./source/product.csv") #[["ProductName", "Supplier", "ProductCost"]]
store_df = pd.read_csv("./source/store.csv")
data_table_df = pd.merge(product_df, store_df, on="ProductId", how="inner")

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

db_uri = "sqlite:///./sqlite.db"
db = SQLDatabase.from_uri(db_uri)
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)

answer_prompt = PromptTemplate.from_template(
    """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at the tables in the database to see what you can query.
    Do NOT skip this step.
    Then you should query the schema of the most relevant tables.
    Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer_prompt
    | llm
    | StrOutputParser()
)
third['sales_date'] = pd.to_datetime(third['sales_date'], errors='coerce')
sixth['sales_date'] = pd.to_datetime(sixth['sales_date'], errors='coerce')

min_year = third['sales_date'].dt.year.min()
max_year = third['sales_date'].dt.year.max()

fig_pie = px.pie(data_frame=fourth.sort_values(by='total_sales', ascending=False).head(20), 
                 names='product_name', 
                 values='total_sales', 
                 title='Market Share of Products',
                 hole=0.3,
                 height=400,
                 width=420)

fifth = fifth.fillna({'store_name': 'Unknown'})
fig_sunburst = px.sunburst(data_frame=fifth, 
                            path=['store_name', 'product_name'], 
                            values='total_sales', 
                            title='Sales Distribution by Store and Product',
                            height=400,
                            width=400)

fig_pie.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
fig_sunburst.update_layout(
        showlegend=False,
        template='plotly_dark',
        margin=dict(l=20, r=20, t=50, b=20),
        autosize=True
)

main_layout = html.Div(style={
    'display': 'grid',
    'grid-template-columns': 'repeat(3, 1fr)',
    'grid-template-rows': 'repeat(2, 1fr)',
    'grid-gap': '20px',
    'padding': '40px',
    'height': 'calc(100vh - 100px)',
    'width': '100vw',
    'justify-content': 'center',
    'align-items': 'center'
}, children=[
        html.Div(style={'grid-column': '1 / 2', 'grid-row': '1 / 2'}
                 , className="plotly-graphx",  children=[
        dcc.Graph(id="fig_scatter", style={'border-radius': 15})
    ]),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '1 / 2'}, className="plotly-graphx",
              children=[
        dcc.Graph(id="fig_bar")
    ]),
    html.Div(style={'grid-column': '3 / 4', 'grid-row': '1 / 3', 'height': '100%', 'display': 'flex', 'flex-direction': 'column'},
    className='box', children=[html.Div(className='plotly-graph', children=[
    html.Div(id="chat-container", className="chat-container"),
    dcc.Input(id='user-input', type='text', placeholder='Ex:Give me the total sales for dec 29, 2020', style={'width': '95%'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Store(id='chat-history', data=[])
    ])]),
    html.Div(style={'grid-column': '1 / 3', 'grid-row': '2 / 3'}, children=[
        dcc.Graph(id="fig_line"),
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '1 / 2', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(figure=fig_pie)
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(id="fig_3d")
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '3 / 4', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(figure=fig_sunburst)
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '4 / 5'}, className='footer', children=[
        html.P("Built by AI Enthusiast", style={'margin': '0'}),
        html.P("Khushbakht Shoymardonov", style={'margin-bottom': '20'}),
        html.P("_______________________")
    ])
])

app = dash.Dash(__name__, title='Khushbakht Shoymardonov')
server = app.server

app.layout = dbc.Container(
    children=[
    html.H1("Walmart Sales", style={'text-align': 'center', 'color': 'white'}),
    html.Div(className="header_component",
            children=[
        dcc.Dropdown(
            id="dropdown_store",
            options=first['store_name'].unique(),
            value=None, className="dropdown"
        ),
        dcc.RangeSlider(
                id='range_slider',
                className="range_slider",
                min=min_year,
                max=max_year,
                step=1,
                allowCross=False,
                value=[min_year, max_year],
                marks={str(year): str(year) for year in range(min_year, max_year+1, 1)}
            ),
        html.Button('Home', id="home-button", style={'margin-left':'200px'}),
        html.Button('Table', id="table-button", style={'margin-left':'10px'}),
    ]),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[main_layout])
], fluid=True, style={
'background-image': 'url("./assets/world-map_2.png")', 'background-attachment': 'fixed',
'background-repeat': 'no-repeat','display': 'inline-block', 'margin-top':'5px'})

table_layout =  html.Div(style={
    'padding': '40px',
    'height': 'calc(100vh - 100px)',
    'width': '100vw',
    'justify-content': 'center',
    'align-items': 'center'
}, children=[
html.Div(children=[
    dash_table.DataTable(
        data_table_df.to_dict("records"),
        [{"name": i, "id": i} for i in data_table_df.columns],
        filter_action="native",
        filter_options={"placeholder_text": "Filter column..."},
        page_size=15,
        style_cell={
                    'backgroundColor': 'rgba(254, 255, 255, 0.245)',
                    'color': '#fff',
                    'padding': '5px',
                    'border': '1px solid #444'
        },
        style_header={
                    'backgroundColor': '#444',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'border': '1px solid #444'
        },
        style_filter={
                    'backgroundColor': 'rgba(254, 255, 255, 0.545)',
                    'color': '#fff',
                    'fontWeight': 'bold',
                    'border': '1px solid #444'
        },
        style_table={
                    'overflowY': 'auto',
                    'height': '400px',
                    'border': '1px solid #444',
                    'border-radius': '20px',
        }
)
])])


@app.callback(Output('page-content', 'children'),
              [Input('home-button', 'n_clicks'),
               Input('table-button', 'n_clicks')])

def display_page(home_clicks, table_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return main_layout
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'home-button':
            return main_layout
        elif button_id == 'table-button':
            return table_layout



@app.callback(
    Output("fig_scatter", "figure"),
    Output("fig_bar", "figure"),
    Input("dropdown_store", "value")
)
def update_plot_bar(selected_store):
    if selected_store is None:
        filtered_store_scatter=first
        filtered_store_bar=second
    else:
        filtered_store_scatter = first[first['store_name']==selected_store]
        filtered_store_bar = second[second['store_name']==selected_store]
    fig_scatter = px.scatter(data_frame=filtered_store_scatter, 
                            x='unit_price', 
                            y='total_quantity_sold', 
                            height=400,
                            width=420,
                            color='product_name', 
                            title='Sales Performance by Unit Price and Quantity Sold',
                            labels={'unit_price': 'Unit Price', 'total_quantity_sold': 'Total Quantity Sold'})

    second['short_product_name'] = second['product_name'].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
    fig_bar = px.bar(data_frame=filtered_store_bar.sort_values(by='total_sales', ascending=False).head(30), 
                    x='product_name', 
                    y='total_sales', 
                    height=400,
                    width=550,                  
                    title='Total Sales by Product',
                    labels={'total_sales': 'Total Sales'},
                    color_discrete_sequence=px.colors.sequential.Blues)
    fig_bar.update_layout(
        xaxis_tickangle=-45
    )
    fig_scatter.update_layout(
        showlegend=False,
        template='plotly_dark',
        margin=dict(l=20, r=20, t=50, b=20),
        autosize=True
    )
    fig_bar.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
    return fig_scatter, fig_bar

@app.callback(
    Output("fig_line", "figure"),
    Output("fig_3d", "figure"),
    Input("range_slider", "value")
)
def update_line_chart_3d(selected_range):
    min_year, max_year = selected_range
    filtered_data = third[(third['sales_date'].dt.year >= min_year) & (third['sales_date'].dt.year <= max_year)]
    filtered_data_3d = sixth[(sixth['sales_date'].dt.year >= min_year) & (sixth['sales_date'].dt.year <= max_year)]
    fig_line = px.line(data_frame=filtered_data, 
                   x='sales_date', 
                   y='total_sales', 
                   height=400,
                   title='Sales Trends Over Time',
                   labels={'sales_date': 'Sales Date', 'total_sales': 'Total Sales'})
    fig_3d = px.scatter_3d(data_frame=filtered_data_3d, 
                        x='sales_date', 
                        y='store_id', 
                        z='total_quantity_sold', 
                        color='product_name', 
                        title='Sales Analysis by Store, Product, and Date',
                        height=400,
                        width=550,
                        labels={'sales_date': 'Sales Date', 'store_id': 'Store ID', 'total_quantity_sold': 'Total Quantity Sold'})
    fig_line.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
    fig_3d.update_layout(
        showlegend=False,
        template='plotly_dark',
        margin=dict(l=20, r=20, t=50, b=20),
        autosize=True
        )
    
    return fig_line, fig_3d

@app.callback(
    Output('chat-container', 'children'),
    Output('chat-history', 'data'),
    Input('submit-button', 'n_clicks'),
    Input('user-input', 'value'),
    State('chat-history', 'data')
)
def update_chat(n_clicks, user_input, chat_history):
    if n_clicks > 0 and user_input:
      
        result = chain.invoke({"question": user_input})
       
        chat_history.append({'question': user_input, 'answer': result})
       
        messages = []
        for entry in chat_history:
            messages.append(html.Div(f"{entry['question']}",className="user-message"))
            messages.append(html.Div(f"{entry['answer']}", className="ai-message"))

        return messages, chat_history

    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)