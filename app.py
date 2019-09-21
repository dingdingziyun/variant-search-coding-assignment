#Ziyun Ding
#dingdingziyun@gmail.com
#9-19-2019

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import visdcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# read variants file
def read_var_table(var_file):
    variants = pd.read_csv(var_file, sep = '\t')
    # exclude entries without gene name and nucleotide change
    variants = variants[variants['Gene'].notnull()]
    variants = variants[variants['Nucleotide Change'].notnull()][[
        'Gene', 'Nucleotide Change', 'Protein Change', 'Alias', 'Region',
        'Reported Classification', 'Last Evaluated', 'Last Updated', 'URL'
    ]]
    variants = variants.fillna('-')
    available_indicators = variants['Gene'].unique()
    grouped_gene = variants.groupby(['Gene'])
    return available_indicators, grouped_gene

available_indicators, grouped_gene = read_var_table('./data/variants.tsv')


# generate the html layout
app.layout = html.Div(children = [
    # the header
    html.H1(
        'Variant Search',
        style={
            'textAlign': 'center',
            'color': 'blue'
        }
        ),
    # the auto-suggest feature for entering the gene name
    dcc.Dropdown(
        id='my-id',
        options=[{'label': i, 'value': i} for i in available_indicators],
        value=None,
        placeholder='Please enter the valid gene names. Example: CDKL5',
        #multi=True
    ),
    html.Button('Submit', id='button'),

    html.Div(id='my-div'),
    html.Footer('Ziyun Ding: dingdingziyun@gmail.com'),

])


# taking the input from the dropdown, output the table to the html layout
@app.callback(
    dash.dependencies.Output('my-div', 'children'),
    #Output(component_id='my-div', component_property='children'),
    #[Input(component_id='my-id', component_property='value')]
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('my-id', 'value')]
)


def table_link(n_clicks, input_value):
    # generate the html.table if the input is correct
    if input_value != None and input_value in available_indicators:
        # get the dataframe by the gene name
        dataframe = grouped_gene.get_group(input_value)
        # group the dataframe based on the Protein Change and Reported Classification 
        # and aggregate the information in other columns together
        dataframe = dataframe.groupby(['Protein Change','Reported Classification']).agg({
                        'Gene': 'first',
                        'Nucleotide Change': lambda x: ', '.join(set(x)),
                        'Alias': lambda x: ', '.join(set(map(str,x))),
                        'Region': lambda x: ', '.join(set(map(str,x))),
                        'Last Evaluated': lambda x: ', '.join(set(map(str,x))),
                        'Last Updated': lambda x: ', '.join(set(x)),
                        'URL': lambda x: ', '.join(set(x))
                    }).reset_index().sort_values(['Nucleotide Change'])
        dataframe = dataframe[['Gene', 'Nucleotide Change', 'Protein Change', 'Alias', 'Region',
                    'Reported Classification', 'Last Evaluated', 'Last Updated', 'URL']]
        # Change the URL column into ClinVar hyperlinks
        link_column = 'URL'
        
        rows = []
        for i in range(len(dataframe)):
            row = []
            for col in dataframe.columns:
                value = dataframe.iloc[i][col]
                if col == link_column:
                    cell = html.Td(html.A('ClinVar', href=value, target='_blank'))
                else:
                    cell = html.Td(children=value)
                row.append(cell)
            rows.append(html.Tr(row))



        return html.Table(
                        # Header
                        [html.Tr([html.Th(col.title()) for col in dataframe.columns])] +
                        rows,className='mtable', style={'border':'1.5px', 'font-size':'1.2rem', 'width': '30%'}
                        )
    # give warning if the input is empty or incorrect
    else:
        return html.Div(children='Please enter a valid gene name', style={
        'textAlign': 'center',
        'color': 'red'
        })


if __name__ == '__main__':
    app.run_server(debug=True)
