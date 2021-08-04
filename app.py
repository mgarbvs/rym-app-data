# -*- coding: utf-8 -*-
#The submission confirmation number is ad6bf06d-8288-4e75-81f8-4d8c15c43fe3. 
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Selecting on new value clears both values sometimes?

# Remember to unzip the csv files before running!
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime
import seaborn as sns
import plotly.express as px
from dash.exceptions import PreventUpdate
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=False)

music_df = pd.read_csv('DF1955.csv')
#Date stuff
music_df['Date'] = pd.to_datetime(music_df['Date'],infer_datetime_format = True, errors = 'coerce')
music_df['Month'] = music_df['Date'].dt.month
music_df['Season']= music_df['Month']%12 // 3 + 1
music_df.loc[(music_df['Season'] == 4),'Season'] = 'Fall'
music_df.loc[(music_df['Season'] == 3),'Season'] = 'Summer'
music_df.loc[(music_df['Season'] == 2),'Season'] = 'Spring'
music_df.loc[(music_df['Season'] == 1),'Season'] = 'Winter'
music_df['Year'] = music_df['Date'].dt.year
music_df['Year'] = pd.to_datetime(music_df['Year'], format = "%Y")
music_df['Year'] = music_df['Year'].dt.year.astype('int64')
music_df.loc[music_df['Year'] > 2021,'Year'] = music_df.loc[music_df['Year'] > 2021,'Year'] - 100

music_df = music_df.drop(columns = ['RYM Ratings'])
music_df['Genres'] = music_df['Genres'].str.split(',')
music_df['Primary Genre'] = music_df['Genres'].str[0]
music_df['Secondary Genre'] = music_df['Genres'].str[1]

#Replace nan values in ratings with this
#Fix_Year =  music_df.groupby(by = 'Year')['Ratings'].mean()
fix_year =  music_df.groupby(by = 'Year')['Ratings'].median()
for i in range(1955,2021):
    music_df.loc[music_df['Year'] == i,'Ratings'] = music_df.loc[music_df['Year'] == i,'Ratings'].fillna(fix_year[i])

gneres_and_avg = music_df.groupby(by = 'Primary Genre')[['RYM Rating','Ratings']].agg({'RYM Rating':'mean',
                                                                                       'Ratings':'sum'})
list_of_genres = sorted(music_df['Primary Genre'].unique())

selection = list_of_genres[428]

genre_rating_yearly = music_df[music_df['Primary Genre'] == selection][['RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Year','Primary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance
genre_secondary_rating_yearly = music_df[music_df['Primary Genre'] == selection][['RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Year','Primary Genre', 'Secondary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance
genre_rating_yearly_specifics = music_df[music_df['Primary Genre'] == selection][['Artist','Album','RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Artist','Album','Year','Primary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance



fig = px.scatter(genre_rating_yearly, y = 'RYM Rating', x = 'Year', hover_name =  'Primary Genre', size = 'Ratings', title = selection + " Genre Performance", trendline = "ols")
fig.update_layout(title_x=0.55, showlegend= False,margin=dict(
            l=0,
            r=0,
            b = 78,
            t = 60
        ))
fig_box  = px.scatter(genre_secondary_rating_yearly, y = 'RYM Rating', x = 'Year', hover_name =  'Secondary Genre', hover_data = ['Primary Genre'], size = 'Ratings', title = selection + " Secondary Genre Performance", color = 'Secondary Genre')
fig_box.update_layout(
        yaxis = dict(
            visible = False
        ),
      margin=dict(
            l=0,
            r=0,
            b = 78,
            t = 60
        )
    )
fig_bub  = px.scatter(genre_rating_yearly_specifics, y = 'RYM Rating', x = 'Year', hover_name =  'Artist', hover_data = ['Album','Artist'], size = 'Ratings', color = 'Artist', title = "Artists and Albums in "+selection)
fig_bub.update_layout(
        yaxis = dict(
            visible = False
        ),
      margin=dict(
            l=  0,
            r=0,
            b = 78,
            t = 60
        )
    )


app.layout = html.Div([

    html.Div([
        html.H4('Genre Selection: ',style= {'width': '33%', 'display': 'inline-block', 'text-align':'center'}),

         dcc.Dropdown(
                id='genre_selection',
                options=[{'label': j, 'value': i} for i, j in zip(range(len(list_of_genres)), list_of_genres)],
                #value='621397',
                style= {'width': '50%','display': 'inline-block', }
            ),
         
       html.Div([
            dcc.Graph(id='g1', figure=fig)
       ], className="three columns"),

        html.Div([
            dcc.Graph(id='g2', figure=fig_box,style={'display': 'flex'})
        ], className="three columns"),
        html.Div([
      #      html.H3(' '),
            dcc.Graph(id='g3', figure=fig_bub,style={'display': 'flex'})
        ],className="five columns" ),

         
    ]) #className="row")

])




@app.callback(
    Output('g1', 'figure'),
    Output('g2', 'figure'),
    Output('g3', 'figure'),
    Input('genre_selection','value')
    )

def update_graph(genre_selection):

    if (genre_selection == None):
        return dash.no_update,dash.no_update,dash.no_update
    
    print(genre_selection)
    selection = list_of_genres[genre_selection]
    genre_rating_yearly = music_df[music_df['Primary Genre'] == selection][['RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Year','Primary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance
    genre_secondary_rating_yearly = music_df[music_df['Primary Genre'] == selection][['RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Year','Primary Genre', 'Secondary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance
    genre_rating_yearly_specifics = music_df[music_df['Primary Genre'] == selection][['Artist','Album','RYM Rating','Ratings','Year','Primary Genre', 'Secondary Genre']].groupby(by = ['Artist','Album','Year','Primary Genre']).agg({'RYM Rating':'mean','Ratings':'sum'}).reset_index() #For graphing genre and performance


    #if (len(throwers[throwers['pitcher'] == player_id_r]['player_name'].unique()) == 0):
    #    raise PreventUpdate
    
    # bar plot
    fig = px.scatter(genre_rating_yearly, y = 'RYM Rating', x = 'Year', hover_name =  'Primary Genre', size = 'Ratings', title = selection + " Genre Performance",trendline = "ols")
    fig.update_layout(title_x=0.55, showlegend= False,margin=dict(
                l=30,
                r=0,
                b = 78,
                t = 60
            ))
    if (genre_secondary_rating_yearly['Secondary Genre'].empty):
        fig_box = px.scatter(genre_rating_yearly, y = 'RYM Rating', x = 'Year', hover_name =  'Primary Genre', size = 'Ratings', title =  "No Secondary Genres Found")
        fig.update_layout(title_x=0.55, showlegend= False,margin=dict(
                l=0,
                r=0,
                b = 78,
                t = 60
            ))
    else:
        fig_box  = px.scatter(genre_secondary_rating_yearly, y = 'RYM Rating', x = 'Year', hover_name =  'Secondary Genre', hover_data = ['Primary Genre'], size = 'Ratings', title = selection + " Secondary Genre Performance", color = 'Secondary Genre')
        fig_box.update_layout(
                yaxis = dict(
                    visible = False
                ),
              margin=dict(
                    l=0,
                    r=0,
                    b = 78,
                    t = 60
                )
            )
    fig_bub  = px.scatter(genre_rating_yearly_specifics, y = 'RYM Rating', x = 'Year', hover_name =  'Artist', hover_data = ['Album','Artist'], size = 'Ratings', color = 'Artist', title = "Artists and Albums in "+selection,width = 600)
    fig_bub.update_layout(
            yaxis = dict(
                visible = False
            ),
          margin=dict(
                l=  0,
                r=0,
                b = 78,
                t = 60
            )
        )
    return fig, fig_box, fig_bub



if __name__ == '__main__':
    app.run_server(debug=True)