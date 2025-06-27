# main.py - Historical Data Logic Implementation

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

# Initialize GitHub data manager
data_manager = GitHubDataManager()

# Get last month (default month)
def get_last_month():
    """Get last month's year-month string"""
    today = datetime.now()
    if today.month == 1:
        last_month = datetime(today.year - 1, 12, 1)
    else:
        last_month = datetime(today.year, today.month - 1, 1)
    return last_month.strftime("%Y-%m")

default_month = get_last_month()  # This is the default month (2025-05)

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
    dcc.Store(id='data-store', data={}),
    dcc.Store(id='week-cols-store', data=['Week 1', 'Week 2', 'Week 3', 'Week 4']),
    dcc.Store(id='sidebar-open', data=False),
    dcc.Store(id='selected-sites', data=['HK_avg', 'SC_avg']),
    dcc.Store(id='selected-gauges', data=['HK_avg', 'SC_avg']),
    dcc.Store(id='current-viewing-month', data=default_month),  # Current viewing month
    dcc.Store(id='is-user-selected', data=False),  # Track if user has made a selection
    html.Div(id="app-container")
])

# === CORE LOGIC: Historical Data Management ===

# 1. Handle month selector changes
@app.callback(
    [Output('current-viewing-month', 'data'),
     Output('is-user-selected', 'data')],
    Input('month-selector', 'value'),
    State('current-viewing-month', 'data'),
    prevent_initial_call=True
)
def handle_month_selection(selected_month, current_month):
    """Handle user month selection in the sidebar"""
    if selected_month and selected_month != current_month:
        print(f"User selected month: {selected_month}")
        return selected_month, True  # Mark as user-selected
    return no_update, no_update

# 2. Load data based on current viewing month
@app.callback(
    Output('data-store', 'data'),
    [Input('current-viewing-month', 'data'),
     Input('device-store', 'data')],  # Initial load trigger
    prevent_initial_call=False
)
def load_data_for_viewing_month(viewing_month, device_type):
    """Load data for the currently selected viewing month"""
    if viewing_month:
        print(f"Loading data for viewing month: {viewing_month}")
        df_month = data_manager.load_data(viewing_month)
        if df_month is not None and not df_month.empty:
            print(f"Successfully loaded data: {len(df_month)} rows")
            return df_month.to_dict('index')
        else:
            print(f"No data found for: {viewing_month}")
    return {}

# 3. Reset to default month on page refresh (handled by initial layout values)
# The dcc.Store(id='current-viewing-month', data=default_month) handles this automatically

# === OTHER CALLBACKS (remain the same) ===

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
        target_month = upload_month if upload_month else default_month
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
        return ['HK_avg', 'SC_avg']  # Keep internal codes
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
        return ['HK_avg', 'SC_avg']  # Keep internal codes
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
        hk_sites = ['HK_avg', 'ELC', 'GGW', 'HSK', 'LFS', 'MAP', 'CS1', 'ST1']  # Updated
        return hk_sites, hk_sites

    elif trigger_id == 'select-sc-sites':
        sc_sites = ['SC_avg', 'GZ1', 'YT1', 'CD1', 'SZ2']  # Updated
        return sc_sites, sc_sites

    elif trigger_id == 'select-all-sites':
        all_sites = [
            'HK_avg', 'SC_avg', 'ELC', 'GGW', 'HSK', 'LFS', 'MAP', 'CS1', 'ST1',  # Updated
            'GZ1', 'YT1', 'CD1', 'SZ2'  # Updated
        ]
        return all_sites, all_sites
    
    return no_update, no_update

# Template download callback
# Updated template download callback in main.py
@app.callback(
    Output('download-template-file', 'data'),
    Input('download-template', 'n_clicks'),
    prevent_initial_call=True
)
def download_template(n_clicks):
    if n_clicks and n_clicks > 0:
        # Complete list of all warehouse sites
        all_sites = [
            'HK_avg',   # Hong Kong Average
            'SC_avg',   # South China Average
            # Hong Kong Sites
            'ELC',
            'GGW', 
            'HSK',
            'LFS',
            'MAP',
            'CS1',
            'ST1',
            # South China Sites
            'GZ1',
            'YT1', 
            'CD1',
            'SZ2'
        ]
        
        template_data = {
            'Site': all_sites,
            'Monthly Performance': [''] * len(all_sites),
            'Max/Month': [''] * len(all_sites),
            'Completed': [''] * len(all_sites),
            'Missing': [''] * len(all_sites),
            'Week 1': [''] * len(all_sites),
            'Week 2': [''] * len(all_sites),
            'Week 3': [''] * len(all_sites),
            'Week 4': [''] * len(all_sites)
        }
        template_df = pd.DataFrame(template_data)
        
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


# Main layout callback - Updated to use current-viewing-month
@app.callback(
    Output("app-container", "children"),
    [Input('device-store', 'data'),
     Input('data-store', 'data'),
     Input('week-cols-store', 'data'),
     Input('selected-sites', 'data'),
     Input('selected-gauges', 'data'),
     Input('current-viewing-month', 'data')]  # Use viewing month instead
)
def display_layout(device_type, data_dict, week_cols_data, selected_sites, selected_gauges, viewing_month):
    # Convert stored data back to DataFrame
    df_current = pd.DataFrame.from_dict(data_dict, orient='index')
    
    # Get available months for dropdown
    available_months = data_manager.get_available_months()
    
    if device_type == 'mobile':
        return layout_mobile(df_current, week_cols_data, selected_sites, selected_gauges, viewing_month, available_months)
    else:
        return layout_pc(df_current, week_cols_data, selected_sites, selected_gauges, viewing_month, available_months)

# Run the app
if __name__ == '__main__':
    print("=== 5S Dashboard Starting ===")
    print(f"Default month (last month): {default_month}")
    data_manager.debug_connection()
    
    print(f"\nTesting default month data load: {default_month}")
    test_data = data_manager.load_data(default_month)
    if test_data is not None and not test_data.empty:
        print(f"✅ Default data loaded successfully: {len(test_data)} rows")
        print(f"Sites list: {list(test_data.index)}")
    else:
        print("❌ Default data load failed")
        available_months = data_manager.get_available_months()
        print(f"Available months: {available_months}")
    
    print("=== Debug Complete ===\n")
    
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)
