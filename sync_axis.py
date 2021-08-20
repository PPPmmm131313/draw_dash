import dash
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from typing import Callable


def draw_dash(param_dict: list, test_func: Callable) -> object:
    """
        построение dash (! есть глобальная переменная all_ranges_for_figures)

        :param param_dict: лист со словарем для dropdown [{'label': 'label_smth', 'value': 'value_smth'}...]
        :param test_func: функция отрисовки на figure в зависимости от значения в dropdown с мин и макс значечниями
        :return: ссылка на построенный dash

        example:
        --------
        >>> dropdown_values = ['test1', 'test2']
        >>> param_dict = [{'label': i, 'value': i} for i in dropdown_values]
        >>> df = pd.DataFrame([[1, 'test1', 10], [2, 'test1', 11], [1, 'test2', 3], [3, 'test2', 5]],
        >>>                     columns=['data', 'param_id', 'tm_value'])
        >>> def example_func(figure, dropdown_name):
        >>>     min_r = []
        >>>     max_r = []
        >>>     for i_name in dropdown_name:
        >>>         figure.add_trace(go.Scatter(x=df[df.param_id == i_name].data, y=df[df.param_id == i_name].tm_value, name=i_name))
        >>>         min_r.append(min(df.data.values))
        >>>         max_r.append(max(df.data.values))
        >>>     figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        >>>     return figure, min_r, max_r
        >>>
        >>> plot_func.draw_dash(param_dict, example_func)
        """

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(external_stylesheets=external_stylesheets)
    all_ranges_for_figures = []

    def get_index_of_range(all_ranges):
        # TODO: перепесать без глобальной пременной
        global all_ranges_for_figures
        try:
            all_r = [all_ranges[i]['layout']['xaxis']['range']
                     for i in range(len(all_ranges))]
            if len(all_r) == len(all_ranges_for_figures):
                compere = np.array(
                    [x == y for x, y in zip(all_r, all_ranges_for_figures)])
                c_ind = np.where(compere == False)
                return c_ind
        except BaseException:
            return []

    def number_plot(a_plot, r_plot):
        num = a_plot - r_plot
        if num > 0:
            return num, dict()
        else:
            return num, dict(display='none')

    def add_dropdown(id_index):
        fig_dropdown = html.Div([
            dcc.Dropdown(id={
                'type': 'filter-dropdown',
                'index': id_index
            },
                options=param_dict,
                style=dict(),
                value=None,
                multi=True
            )])
        return fig_dropdown
    ###

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
    app.layout = html.Div(
        [button_add, button_remove, html.Br(), button_s, fig_plots])

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
        State({'type': 'filter-dropdown', 'index': ALL}, 'options')  # trigger
    )
    def add_smth_new(a_plot, r_plot, value, children, filename):
        global all_ranges_for_figures
        n_plot, hidden = number_plot(a_plot, r_plot)
        if n_plot > int(value):
            area = html.Div(id={'type': 'fig_plot', 'index': n_plot})
            fig_dropdown = add_dropdown(n_plot)
            children.extend([fig_dropdown, area])
        else:
            children = children[:-2]

        all_ranges_for_figures = [[-1, 6] for i in range(n_plot)]
        return children, hidden, str(n_plot)

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
                fig, min_r, max_r = test_func(fig, i_drop_name)
                all_ranges_for_figures[ind] = [min(min_r), max(max_r)]
                ind += 1
                return_list.append(
                    [dcc.Graph(figure=fig, id={'type': 'figure', 'index': len(return_list)})])
            else:
                return_list.append([dcc.Graph(figure=go.Figure(), id={
                                   'type': 'figure', 'index': len(return_list)})])

        return return_list

    @app.callback(
        # output
        Output({'type': 'figure', 'index': ALL}, 'figure'),
        Output('synchronize_button', 'value'),
        Output('synchronize_button', 'style'),
        Output('synchronize_button', 'children'),
        # input
        # this triggers the event
        [Input({'type': 'figure', 'index': ALL}, 'relayoutData')],
        Input('synchronize_button', 'n_clicks'),
        Input('synchronize_button', 'value'),
        Input('synchronize_button', 'style'),
        Input('synchronize_button', 'children'),
        [State({'type': 'figure', 'index': ALL}, 'figure')])
    def test(
            trigger,
            n_clicks,
            synch_value,
            synch_style,
            button_name,
            fig_ranges):
        global all_ranges_for_figures
        # TODO: rename n_clicks%2
        if n_clicks % 2 == 1:
            synch_value = 'synchronize_all'
            synch_style = {
                'background-color': 'lightsteelblue',
                'color': 'black'}
        else:
            synch_value = 'unsynchronized'
            synch_style = {'background-color': 'white', 'color': 'black'}

        if len(fig_ranges) > 1:
            if n_clicks % 2 == 1:
                try:
                    i_range = get_index_of_range(fig_ranges)[0]
                except BaseException:
                    i_range = np.array([])
                if i_range.size > 0:
                    for j in range(len(fig_ranges)):
                        fig_ranges[j]['layout']['xaxis']['range'] = fig_ranges[i_range[0]
                                                                               ]['layout']['xaxis']['range']

        all_ranges_for_figures = [
            fig_ranges[j]['layout']['xaxis']['range'] for j in range(
                len(fig_ranges))]
        return fig_ranges, synch_value, synch_style, button_name

    return app.run_server(debug=True, use_reloader=False)
