from typing import Callable

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ALL
from plotly.subplots import make_subplots


def draw_dash(test_df, param_dict: list, test_func: Callable) -> object:
    """
    построение dash (! есть глобальная переменная all_ranges_for_figures)

    :param test_df:
    :param param_dict: лист со словарем для dropdown [{'label':'label_smth', 'value':'value_smth'}]
    :param test_func: функция отрисовки в зависимрсти от параметра, мин и макс
    :return: ссылка на построенный dash

    example:
    --------
    >>> param_dict = [{'label': i, 'value': i} for i in ['test1', 'test2', 'test3']]
    >>> df = pd.DataFrame([[1, 'test1', 10], [2, 'test1', 11], [3, 'test1', 17],
    >>>                    [1, 'test2', 3], [2, 'test2', 5],
    >>>                    [1, 'test3', 1.5], [2, 'test3', 3]],
    >>>                   columns=['data', 'param_id', 'tm_value'])
    >>> def example_func(figure, df, i_name, secondary_y):
    >>>         figure.add_trace(go.Scatter(x = df[df.param_id == i_name].data, y = df[df.param_id == i_name].tm_value, name=i_name), secondary_y=secondary_y)
    >>>         min_r = min(df.data.values)
    >>>         max_r = max(df.data.values)
    >>>         return figure, min_r, max_r
    >>>
    >>> draw_dash(df, param_dict, example_func)
    """
    # TODO: переписать нормально с входным dataframe и upload files func
    # style
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = dash.Dash(external_stylesheets=external_stylesheets)
    all_ranges_for_figures = []

    # functions
    def get_index_of_range(all_ranges):
        # TODO: перепесать без глобальной пременной
        global all_ranges_for_figures
        try:
            all_r = [
                all_ranges[i]["layout"]["xaxis"]["range"]
                for i in range(len(all_ranges))
            ]
            if len(all_r) == len(all_ranges_for_figures):
                compere = np.array(
                    [x == y for x, y in zip(all_r, all_ranges_for_figures)]
                )
                c_ind = np.where(compere == False)
                return c_ind
        except BaseException:
            return []

    def number_plot(a_plot, r_plot):
        num = a_plot - r_plot
        if num > 0:
            return num, dict()
        else:
            return num, dict(display="none")

    def add_dropdown(id_index, type_drop="filter-dropdown", style_dropdown=dict()):
        fig_dropdown = html.Div(
            [
                dcc.Dropdown(
                    id={"type": type_drop, "index": id_index},
                    options=param_dict,
                    style=style_dropdown,
                    value=None,
                    multi=True,
                )
            ]
        )
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

    ###
    upload_data = dcc.Upload(
        html.Button("Upload File"), id="upload_data", multiple=True
    )
    button_add = html.Button("+", id="add_plot", n_clicks=0, value="0")
    button_remove = html.Button(
        "-", id="remove_plot", n_clicks=0, style=dict(display="none")
    )

    button_s = html.Button(
        children="Sync. all",
        id="synchronize_button",
        value="unsynchronized",
        n_clicks=0,
        style={"background-color": "white", "color": "black"},
    )

    fig_plots = html.Div(id="fig_plot", children=[])
    app.layout = html.Div(
        [upload_data, button_add, button_remove, html.Br(), button_s, fig_plots]
    )

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
        global all_ranges_for_figures
        n_plot, hidden = number_plot(a_plot, r_plot)
        if n_plot > int(value):
            area = html.Div(id={"type": "fig_plot", "index": n_plot})
            fig_dropdown = add_dropdown(n_plot)
            fig_dropdown_second = add_dropdown(
                n_plot,
                type_drop="filter_second_ax",
                style_dropdown=dict(display="none"),
            )

            s_a = dcc.Checklist(
                id={"type": "second_ax", "index": n_plot},
                options=[{"label": "Second ax", "value": "s_a"}],
            )

            children.extend([s_a, fig_dropdown, fig_dropdown_second, area])
        else:
            children = children[:-4]

        all_ranges_for_figures = [[-1, 6] for i in range(n_plot)]
        return children, hidden, str(n_plot)

    @app.callback(
        # output
        Output({"type": "filter_second_ax", "index": ALL}, "style"),
        # input
        Input({"type": "second_ax", "index": ALL}, "value"),
    )
    def second_ax(button_type):
        styles_drop = []
        for i in button_type:
            add = dict(display="none") if i != ["s_a"] else dict()
            styles_drop.append(add)
        return styles_drop

    @app.callback(
        # output
        Output({"type": "filter-dropdown", "index": ALL}, "options"),
        Output({"type": "filter_second_ax", "index": ALL}, "options"),
        # input
        [Input("upload_data", "filename")],
        [State({"type": "filter-dropdown", "index": ALL}, "options")],
    )
    def name_to_drop_down(filename, exist_opt):
        if filename is not None:
            for i in range(len(filename)):
                exist_opt[0].append({"label": filename[i][:-5], "value": filename[i][:-5]})
                exist_opt[0] = set_dict(exist_opt[0])
        return [exist_opt[0] for i in range(len(exist_opt))], [
            exist_opt[0] for i in range(len(exist_opt))
        ]

    @app.callback(
        # output
        Output({"type": "fig_plot", "index": ALL}, "children"),
        # input
        Input({"type": "filter-dropdown", "index": ALL}, "value"),
        Input({"type": "filter_second_ax", "index": ALL}, "value"),
        Input({"type": "second_ax", "index": ALL}, "value"),
    )
    def update_output(filename, second_data, second_type):
        global all_ranges_for_figures
        return_list = []
        ind = 0

        for i_drop_name in filename:
            if i_drop_name:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                min_r = []
                max_r = []
                for i_name in i_drop_name:
                    fig, min_range, max_range = test_func(fig, test_df, i_name, False)
                    min_r.append(min_range)
                    max_r.append(max_range)
                if second_type[ind] == ["s_a"] and second_data[ind]:
                    for i_name in second_data[ind]:
                        fig, min_range, max_range = test_func(fig, test_df, i_name, True)
                        min_r.append(min_range)
                        max_r.append(max_range)
                all_ranges_for_figures[ind] = [min(min_r), max(max_r)]
                fig.update_layout(
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                    )
                )

                ind += 1
                return_list.append(
                    [
                        dcc.Graph(
                            figure=fig, id={"type": "figure", "index": len(return_list)}
                        )
                    ]
                )
            else:
                return_list.append(
                    [
                        dcc.Graph(
                            figure=go.Figure(),
                            id={"type": "figure", "index": len(return_list)},
                        )
                    ]
                )

        return return_list

    @app.callback(
        # output
        Output({"type": "figure", "index": ALL}, "figure"),
        Output("synchronize_button", "value"),
        Output("synchronize_button", "style"),
        Output("synchronize_button", "children"),
        # input
        [Input({"type": "figure", "index": ALL}, "relayoutData")], # this triggers the event
        Input("synchronize_button", "n_clicks"),
        Input("synchronize_button", "value"),
        Input("synchronize_button", "style"),
        Input("synchronize_button", "children"),
        [State({"type": "figure", "index": ALL}, "figure")],
    )
    def test(trigger, n_clicks, synch_value, synch_style, button_name, fig_ranges):
        global all_ranges_for_figures
        # TODO: rename n_clicks%2
        if n_clicks % 2 == 1:
            synch_value = "synchronize_all"
            synch_style = {"background-color": "lightsteelblue", "color": "black"}
        else:
            synch_value = "unsynchronized"
            synch_style = {"background-color": "white", "color": "black"}

        if len(fig_ranges) > 1:
            if n_clicks % 2 == 1:
                try:
                    i_range = get_index_of_range(fig_ranges)[0]
                except BaseException:
                    i_range = np.array([])
                if i_range.size > 0:
                    for j in range(len(fig_ranges)):
                        fig_ranges[j]["layout"]["xaxis"]["range"] = fig_ranges[
                            i_range[0]
                        ]["layout"]["xaxis"]["range"]

        all_ranges_for_figures = [
            fig_ranges[j]["layout"]["xaxis"]["range"] for j in range(len(fig_ranges))
        ]
        return fig_ranges, synch_value, synch_style, button_name

    return app.run_server(debug=True, use_reloader=False)