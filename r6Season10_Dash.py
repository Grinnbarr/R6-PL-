#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option("display.precision", 3)
pd.options.mode.chained_assignment = None  # default='warn'

# ! pip install plotly==4.5.4
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
from plotly import tools
# import ipywidgets as widgets
# from ipywidgets import *
# from IPython.display import display

# !pip install dash==1.12.0
# !pip install jupyter-dash
# from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

# pio.renderers.default='notebook'


# In[2]:


# Import the data
data='R6 PL - Season X.csv'
df = pd.read_csv(data)
df.dropna(axis=0,subset=['ATK_team'],inplace=True)
df.drop(['A_P1','A_P2','A_P3','A_P4','A_P5','B_P1','B_P2','B_P3','B_P4','B_P5'],axis=1,inplace=True)
df = df.astype({'MatchID':'int64','Date':'datetime64[ns]','ATK_win':'bool'}, inplace=True)
df1 = df.drop(['Date','Team_A','Team_B','ATK_team','Winner'],axis=1)


# In[3]:


#define lists of attackers, defenders, maps and sites
ATKOps = ['Nokk','Gridlock','Nomad','Maverick','Lion','Finka','Dokkaebi','Zofia','Ying','Jackal','Hibana','Capitao','Blackbeard','Buck','Sledge','Thatcher','Ash','Thermite','Montagne','Twitch','Blitz','IQ','Fuze','Glaz']
DEFOps = ['Warden','Mozzie','Kaid','Clash','Maestro','Alibi','Vigil','Ela','Lesion','Mira','Echo','Caveira','Valkyrie','Frost','Mute','Smoke','Castle','Pulse','Doc','Rook','Jager','Bandit','Kapkan','Tachanka']
Ops = ATKOps + DEFOps


# In[4]:


#Create ATK/DEF dataframes
ATK = pd.DataFrame(columns=['Operator','Ban_rate','Pick_rate','Wins per pick','wppn','Picks per win','ppwn'])
ATK['Operator'] = ATKOps
DEF = pd.DataFrame(columns=['Operator','Ban_rate','Pick_rate','Wins per pick','wppn','Picks per win','ppwn'])
DEF['Operator'] = DEFOps

# add a colour column
ATKcolour = {'Nokk':'rgb(54,70,156)',
             'Gridlock':'rgb(184,23,83)',
             'Nomad':'rgb(171,133,81)',
             'Maverick':'rgb(113,128,143)',
             'Lion':'rgb(252,174,29)','Finka':'rgb(252,174,29)',
             'Dokkaebi':'rgb(209,217,219)',
             'Zofia':'rgb(71,151,150)',
             'Ying':'rgb(171,70,35)',
             'Jackal':'rgb(117,56,147)',
             'Hibana':'rgb(154,39,63)',
             'Capitao':'rgb(80,146,69)',
             'Blackbeard':'rgb(200,149,41)',
             'Buck':'rgb(25,128,163)',
             'Sledge':'rgb(144,111,121)','Thatcher':'rgb(144,111,121)',
             'Ash':'rgb(215,91,43)','Thermite':'rgb(215,91,43)',
             'Montagne':'rgb(45,89,128)','Twitch':'rgb(45,89,128)',
             'Blitz':'rgb(247,146,30)','IQ':'rgb(247,146,30)',
             'Fuze':'rgb(183,54,54)','Glaz':'rgb(183,54,54)'}
DEFcolour = {'Warden':'rgb(54,70,156)',
             'Mozzie':'rgb(184,23,83)',
             'Kaid':'rgb(171,133,81)',
             'Clash':'rgb(113,128,143)',
             'Maestro':'rgb(102,110,36)','Alibi':'rgb(102,110,36)',
             'Vigil':'rgb(209,217,219)',
             'Ela':'rgb(71,151,150)',
             'Lesion':'rgb(171,70,35)',
             'Mira':'rgb(117,56,147)',
             'Echo':'rgb(154,39,63)',
             'Caveira':'rgb(80,146,69)',
             'Valkyrie':'rgb(200,149,41)',
             'Frost':'rgb(25,128,163)',
             'Mute':'rgb(144,111,121)','Smoke':'rgb(144,111,121)',
             'Castle':'rgb(215,91,43)','Pulse':'rgb(215,91,43)',
             'Doc':'rgb(45,89,128)','Rook':'rgb(45,89,128)',
             'Jager':'rgb(247,146,30)','Bandit':'rgb(247,146,30)',
             'Kapkan':'rgb(183,54,54)','Tachanka':'rgb(183,54,54)'}
ATK['colour']=ATK['Operator'].map(ATKcolour)
DEF['colour']=DEF['Operator'].map(DEFcolour)


# In[5]:


#Function to populate ATK dataframe
def attack(DF):
    ATK1=ATK.copy()
        
    #Bans
    matches = DF[['MatchID','A_ATK_ban','A_DEF_ban','B_ATK_ban','B_DEF_ban']]
    matches.drop_duplicates(inplace=True)

    for i,j in zip(ATKOps,range(len(ATKOps))):
        tp = matches.loc[(matches['A_ATK_ban']==i) |
                         (matches['B_ATK_ban']==i)]
        try:
            temprate = round((len(tp.index.values)/len(matches.index.values))*100,1)
        except:
            temprate = 0
        ATK1.Ban_rate[j]=temprate
 
    #Picks
    for i,j in zip(ATKOps,range(len(ATKOps))):
        available = DF.loc[(DF['A_ATK_ban']!=i) &
                           (DF['B_ATK_ban']!=i)]
        picks = available.loc[(available['ATK_O1']==i) |
                              (available['ATK_O2']==i) |
                              (available['ATK_O3']==i) |
                              (available['ATK_O4']==i) |
                              (available['ATK_O5']==i)]
        try:
            pickrate = round((len(picks.index.values)/len(available.index.values))*100,1)
            ATK1['Pick_rate'][j]=pickrate
        except:
            ATK1['Pick_rate'][j]=0

    #Wins per pick        
    for i,j in zip(ATKOps,range(len(ATKOps))):
        pick = DF.loc[(DF['ATK_O1']==i) |
                      (DF['ATK_O2']==i) |
                      (DF['ATK_O3']==i) |
                      (DF['ATK_O4']==i) |
                      (DF['ATK_O5']==i)]
        win_pick = pick.loc[(pick['ATK_win']==True)]
        try:
            win_pickrate = round((len(win_pick.index.values)/len(pick.index.values)),3)
            ATK1['Wins per pick'][j]=win_pickrate
            ATK1['wppn'][j]=round(len(pick.index.values),0)
        except:
            ATK1['Wins per pick'][j]=0
            ATK1['wppn'][j]=0

    # Picks per win
    for i,j in zip(ATKOps,range(len(ATKOps))):
        win = DF.loc[(DF['ATK_win']==True)]
        pick_win = win.loc[(win['ATK_O1']==i) |
                           (win['ATK_O2']==i) |
                           (win['ATK_O3']==i) |
                           (win['ATK_O4']==i) |
                           (win['ATK_O5']==i)]

        try:
            pick_winrate = round((len(pick_win.index.values)/len(win.index.values)),3)
            ATK1['Picks per win'][j]=pick_winrate
            ATK1['ppwn'][j]=round(len(win.index.values),0)
        except:
            ATK1['Picks per win'][j]=0
            ATK1['ppwn'][j]=0
            
    return ATK1


# In[6]:


#Function to populate DEF dataframe
def defence(DF):
    DEF1=DEF.copy()
    
    #Bans
    matches = DF[['MatchID','A_ATK_ban','A_DEF_ban','B_ATK_ban','B_DEF_ban']]
    matches.drop_duplicates(inplace=True)

    for i,j in zip(DEFOps,range(len(DEFOps))):
        tp = matches.loc[(matches['A_DEF_ban']==i) |
                         (matches['B_DEF_ban']==i)]
        try:
            temprate = round((len(tp.index.values)/len(matches.index.values))*100,1)
        except:
            temprate = 0
        DEF1.Ban_rate[j]=temprate
    
    #Picks    
    for i,j in zip(DEFOps,range(len(DEFOps))):
        available = DF.loc[(DF['A_DEF_ban']!=i) &
                           (DF['B_DEF_ban']!=i)]
        picks = available.loc[(available['DEF_O1']==i) |
                              (available['DEF_O2']==i) |
                              (available['DEF_O3']==i) |
                              (available['DEF_O4']==i) |
                              (available['DEF_O5']==i)]
        try:
            pickrate = round((len(picks.index.values)/len(available.index.values))*100,1)
            DEF1['Pick_rate'][j]=pickrate
        except:
            DEF1['Pick_rate'][j]=0
    
    #Wins per pick      
    for i,j in zip(DEFOps,range(len(DEFOps))):
        pick = DF.loc[(DF['DEF_O1']==i) |
                      (DF['DEF_O2']==i) |
                      (DF['DEF_O3']==i) |
                      (DF['DEF_O4']==i) |
                      (DF['DEF_O5']==i)]
        win_pick = pick.loc[(pick['ATK_win']==False)]
        try:
            win_pickrate = round((len(win_pick.index.values)/len(pick.index.values)),3)
            DEF1['Wins per pick'][j]=win_pickrate
            DEF1['wppn'][j]=round(len(pick.index.values),0)
        except:
            DEF1['Wins per pick'][j]=0
            DEF1['wppn'][j]=0
            
    # Picks per win
    for i,j in zip(DEFOps,range(len(DEFOps))):
        win = DF.loc[(DF['ATK_win']==False)]
        pick_win = win.loc[(win['DEF_O1']==i) |
                           (win['DEF_O2']==i) |
                           (win['DEF_O3']==i) |
                           (win['DEF_O4']==i) |
                           (win['DEF_O5']==i)]

        try:
            pick_winrate = round((len(pick_win.index.values)/len(win.index.values)),3)
            DEF1['Picks per win'][j]=pick_winrate
            DEF1['ppwn'][j]=round(len(win.index.values),0)
        except:
            DEF1['Picks per win'][j]=0
            DEF1['ppwn'][j]=0
            
    return DEF1


# In[7]:


#Create lists for the drop-down menus
Region_dd_options = pd.array(['All','European Union','North America','Latin America'],dtype=str)

Map=df1['Map'].unique()
Map_dd_options = np.append(['All'],Map)

Maps=Map.tolist()
Mapsites={elem:pd.DataFrame() for elem in Maps}
for key in Mapsites.keys():
    Mapsites[key]=df1.loc[(df1['Map']==key)].Site.unique().tolist()
    
Mapsites = pd.DataFrame.from_dict(Mapsites)
dfall = pd.DataFrame([['All','All','All','All','All','All','All']], 
                     columns = ['Kafe','Coastline','Bank','Villa','Clubhouse','Consulate','Border']
                    )
Mapsites = pd.concat([dfall,Mapsites])
Mapsites['All'] = ['All','All','All','All','All']
Mapsites=Mapsites.reset_index(drop=True)

Mapsites_dd_options=Mapsites.to_dict('list')


# In[ ]:


###Create DASH infographic
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#333333',
    'text': '#eeeeee',
    'plot_background': '#444444'
}


app.layout = html.Div(
    style={'backgroundColor': colors['background'],
          'width':'70%',
          'padding':'25px'},
    children=[
        html.H6(children='RAINBOW 6 PRO LEAGUE: Season X operator statistics',
                style={
                   'color': colors['text'],
                   'font-weight': 'bold'
                }),
        
        html.Div([
            html.Label('Region',
                          style={'color':colors['text']}),
            html.Label('Map',
                      style={'color': colors['text']}),
            html.Label('Site',
                      style={'color': colors['text']})],
            style={'columnCount': 3}),
        
        html.Div([            
            dcc.Dropdown(
                id='Region_dropdown',
                options=[{'label':i,'value':i} for i in Region_dd_options],
                value='All'),            
            dcc.Dropdown(
                id='Map_dropdown',
                options=[{'label':i,'value':i} for i in Map_dd_options],
                value='All'),            
            dcc.Dropdown(
                id='Mapsite_dropdown',
                value='All')],
            style={'columnCount': 3}),
        
        html.Hr(),
        
        html.Div([
            dash_table.DataTable(
                id='Bans',
                columns = [{'name': 'ATK', 'id': 'ATK'},{'name': 'ATK ban rate (%)', 'id': 'ATK ban rate (%)'},
                           {'name': 'DEF', 'id': 'DEF'},{'name': 'DEF ban rate (%)', 'id': 'DEF ban rate (%)'}],
                style_table={
                    'maxWidth':'80%',
                    'margin-left':'10%',
                    'margin-right':'10%'
                },
                style_header={
                    'backgroundColor':colors['background'],
                    'fontWeight':'bold'
                },
                style_cell={
                    'backgroundColor':colors['plot_background'],
                    'color':colors['text'],
                    'text_align':'center',
                    'font_family': ["Open Sans", "HelveticaNeue", "Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
                    'height':'auto',
                    'whiteSpace':'normal'
                },
                style_data_conditional=[{
                    'if':{'column_id':['ATK','DEF']},
                    'fontWeight':'bold'
                }],
                style_as_list_view=True,
            ),
            
            dash_table.DataTable(
                id='Picks',
                columns = [{'name': 'ATK', 'id': 'ATK'},{'name': 'ATK pickrate when available (%)', 
                                                         'id': 'ATK pickrate when not banned (%)'},
                           {'name': 'DEF', 'id': 'DEF'},{'name': 'DEF pickrate when available (%)', 
                                                         'id': 'DEF pickrate when not banned (%)'}],
                style_table={
                    'maxWidth':'80%',
                    'margin-left':'10%',
                    'margin-right':'10%'
                },
                style_header={
                    'backgroundColor':colors['background'],
                    'fontWeight':'bold'
                },
                style_cell={
                    'backgroundColor':colors['plot_background'],
                    'color':colors['text'],
                    'text_align':'center',
                    'font_family': ["Open Sans", "HelveticaNeue", "Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
                    'height':'auto',
                    'whiteSpace':'normal'
                },
                style_data_conditional=[{
                    'if':{'column_id':['ATK','DEF']},
                    'fontWeight':'bold'
                }],
                style_as_list_view=True,
            ),
            
             dash_table.DataTable(
                id='ATK win rate',
                columns = [{'name': 'ATK winrate', 'id': 'winrate'}],
                style_table={
                    'maxWidth':'80%',
                    'margin-left':'10%',
                    'margin-right':'10%'
                },
                style_cell={
                    'backgroundColor':colors['plot_background'],
                    'color':colors['text'],
                    'text_align':'center',
                    'font_family': ["Open Sans", "HelveticaNeue", "Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
                    'fontWeight':'bold',
                    'font_size':'150%',
                },
             ),
        ],
            style={'columnCount': 3}
        ),
        
        html.Hr(),
        
        html.Div([
            html.Div([
                dcc.Graph(id='ATKppw',
                      config={
#                           'responsive':True,
                          'doubleClick':'reset'
                      })
            ],
                className='six columns'
            ),
            html.Div([
                dcc.Graph(id='DEFppw',
                      config={
#                           'responsive':True,
                          'doubleClick':'reset'}
                         )
            ],
                className='six columns'
            ),
            ],className='row'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='ATKwpp',
                      config={
#                           'responsive':True,
                          'doubleClick':'reset'
                      })
            ],
                className='six columns'
            ),
            html.Div([
                dcc.Graph(id='DEFwpp',
                      config={
#                           'responsive':True,
                          'doubleClick':'reset'}
                         )
            ],
                className='six columns'
            ),
            ],className='row'),
    ],
)


#Callback to populate mapsites dropdown
@app.callback(
    Output('Mapsite_dropdown', 'options'),
    [Input('Map_dropdown', 'value')])        
def set_sites_options(selected_map):
    return [
        {'label': i, 'value': i} for i in Mapsites_dd_options[selected_map]
    ]

@app.callback(
    Output('Mapsite_dropdown', 'value'),
    [Input('Mapsite_dropdown', 'options')])
def set_sites_value(available_options):
    return available_options[0]['value']

#Callbacks to populate graphs

#define database filters
def cut(R,M,S):
    temp = df1.copy()
    if R == 'All':
        pass
    else:
        temp = temp.loc[(temp['Region']==R)]
     
    if M == 'All':
        pass
    else:
        temp = temp.loc[(temp['Map']==M)]
        
    if S == 'All':
        pass
    else:
        temp = temp.loc[(temp['Site']==S)]
    return temp

        
# Bans    
@app.callback(
    Output('Bans','data'),
    [Input('Region_dropdown','value'),
     Input('Map_dropdown','value'),
     Input('Mapsite_dropdown','value')
    ]
)
def update_bans(Region_value, Map_value, Site_value):
    temp = cut(Region_value, Map_value, Site_value)
    ATK1 = attack(temp)
    DEF1 = defence(temp)
    ATKbansort = ATK1.sort_values(by=['Ban_rate'],ascending=False)
    DEFbansort = DEF1.sort_values(by=['Ban_rate'],ascending=False)
    X = ATKbansort.drop(['Pick_rate','Wins per pick','wppn','Picks per win','ppwn','colour'],axis=1)
    Y = DEFbansort.drop(['Pick_rate','Wins per pick','wppn','Picks per win','ppwn','colour'],axis=1)
    X=X.head(4)
    X.columns = ['ATK','ATK ban rate (%)']
    Y=Y.head(4)
    Y.columns = ['DEF','DEF ban rate (%)']
    X.reset_index(inplace=True,drop=True)
    Y.reset_index(inplace=True,drop=True)
    Z=pd.concat([X,Y],axis=1)
    return Z.to_dict('rows')

# Picks
@app.callback(
    Output('Picks','data'),
    [Input('Region_dropdown','value'),
     Input('Map_dropdown','value'),
     Input('Mapsite_dropdown','value')
    ]
)
def update_picks(Region_value, Map_value, Site_value):
    temp1 = cut(Region_value, Map_value, Site_value)
    ATK1 = attack(temp1)
    DEF1 = defence(temp1)
    ATKpicksort = ATK1.sort_values(by=['Pick_rate'],ascending=False)
    DEFpicksort = DEF1.sort_values(by=['Pick_rate'],ascending=False)
    X = ATKpicksort.drop(['Ban_rate','Wins per pick','wppn','Picks per win','ppwn','colour'],axis=1)
    Y = DEFpicksort.drop(['Ban_rate','Wins per pick','wppn','Picks per win','ppwn','colour'],axis=1)
    X=X.head(4)
    X.columns = ['ATK','ATK pickrate when not banned (%)']
    Y=Y.head(4)
    Y.columns = ['DEF','DEF pickrate when not banned (%)']
    X.reset_index(inplace=True,drop=True)
    Y.reset_index(inplace=True,drop=True)
    Z=pd.concat([X,Y],axis=1)
    return Z.to_dict('rows')

# ATKwins
@app.callback(
    Output('ATK win rate','data'),
    [Input('Region_dropdown','value'),
     Input('Map_dropdown','value'),
     Input('Mapsite_dropdown','value')
    ]
)
def update_ATKwin(Region_value, Map_value, Site_value):
    temp2 = cut(Region_value, Map_value, Site_value)
    ATKwins = temp2.loc[(temp2['ATK_win']==True)]
    try:
        winrate = round((len(ATKwins.index.values)/len(temp2.index.values))*100,1)
    except:
        winrate = 'N/A'
        
    winrate = str(winrate)+'%'
    return [{'winrate': winrate}]


#Ppw
@app.callback(
    [Output('ATKppw','figure'),
     Output('DEFppw','figure')],
    [Input('Region_dropdown','value'),
     Input('Map_dropdown','value'),
     Input('Mapsite_dropdown','value')
    ]
)
def update_ppw(Region_value, Map_value, Site_value):
    temp = cut(Region_value, Map_value, Site_value)
    ATK1 = attack(temp)
    DEF1 = defence(temp)
    ATKppwsort = ATK1.sort_values(by=['Picks per win'],ascending=False)
    DEFppwsort = DEF1.sort_values(by=['Picks per win'],ascending=False)
    return [{
        'data': [
            {'x': ATKppwsort.Operator.head(7),
             'y': ATKppwsort['Picks per win'],
             'type': 'bar',
             'name': 'ATKppw',
             'text': ATKppwsort.Operator.head(7).tolist(),
             'textposition': 'auto',
             'textangle': -90,
             'customdata': ATKppwsort.ppwn.head(7).tolist(),
             'hovertemplate': '%{y}<br>n=%{customdata}',
             'marker': {
                 'color':ATKppwsort.colour
             }
            }
        ],
        'layout': {
            'title': 'ATK top picks per win',
            'plot_bgcolor': colors['plot_background'],
            'paper_bgcolor': colors['background'],
            'xaxis': {
                'showticklabels': False,
                'title': 'Operators'
            },
            'yaxis': {
                'title': 'Picks per win',
                'range':[0,1]
            },
            'font': {
                'color': colors['text']
            }
        }
    },
        {'data': [
            {'x': DEFppwsort.Operator.head(7),
             'y': DEFppwsort['Picks per win'],
             'type': 'bar',
             'name': 'DEFppw',
             'text': DEFppwsort.Operator.head(7).tolist(),
             'textposition': 'auto',
             'textangle': -90,
             'customdata': DEFppwsort.ppwn.head(7).tolist(),
             'hovertemplate': '%{y}<br>n=%{customdata}',
             'marker': {
                 'color':DEFppwsort.colour
             }
            }
        ],
        'layout': {
            'title': 'DEF top picks per win',
            'plot_bgcolor': colors['plot_background'],
            'paper_bgcolor': colors['background'],
            'xaxis': {
                'showticklabels': False,
                'title': 'Operators'
            },
            'yaxis': {
                'title': 'Picks per win',
                'range':[0,1]
            },
            'font': {
                'color': colors['text']
            }
        }
        }
    ]
        
#WPP
@app.callback(
    [Output('ATKwpp','figure'),
     Output('DEFwpp','figure')],
    [Input('Region_dropdown','value'),
     Input('Map_dropdown','value'),
     Input('Mapsite_dropdown','value')
    ]
)
def update_wpp(Region_value, Map_value, Site_value):
    temp = cut(Region_value, Map_value, Site_value)
    ATK1 = attack(temp)
    DEF1 = defence(temp)
    ATKwppsort = ATK1.sort_values(by=['Wins per pick'],ascending=False)
    DEFwppsort = DEF1.sort_values(by=['Wins per pick'],ascending=False)
    return [{
        'data': [
            {'x': ATKwppsort.Operator.head(7),
             'y': ATKwppsort['Wins per pick'],
             'type': 'bar',
             'name': 'ATKwpp',
             'text': ATKwppsort.Operator.head(7).tolist(),
             'textposition': 'auto',
             'textangle': -90,
             'customdata': ATKwppsort.wppn.head(7).tolist(),
             'hovertemplate': '%{y}<br>n=%{customdata}',
             'marker': {
                 'color':ATKwppsort.colour
             }
            }
        ],
        'layout': {
            'title': 'ATK top wins per pick',
            'plot_bgcolor': colors['plot_background'],
            'paper_bgcolor': colors['background'],
            'xaxis': {
                'showticklabels': False,
                'title': 'Operators'
            },
            'yaxis': {
                'title': 'Wins per pick',
                'range':[0,1]
            },
            'font': {
                'color': colors['text']
            }
        }
    },
        {'data': [
            {'x': DEFwppsort.Operator.head(7),
             'y': DEFwppsort['Wins per pick'],
             'type': 'bar',
             'name': 'DEFwpp',
             'text': DEFwppsort.Operator.head(7).tolist(),
             'textposition': 'auto',
             'textangle': -90,
             'customdata': DEFwppsort.wppn.head(7).tolist(),
             'hovertemplate': '%{y}<br>n=%{customdata}',
             'marker': {
                 'color':DEFwppsort.colour
             }
            }
        ],
        'layout': {
            'title': 'DEF top wins per pick',
            'plot_bgcolor': colors['plot_background'],
            'paper_bgcolor': colors['background'],
            'xaxis': {
                'showticklabels': False,
                'title': 'Operators'
            },
            'yaxis': {
                'title': 'Picks per win',
                'range':[0,1]
            },
            'font': {
                'color': colors['text']
            }
        }
        }
    ]

if __name__ == '__main__':
#     app.run_server(mode="external",debug=True) #inline/external
    app.run_server(debug=False)


# In[ ]:




