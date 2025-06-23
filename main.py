import dash
from dash import dcc, html, Output, Input, State, callback_context, no_update
import pandas as pd
import base64
import io
from datetime import datetime, date, timedelta
import json
import os
from github_storage_manager import GitHubDataManager
from components import make_sidebar, make_sidebar_toggle_pc, make_sidebar_toggle_mobile
from components import layout_pc, layout_mobile

# --- Data setup ---
def load_default_data():
    data_rows = [
        ['ELC', 90.18, 80, 76, 4, 91.62, 85.00, 99.11, 85.00],
        ['GGW', 87.54, 168, 168, 0, 85.00, 95.17, 85.00, 85.00],
        ['HSK', 85.65, 180, 180, 0, 87.62, 85.00, 85.00, 85.00],
        ['LFS', 86.28, 300, 296, 4, 85.00, 88.96, 85.00, 86.16],
        ['MAP', 87.78, 84, 82, 2, 85.00, 85.00, 88.12, 85.00],
        ['MTL', 90.84, 160, 157, 3, 85.00, 94.70, 98.67, 85.00],
        ['STLC', 85.00, 160, 154, 6, 85.00, 85.00, 85.00, 85.00],
        ['HK_avg', 88.50, 150, 148, 2, 85.00, 87.50, 90.00, 88.50],
        ['GuangZhou', 86.25, 140, 135, 5, 83.00, 87.50, 88.00, 86.50],
        ['Yantian (ZhongTong)', 89.75, 120, 118, 2, 88.00, 90.50, 91.00, 89.50],
        ['Chengdu', 84.50, 160, 152, 8, 82.00, 85.00, 86.00, 85.00],
        ['Pinghu', 87.80, 100, 98, 2, 86.00, 88.50, 89.00, 87.50],
        ['SC_avg', 87.00, 130, 126, 4, 84.75, 87.88, 88.50, 87.13]
    ]
    week_cols = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    df = pd.DataFrame(
        data_rows,
        columns=['Site', 'Monthly Performance', 'Max/Month', 'Completed', 'Missing'] + week_cols
    ).set_index('Site')
    return df, week_cols

# Initialize GitHub data manager
data_manager = GitHubDataManager()
df_default, week_cols = load_default_data()

# Ensure default data exists for current month
def get_last_month():
    """获取上个月的年月字符串"""
    today = datetime.now()
    if today.month == 1:
        last_month = datetime(today.year - 1, 12, 1)
    else:
        last_month = datetime(today.year, today.month - 1, 1)
    return last_month.strftime("%Y-%m")

current_year_month = get_last_month()  # 默认显示上个月

if not data_manager.data_exists(current_year_month):
    data_manager.save_data(current_year_month, df_default)

# --- Dash App Setup ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Client-side callback for device detection
app.clientside_callback(
    """
    function(n) {
        if (window.innerWidth <= 768 || /iphone|android|mobile|phone/i.test(navigator.userAgent)) {
            return 'mobile';
        } else {
            return 'pc';
        }
    }
    """,
    Output('device-store', 'data'),
    Input('init-load', 'n_intervals')
)

# Main app layout
app.layout = html.Div([
    dcc.Interval(id='init-load', interval=200, n_intervals=0, max_intervals=1),
    dcc.Store(id='device-store', data='pc'),
    dcc.Store(id='data-store', data=df_default.to_dict('index')),
    dcc.Store(id='week-cols-store', data=week_cols),
    dcc.Store(id='sidebar-open', data=False),
    dcc.Store(id='selected-sites', data=['HK_avg', 'SC_avg']),  # Default show HK_avg and SC_avg
    dcc.Store(id='selected-gauges', data=['HK_avg', 'SC_avg']),  # Default show HK_avg and SC_avg gauges
    dcc.Store(id='current-month', data=current_year_month),
    html.Div(id="app-container")
])

# Sidebar control callbacks
@app.callback(
    [Output('sidebar', 'style'),
     Output('sidebar-open', 'data')],
    [Input('open-sidebar', 'n_clicks'),
     Input('open-sidebar-mobile', 'n_clicks'),
     Input('close-sidebar', 'n_clicks')],
    [State('sidebar-open', 'data')],
    prevent_initial_call=True
)
def toggle_sidebar(open_clicks, open_mobile_clicks, close_clicks, is_open):
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    sidebar_hidden_style = {
        'position': 'fixed', 'top': '0', 'right': '-400px', 'width': '400px', 'height': '100vh', 
        'backgroundColor': 'white', 'boxShadow': '-2px 0 5px rgba(0,0,0,0.1)', 
        'transition': 'right 0.3s ease', 'zIndex': '1000', 'fontFamily': 'Arial, sans-serif'
    }
    
    sidebar_visible_style = {
        'position': 'fixed', 'top': '0', 'right': '0px', 'width': '400px', 'height': '100vh', 
        'backgroundColor': 'white', 'boxShadow': '-2px 0 5px rgba(0,0,0,0.1)', 
        'transition': 'right 0.3s ease', 'zIndex': '1000', 'fontFamily': 'Arial, sans-serif'
    }
    
    if trigger_id in ['open-sidebar', 'open-sidebar-mobile']:
        return sidebar_visible_style, True
    elif trigger_id == 'close-sidebar':
        return sidebar_hidden_style, False
    
    return no_update, no_update

# Month selection callback
@app.callback(
    [Output('data-store', 'data'),
     Output('current-month', 'data')],
    [Input('month-selector', 'value')],
    prevent_initial_call=True
)
def update_data_from_month_selection(selected_month):
    if selected_month:
        df_month = data_manager.load_data(selected_month)
        if df_month is not None:
            return df_month.to_dict('index'), selected_month
        else:
            # If no data exists for selected month, use default data
            return df_default.to_dict('index'), selected_month
    return no_update, no_update

# File upload callback
@app.callback(
    [Output('data-store', 'data', allow_duplicate=True),
     Output('upload-status', 'children'),
     Output('upload-status', 'style')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-month-selector', 'value')],
    prevent_initial_call=True
)
def update_data_from_upload(contents, filename, upload_month):
    if contents is None:
        return no_update, "", {'display': 'none'}
    
    df_new, message = data_manager.parse_excel_file(contents, filename)
    
    if df_new is not None:
        # Save data for selected month
        target_month = upload_month if upload_month else current_year_month
        success = data_manager.save_data(target_month, df_new)
        
        if success:
            success_style = {'color': '#28A745', 'fontWeight': 'bold'}
            success_message = f"{message} Data saved to GitHub for {target_month}."
            return df_new.to_dict('index'), success_message, success_style
        else:
            error_style = {'color': '#DC3545', 'fontWeight': 'bold'}
            return no_update, "Failed to save to GitHub, saved locally instead.", error_style
    else:
        error_style = {'color': '#DC3545', 'fontWeight': 'bold'}
        return no_update, message, error_style

# Site selection callback for line chart
@app.callback(
    Output('selected-sites', 'data'),
    Input('site-selector', 'value'),
    prevent_initial_call=True
)
def update_selected_sites(selected_sites):
    if not selected_sites:
        return ['HK_avg', 'SC_avg']
    # Ensure HK_avg and SC_avg are always displayed
    if 'HK_avg' not in selected_sites:
        selected_sites.append('HK_avg')
    if 'SC_avg' not in selected_sites:
        selected_sites.append('SC_avg')
    return selected_sites

# Gauge selection callback
@app.callback(
    Output('selected-gauges', 'data'),
    Input('gauge-selector', 'value'),
    prevent_initial_call=True
)
def update_selected_gauges(selected_gauges):
    if not selected_gauges:
        return ['HK_avg', 'SC_avg']
    return selected_gauges

# Quick selection callbacks
@app.callback(
    [Output('site-selector', 'value'),
     Output('gauge-selector', 'value')],
    [Input('select-hk-sites', 'n_clicks'),
     Input('select-sc-sites', 'n_clicks'),
     Input('select-all-sites', 'n_clicks')],
    prevent_initial_call=True
)
def update_quick_selection(hk_clicks, sc_clicks, all_clicks):
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'select-hk-sites':
        # Hong Kong sites
        hk_sites = ['HK_avg', 'ELC', 'GGW', 'HSK', 'LFS', 'MAP', 'MTL', 'STLC']
        return hk_sites, hk_sites
    
    elif trigger_id == 'select-sc-sites':
        # South China sites
        sc_sites = ['SC_avg', 'GuangZhou', 'Yantian (ZhongTong)', 'Chengdu', 'Pinghu']
        return sc_sites, sc_sites
    
    elif trigger_id == 'select-all-sites':
        # All sites
        all_sites = [
            'HK_avg', 'SC_avg', 'ELC', 'GGW', 'HSK', 'LFS', 'MAP', 'MTL', 'STLC',
            'GuangZhou', 'Yantian (ZhongTong)', 'Chengdu', 'Pinghu'
        ]
        return all_sites, all_sites
    
    return no_update, no_update

# Template download callback
@app.callback(
    Output('download-template-file', 'data'),
    Input('download-template', 'n_clicks'),
    prevent_initial_call=True
)
def download_template(n_clicks):
    if n_clicks and n_clicks > 0:
        template_df = df_default.reset_index()
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='5S_Data', index=False)
        
        output.seek(0)
        
        return dict(
            content=base64.b64encode(output.getvalue()).decode(),
            filename="5S_Dashboard_Template.xlsx",
            type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            base64=True
        )
    return no_update

# Main layout callback
@app.callback(
    Output("app-container", "children"),
    [Input('device-store', 'data'),
     Input('data-store', 'data'),
     Input('week-cols-store', 'data'),
     Input('selected-sites', 'data'),
     Input('selected-gauges', 'data'),
     Input('current-month', 'data')]
)
def display_layout(device_type, data_dict, week_cols_data, selected_sites, selected_gauges, current_month):
    # Convert stored data back to DataFrame
    df_current = pd.DataFrame.from_dict(data_dict, orient='index')
    
    # Get available months for dropdown
    available_months = data_manager.get_available_months()
    
    if device_type == 'mobile':
        return layout_mobile(df_current, week_cols_data, selected_sites, selected_gauges, current_month, available_months)
    else:
        return layout_pc(df_current, week_cols_data, selected_sites, selected_gauges, current_month, available_months)

# 添加到 main.py 的回调函数部分



# Run the app
if __name__ == '__main__':
    # For Render deployment
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)
