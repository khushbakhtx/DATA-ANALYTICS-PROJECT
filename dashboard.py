import dash
from dash import Dash, dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from etl import get_data
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

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize database and LLM
db_uri = "sqlite:///./sqlite.db"
db = SQLDatabase.from_uri(db_uri)
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

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

fig_scatter = px.scatter(data_frame=first, 
                          x='unit_price', 
                          y='total_quantity_sold', 
                          height=400,
                          width=420,
                          color='product_name', 
                          title='Sales Performance by Unit Price and Quantity Sold',
                          labels={'unit_price': 'Unit Price', 'total_quantity_sold': 'Total Quantity Sold'})

second['short_product_name'] = second['product_name'].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
fig_bar = px.bar(data_frame=second.sort_values(by='total_sales', ascending=False).head(30), 
                  x='short_product_name', 
                  y='total_sales', 
                  height=400,
                  width=550,                  
                  title='Total Sales by Product',
                  labels={'total_sales': 'Total Sales'},
                  color_discrete_sequence=px.colors.sequential.Blues)
fig_bar.update_layout(
    xaxis_tickangle=-45
)

fig_line = px.line(data_frame=third, 
                   x='sales_date', 
                   y='total_sales', 
                   height=400,
                   title='Sales Trends Over Time',
                   labels={'sales_date': 'Sales Date', 'total_sales': 'Total Sales'})

fig_pie = px.pie(data_frame=fourth.head(20), 
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

fig_3d = px.scatter_3d(data_frame=sixth, 
                        x='sales_date', 
                        y='store_id', 
                        z='total_quantity_sold', 
                        color='product_name', 
                        title='Sales Analysis by Store, Product, and Date',
                        height=400,
                        width=550,
                        labels={'sales_date': 'Sales Date', 'store_id': 'Store ID', 'total_quantity_sold': 'Total Quantity Sold'})

fig_scatter.update_layout(
    showlegend=False,
    template='plotly_dark',
    margin=dict(l=20, r=20, t=50, b=20),
    autosize=True
)
fig_bar.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
fig_line.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
fig_pie.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
fig_sunburst.update_layout({'showlegend':False,
                           'template':'plotly_dark'})
fig_3d.update_layout({'showlegend':False,
                           'template':'plotly_dark'})

app = dash.Dash(__name__, title='Khushbakht Shoymardonov')

app.layout = dbc.Container(
    children=[
    html.H1("Walmart Sales", style={'text-align': 'center', 'color': 'white'}),
    html.Div(style={
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
        dcc.Graph(figure=fig_scatter, style={'border-radius': 15})
    ]),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '1 / 2'}, className="plotly-graphx",
              children=[
        dcc.Graph(figure=fig_bar)
    ]),
    html.Div(style={'grid-column': '3 / 4', 'grid-row': '1 / 3', 'height': '100%', 'display': 'flex', 'flex-direction': 'column'},
    className='box', children=[html.Div(className='plotly-graph', children=[
    html.Div(id="chat-container", className="chat-container"),
    dcc.Input(id='user-input', type='text', placeholder='Ex:Give me the total sales for dec 29, 2020', style={'width': '95%'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Store(id='chat-history', data=[])
    ])]),
    html.Div(style={'grid-column': '1 / 3', 'grid-row': '2 / 3'}, children=[
        dcc.Graph(figure=fig_line),
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '1 / 2', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(figure=fig_pie)
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(figure=fig_3d)
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '3 / 4', 'grid-row': '3 / 4'}, children=[
        dcc.Graph(figure=fig_sunburst)
    ], className="plotly-graphx"),
    html.Div(style={'grid-column': '2 / 3', 'grid-row': '4 / 5'}, className='footer', children=[
        html.P("Built by AI Enthusiast", style={'margin': '0'}),
        html.P("Khushbakht Shoymardonov", style={'margin-bottom': '20'}),
        html.P("_______________________")
    ])
]),
], fluid=True, style={
'background-image': 'url("./assets/world-map_2.png")', 'background-attachment': 'fixed',
'background-repeat': 'no-repeat','display': 'inline-block', 'margin-top':'5px'})




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