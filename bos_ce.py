from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate

url='https://raw.githubusercontent.com/HNemrawi/Test1/main/App.csv'
bosce = pd.read_csv(url, index_col=0,converters={'Rank on List': int,'Personal ID': str})
#bosce = pd.read_csv('App.csv', converters={'Rank on List': int,'Personal ID': str})

color_discrete_map = {"White": "#0819AB",
                      "Black, African American, or African": "#09A0B2",
                      "Asian or Asian American": "#00629B",
                      "Multi-Racial": "#08A88D",
                      "American Indian, Alaska Native, or Indigenous": "#0947B2",
                      "Native Hawaiian or Pacific Islander": "#00629b",
                      "Non-Hispanic/Non-Latin(a)(o)(x)": "#09A0B2",
                      "Hispanic/Latin(a)(o)(x)": "#0819AB",
                      "Client doesn't know": "#D3D3D3",
                      "Data not collected": "#D3D3D3",
                      "Client refused": "#D3D3D3",
                      "Male": "#00629b",
                      "Female": "#08A88D",
                      "Transgender": "#09A0B2"}

logo = "https://images.squarespace-cdn.com/content/v1/54ca7491e4b000c4d5583d9c/eb7da336-e61c-4e0b-bbb5-1a7b9d45bff6/Dash+Logo+2.png?format=750w"
Logo = html.Div([
    html.A([
        html.Img(
            src=logo,
            className='text-center',
            style={'height': '20%', 'width': '20%', 'float': 'center',
                   'position': 'center', 'padding-top': 0, 'padding-right': 0})
    ],
        href="https://icalliances.org/",
        target='_blank')
])

Title = html.H1(
    'WI BoS Coordinated Entry Equity DASHboard',
    className='text-center',
    style={'fontSize': 30, 'fontFamily': 'Source Sans Pro',
           'color': '#00629B', 'align': 'center',
           'height': '20%', 'width': '100%', 'float': 'center',
           'position': 'center'})

app = Dash(__name__,external_stylesheets=[dbc.themes.MINTY])
server=app.server

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col([Logo
                 ],
                width={'size': 12, 'offset': 0, 'order': 0},
                xs=12, sm=12, md=12, lg=12, xl=12
                )
    ),
    dbc.Row(
        dbc.Col([Title])
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([

            dcc.Dropdown(placeholder='Select Project Type',
                         id='project-type',
                         multi=False,
                         options=bosce['Project Type'].unique())
        ],
            width={'size': 3, 'offset': 0, 'order': 2},
            xs=12, sm=6, md=6, lg=3, xl=3
        ),
        dbc.Col([

            dcc.Dropdown(placeholder='Select Household Type',
                         id='household-type',
                         multi=False,
                         options=bosce['Household Type'].unique())
        ],
            width={'size': 3, 'offset': 0, 'order': 1},
            xs=12, sm=6, md=6, lg=3, xl=3
        ),
        dbc.Col([

            dcc.Dropdown(placeholder='Select Breakdown by',
                         id='coulmn-name',
                         multi=False,
                         options=['Race', 'Ethnicity', 'Gender'])
        ],
            width={'size': 3, 'offset': 0, 'order': 3},
            xs=12, sm=6, md=6, lg=3, xl=3),
        dbc.Col([

            dcc.Dropdown(placeholder='Select Top,Bottom #',
                         id='top-bottom',
                         multi=False,
                         options=[50, 100, 200, 300, 400],
                         value=int())
        ],
            width={'size': 3, 'offset': 0, 'order': 3},
            xs=12, sm=6, md=6, lg=3, xl=3),
    ]),
    html.Br(),
    html.Br(),
    dbc.Button('Create Graphs', id='submit-val', n_clicks=0),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='top-n', figure={})],
            width={'size': 6, 'offset': 0, 'order': 0},
            xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([
            dcc.Graph(id='bottom-n', figure={})],
            width={'size': 6, 'offset': 0, 'order': 0},
            xs=12, sm=12, md=12, lg=6, xl=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='scatter-plot', figure={})
        ],
            width={'size': 12, 'offset': 0, 'order': 0},
            xs=12, sm=12, md=12, lg=12, xl=12
        )
    ])
])


@app.callback(
    Output('top-n', 'figure'),
    Output('bottom-n', 'figure'),
    Input('submit-val', 'n_clicks'),
    State('household-type', 'value'),
    State('project-type', 'value'),
    State('coulmn-name', 'value'),
    State('top-bottom', 'value'))
def Update_graph(button_click, household_type, project_type, variable_name, top_bottom, then=None):
    my_list=[household_type, project_type, variable_name, top_bottom]
    if None in my_list:
        raise PreventUpdate
    msk = (bosce['Household Type'] == household_type) & \
          (bosce['Project Type'] == project_type)
    filtered_bosce = bosce[msk]
    Top = filtered_bosce.nsmallest(top_bottom, 'Rank on List')
    Top = Top.groupby([variable_name])['Personal ID'].count().reset_index(name='count')
    Top['Percent'] = Top['count'] / Top['count'].sum()
    Bottom = filtered_bosce.nlargest(top_bottom, 'Rank on List')
    Bottom = Bottom.groupby([variable_name])['Personal ID'].count().reset_index(name='count')
    Bottom['Percent'] = Bottom['count'] / Bottom['count'].sum()
    new_line = '<br>'
    fig1 = px.bar(Top, x=variable_name, y='Percent', color=variable_name, text='count', template="plotly_white",
                  color_discrete_map=color_discrete_map, height=500,
                  title=f'{variable_name} Breakdown of Top {top_bottom}{new_line}{household_type} on the {project_type} List')
    fig1.update_layout(showlegend=False)
    fig1.layout.yaxis.tickformat = ',.0%'
    fig2 = px.bar(Bottom, x=variable_name, y='Percent', color=variable_name, text='count', template="plotly_white",
                  color_discrete_map=color_discrete_map, height=500,
                  title=f'{variable_name} Breakdown of Bottom {top_bottom}{new_line}{household_type} on the {project_type} List')
    fig2.update_layout(showlegend=False)
    fig2.layout.yaxis.tickformat = ',.0%'
    return fig1, fig2


@app.callback(
    Output('scatter-plot', 'figure'),
    Input('submit-val', 'n_clicks'),
    State('household-type', 'value'),
    State('project-type', 'value'),
)
def update_scatter(button_click, household_type, project_type):
    my_list = [household_type, project_type]
    if None in my_list:
        raise PreventUpdate
    msk = (bosce['Household Type'] == household_type) & \
          (bosce['Project Type'] == project_type)
    filtered_bosce = bosce[msk]
    fig3 = px.scatter(filtered_bosce, x="Rank on List", y="VI Score", animation_frame="Project Type",
                      animation_group="Personal ID",
                      color="Race", hover_name="Race", height=400, width=970, template="plotly_white",
                      title=f'Relation between VI Score and Rank on the {project_type} List for {household_type}',
                      log_x=True, size_max=55, color_discrete_map=color_discrete_map)
    fig3.update_layout(xaxis=dict(autorange="reversed"))
    return fig3


if __name__ == '__main__':
    app.run_server(debug=False)
