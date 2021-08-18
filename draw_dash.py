from typing import Callable
from dash.dependencies import Input, Output, State, ALL
import dash
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html


def draw_dash(param_dict: list, test_func: Callable) -> object:
    """
    построение dash

    :param param_dict: лист со словарем для dropdown [{'label': 'label_smth', 'value': 'value_smth'}...]
    :param test_func: функция отрисовки на figure в зависимости от значения в dropdown
    :return: ссылка на построенный dash

    example:
    --------
    >>> import draw_dash as d_dash
    >>> import pandas as pd
    >>> import plotly.graph_objects as go
    >>> dropdown_values = ['test1', 'test2']
    >>> param_dict = [{'label': i, 'value': i} for i in dropdown_values]
    >>> df = pd.DataFrame([[1, 'test1', 10], [2, 'test1', 11], [1, 'test2', 3], [2, 'test2', 5]], columns=['data', 'param_id', 'tm_value'])
    >>> def example_func(figure, dropdown_name):
    >>>     for i_name in dropdown_name:
    >>>         figure.add_trace(go.Scatter(x=df[df.param_id == i_name].data, y=df[df.param_id == i_name].tm_value, name=i_name))
    >>>     figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    >>>     return figure
    >>> d_dash.draw_dash(param_dict, example_func)
    """

    # style
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = dash.Dash(external_stylesheets=external_stylesheets)
    # functions

    def number_plot(a_plot, r_plot):
        num = a_plot - r_plot
        r_dict = dict() if num > 0 else dict(display="none")
        return num, r_dict

    def add_dropdown(id_index):
        fig_dropdown = html.Div(
            [
                dcc.Dropdown(
                    id={"type": "filter-dropdown", "index": id_index},
                    options=param_dict,
                    style=dict(),
                    value=None,
                    multi=True,
                )
            ]
        )
        return fig_dropdown

    # dash layout
    button_add = html.Button("+", id="add_plot", n_clicks=0, value="0")
    button_remove = html.Button(
        "-", id="remove_plot", n_clicks=0, style=dict(display="none")
    )
    fig_plots = html.Div(id="fig_plot", children=[])
    app.layout = html.Div([button_add, button_remove, fig_plots])
    # callbacks

    @app.callback(
        # output
        Output("fig_plot", "children"),
        Output("remove_plot", "style"),
        Output("add_plot", "value"),
        # input
        Input("add_plot", "n_clicks"),
        Input("remove_plot", "n_clicks"),
        State("add_plot", "value"),
        State("fig_plot", "children"),
        State({"type": "filter-dropdown", "index": ALL}, "options"),
    )
    def add_smth_new(a_plot, r_plot, value, children, filename):
        n_plot, hidden = number_plot(a_plot, r_plot)
        # if n_plot == 0:
        #     children, hidden, str(n_plot)
        if n_plot > int(value):
            area = html.Div(id={"type": "fig_plot", "index": n_plot})
            fig_dropdown = add_dropdown(n_plot)
            children.extend([fig_dropdown, area])
        else:
            children = children[:-2]

        return children, hidden, str(n_plot)

    @app.callback(
        # output
        Output({"type": "fig_plot", "index": ALL}, "children"),
        # input
        Input({"type": "filter-dropdown", "index": ALL}, "value"),
    )
    def update_output(filename):
        return_list = []
        for i_drop_name in filename:
            if i_drop_name:
                fig = go.Figure()
                fig = test_func(fig, i_drop_name)
                return_list.append([dcc.Graph(figure=fig)])
            else:
                return_list.append([dcc.Graph(figure=go.Figure())])
        return return_list

    return app.run_server(debug=True, use_reloader=False)
