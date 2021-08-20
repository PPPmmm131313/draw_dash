import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
path = 'D:/нтц/jupyter lab test/выгрузка из АДКУ за 1.01-31.07.2021/'

## functions
def number_plot(a_plot, r_plot):
    num = a_plot - r_plot
    if num > 0:
        return num, dict()
    else:
        return num, dict(display='none')


def add_dropdown(id_index, style_in=dict()):
    fig_dropdown = html.Div([
        dcc.Dropdown(id={
            'type': 'filter-dropdown',
            'index': id_index
        },
            options=[],
            style=style_in,
            value=None,
            multi=True
        )])
    return fig_dropdown


def set_dict(list_dict):
    if list_dict == []:
        return list_dict
    seen = set()
    new_list = []
    for d in list_dict:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_list.append(d)
    return new_list


def normal_df(df):
    df = df.rename(columns={'Unnamed: 0': 'date', 'Unnamed: 1': 'value'})
    df = df.drop([0, 1])
    df = df.dropna(subset=['date', 'value']).reset_index(drop=True)
    df.date = df.date.astype('datetime64')
    return df


###

upload_data = dcc.Upload(html.Button('Upload File'),
                         id='upload_data',
                         multiple=True)
button_add = html.Button("+",
                         id="add_plot",
                         n_clicks=0,
                         value='0')
button_remove = html.Button("-",
                            id="remove_plot",
                            n_clicks=0,
                            style=dict(display='none'))
fig_plots = html.Div(id='fig_plot', children=[])
app.layout = html.Div([upload_data, button_add, button_remove, fig_plots])


@app.callback(
    # output
    Output('fig_plot', 'children'),
    Output('remove_plot', 'style'),
    Output('add_plot', 'value'),
    # input
    Input('add_plot', 'n_clicks'),
    Input('remove_plot', 'n_clicks'),
    State('add_plot', 'value'),
    State('fig_plot', 'children'),
    State({'type': 'filter-dropdown', 'index': ALL}, 'options')
)
def add_smth_new(a_plot, r_plot, value, children, filename):
    n_plot, hidden = number_plot(a_plot, r_plot)
    if n_plot > int(value):
        area = html.Div(id={'type': 'fig_plot', 'index': n_plot})
        fig_dropdown = add_dropdown(n_plot)
        children.extend([fig_dropdown, area])
    else:
        children = children[:-2]

    return children, hidden, str(n_plot)


@app.callback(
    # output
    Output({'type': 'filter-dropdown', 'index': ALL}, 'options'),
    # input
    [Input('upload_data', 'filename')],
    [State({'type': 'filter-dropdown', 'index': ALL}, 'options')]
)
def name_to_drop_down(filename, exist_opt):
    if filename != None:
        for i in range(len(filename)):
            exist_opt[0].append({'label': filename[i][:-5], 'value': filename[i]})
            exist_opt[0] = set_dict(exist_opt[0])
    return [exist_opt[0] for i in range(len(exist_opt))]


@app.callback(
    # output
    Output({'type': 'fig_plot', 'index': ALL}, 'children'),
    # input
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value')
)
def update_output(filename):
    return_list = []
    # TODO: добавить сравнение с прошлым списком, чтоб не отрисовывать старые
    for i_drop_name in filename:
        if i_drop_name:
            fig = go.Figure()
            for i_name in i_drop_name:
                df_read = pd.read_excel(path + i_name)
                df = normal_df(df_read)
                fig.add_trace(go.Scatter(x=df.date, y=df.value, name=i_name[:-5]))
                fig.update_layout(legend=dict(orientation="h",
                                              yanchor="bottom",
                                              y=1.02,
                                              xanchor="right",
                                              x=1))
            return_list.append([dcc.Graph(figure=fig)])
        else:
            return_list.append([dcc.Graph(figure=go.Figure())])
    return return_list


app.run_server(debug=True, use_reloader=False)


### sync

import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import io
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
all_ranges_for_figures = []


def get_index_of_range(all_ranges):
    global all_ranges_for_figures
    try:
        all_r = [all_ranges[i]['layout']['xaxis']['range'] for i in range(len(all_ranges))]
        if len(all_r) == len(all_ranges_for_figures):
            compere = np.array([x == y for x, y in zip(all_r, all_ranges_for_figures)])
            c_ind = np.where(compere == False)
            return c_ind
    except:
        return []


def number_plot(a_plot, r_plot):
    num = a_plot - r_plot
    if num > 0:
        return num, dict()
    else:
        return num, dict(display='none')


def add_dropdown(id_index, style_in=dict()):
    fig_dropdown = html.Div([
        dcc.Dropdown(id={
            'type': 'filter-dropdown',
            'index': id_index
        },
            options=[],
            style=style_in,
            value=None,
            multi=True
        )])
    return fig_dropdown


def set_dict(list_dict):
    if list_dict == []:
        return list_dict
    seen = set()
    new_list = []
    for d in list_dict:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_list.append(d)
    return new_list


def normal_df(df):
    df = df.rename(columns={'Unnamed: 0': 'date', 'Unnamed: 1': 'value'})
    df = df.drop([0, 1])
    df = df.dropna(subset=['date', 'value']).reset_index(drop=True)
    df.date = df.date.astype('datetime64')
    return df


def get_max_range(all_ranges, type_sync):
    ranges = [all_ranges[i]['layout']['xaxis']['range'] for i in range(len(all_ranges))]

    if type_sync == 1:
        min_range = min(list(zip(*ranges))[0])
        max_range = max(list(zip(*ranges))[1])
    else:
        min_range = max(list(zip(*ranges))[0])
        max_range = min(list(zip(*ranges))[1])
    r_range = [min_range, max_range]
    return r_range


###

upload_data = dcc.Upload(html.Button('Upload File'),
                         id='upload_data',
                         multiple=True)
button_add = html.Button("+",
                         id="add_plot",
                         n_clicks=0,
                         value='0')
button_remove = html.Button("-",
                            id="remove_plot",
                            n_clicks=0,
                            style=dict(display='none'))

button_s = html.Button(children="Sync. all",
                       id="synchronize_button",
                       value='unsynchronized',
                       n_clicks=0,
                       style={'background-color': 'white',
                              'color': 'black'})

fig_plots = html.Div(id='fig_plot', children=[])
app.layout = html.Div([upload_data, button_add, button_remove, html.Br(), button_s, fig_plots])


@app.callback(
    # output
    Output('fig_plot', 'children'),
    Output('remove_plot', 'style'),
    Output('add_plot', 'value'),
    # input
    Input('add_plot', 'n_clicks'),
    Input('remove_plot', 'n_clicks'),
    State('add_plot', 'value'),
    State('fig_plot', 'children'),
    State({'type': 'filter-dropdown', 'index': ALL}, 'options')
)
def add_smth_new(a_plot, r_plot, value, children, filename):
    global all_ranges_for_figures
    n_plot, hidden = number_plot(a_plot, r_plot)
    #     if n_plot ==0:
    #         children, hidden, str(n_plot)
    if n_plot > int(value):
        area = html.Div(id={'type': 'fig_plot', 'index': n_plot})
        fig_dropdown = add_dropdown(n_plot)
        children.extend([fig_dropdown, area])
    #         all_ranges_for_figures.append([-1, 6])
    else:
        children = children[:-2]

    all_ranges_for_figures = [[-1, 6] for i in range(n_plot)]
    return children, hidden, str(n_plot)


@app.callback(
    # output
    Output({'type': 'filter-dropdown', 'index': ALL}, 'options'),
    # input
    [Input('upload_data', 'filename')],
    [State({'type': 'filter-dropdown', 'index': ALL}, 'options')]
)
def name_to_drop_down(filename, exist_opt):
    if filename != None:
        for i in range(len(filename)):
            exist_opt[0].append({'label': filename[i][:-5], 'value': filename[i]})
            exist_opt[0] = set_dict(exist_opt[0])
    return [exist_opt[0] for i in range(len(exist_opt))]


@app.callback(
    # output
    Output({'type': 'fig_plot', 'index': ALL}, 'children'),
    # input
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value')
)
def update_output(filename):
    global all_ranges_for_figures
    return_list = []
    ind = 0
    for i_drop_name in filename:
        if i_drop_name:
            fig = go.Figure()
            min_r = []
            max_r = []
            for i_name in i_drop_name:
                df_read = pd.read_excel('выгрузка из АДКУ за 1.01-31.07.2021/' + i_name)
                df = normal_df(df_read)
                fig.add_trace(go.Scatter(x=df.date, y=df.value, name=i_name[:-5]))
                fig.update_layout(legend=dict(orientation="h",
                                              yanchor="bottom",
                                              y=1.02,
                                              xanchor="right",
                                              x=1))
                min_r.append(min(df.date.values))
                max_r.append(max(df.date.values))
            all_ranges_for_figures[ind] = [min(min_r), max(max_r)]
            ind += 1
            return_list.append([dcc.Graph(figure=fig, id={'type': 'figure', 'index': len(return_list)})])
        else:
            return_list.append([dcc.Graph(figure=go.Figure(), id={'type': 'figure', 'index': len(return_list)})])

    return return_list


@app.callback(
    # output
    Output({'type': 'figure', 'index': ALL}, 'figure'),
    Output('synchronize_button', 'value'),
    Output('synchronize_button', 'style'),
    Output('synchronize_button', 'children'),
    # input
    [Input({'type': 'figure', 'index': ALL}, 'relayoutData')],  # this triggers the event
    Input('synchronize_button', 'n_clicks'),
    Input('synchronize_button', 'value'),
    Input('synchronize_button', 'style'),
    Input('synchronize_button', 'children'),
    [State({'type': 'figure', 'index': ALL}, 'figure')])
def test(trigger, n_clicks, synch_value, synch_style, button_name, fig_ranges):
    global all_ranges_for_figures
    # TODO: rename n_clicks%2
    if n_clicks % 2 == 1:
        synch_value = 'synchronize_all'
        synch_style = {'background-color': 'lightsteelblue', 'color': 'black'}
    else:
        synch_value = 'unsynchronized'
        synch_style = {'background-color': 'white', 'color': 'black'}

    if len(fig_ranges) > 1:
        if n_clicks % 2 == 1:
            try:
                i_range = get_index_of_range(fig_ranges)[0]
            except:
                i_range = np.array([])
            if i_range.size > 0:
                for j in range(len(fig_ranges)):
                    fig_ranges[j]['layout']['xaxis']['range'] = fig_ranges[i_range[0]]['layout']['xaxis']['range']

    all_ranges_for_figures = [fig_ranges[j]['layout']['xaxis']['range'] for j in range(len(fig_ranges))]
    return fig_ranges, synch_value, synch_style, button_name


app.run_server(debug=True, use_reloader=False)