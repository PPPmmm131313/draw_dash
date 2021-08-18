import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import io
import pandas as pd

def test():
    print(1)

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
    # TODO добавить название графиков
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