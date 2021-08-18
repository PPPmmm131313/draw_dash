import dash
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd



def draw_dash(param_dict, df_input):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(external_stylesheets=external_stylesheets)
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
                options=param_dict,
                style=style_in,
                value=None,
                multi=True
            )])
        return fig_dropdown

    button_add = html.Button("+",
                             id="add_plot",
                             n_clicks=0,
                             value='0')
    button_remove = html.Button("-",
                                id="remove_plot",
                                n_clicks=0,
                                style=dict(display='none'))
    fig_plots = html.Div(id='fig_plot', children=[])
    app.layout = html.Div([button_add, button_remove, fig_plots])


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
        if n_plot == 0:
            children, hidden, str(n_plot)
        if n_plot > int(value):
            area = html.Div(id={'type': 'fig_plot', 'index': n_plot})
            fig_dropdown = add_dropdown(n_plot)
            children.extend([fig_dropdown, area])
        else:
            children = children[:-2]

        return children, hidden, str(n_plot)


    @app.callback(
        # output
        Output({'type': 'fig_plot', 'index': ALL}, 'children'),
        # input
        Input({'type': 'filter-dropdown', 'index': ALL}, 'value')
    )
    def update_output(filename):
        return_list = []
        for i_drop_name in filename:
            if i_drop_name:
                fig = go.Figure()
                for i_name in i_drop_name:
                    fig.add_trace(go.Scatter(x=df_input.loc[df_input.param_id == i_name].date.values, y=df_input.loc[df_input.param_id == i_name].value.values, name=i_name))
                    # TODO: добавить функцию для доп отрисовки
                    fig.update_layout(legend=dict(orientation="h",
                                                  yanchor="bottom",
                                                  y=1.02,
                                                  xanchor="right",
                                                  x=1))

                return_list.append([dcc.Graph(figure=fig)])
            else:
                return_list.append([dcc.Graph(figure=go.Figure())])
        return return_list


    return app.run_server(debug=True, use_reloader=False)