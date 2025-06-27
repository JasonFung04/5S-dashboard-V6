# components.py - Part 1 (Lines 1-700)
# UI Components Definition

from dash import dcc, html, dash_table
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

def get_display_name(site_code):
    """Convert internal site codes to user-friendly display names"""
    display_names = {
        'HK_avg': 'Hong Kong Average',
        'SC_avg': 'South China Average',
        # Keep other sites as-is for now, can be extended later
        'MTL': 'CS1',  # if you still have old data
        'STLC': 'ST1',  # if you still have old data
        'GuangZhou': 'GZ1',  # if you still have old data
        'Yantian (ZhongTong)': 'YT1',  # if you still have old data
        'Chengdu': 'CD1',  # if you still have old data
        'Pinghu': 'SZ2'  # if you still have old data
    }
    return display_names.get(site_code, site_code)

# Improved color scheme with clear distinction between HK and SC sites
# 改进的颜色方案 - 更清晰的色彩区分



color_map = {
    # Hong Kong sites - 冷色调光谱，更易区分
    'ELC': '#1E40AF',           # 深蓝
    'GGW': '#0891B2',           # 青蓝
    'HSK': '#059669',           # 绿色
    'LFS': '#DC2626',           # 红色
    'MAP': '#7C3AED',           # 紫色
    'CS1': '#EA580C',           # 橙色 (was MTL)
    'ST1': '#BE185D',           # 玫红 (was STLC)
    'HK_avg': '#DC2626',        # 红色 - 保持不变
    
    # South China sites - 暖色调光谱，形成对比  
    'GZ1': '#F59E0B',           # 琥珀色 (was GuangZhou)
    'YT1': '#8B5CF6',           # 靛蓝 (was Yantian (ZhongTong))
    'CD1': '#10B981',           # 翠绿 (was Chengdu)
    'SZ2': '#F97316',           # 橙红 (was Pinghu)
    'SC_avg': '#7C3AED',        # 紫色 - 保持不变
}

# Line styles mapping for better line chart distinction
line_styles = {
    'ELC': 'solid',
    'GGW': 'solid',
    'HSK': 'solid',
    'LFS': 'solid',
    'MAP': 'solid',
    'MTL': 'solid',
    'STLC': 'solid',
    'HK_avg': 'solid',          # Average uses solid line
    'GuangZhou': 'solid',
    'Yantian (ZhongTong)': 'solid',
    'Chengdu': 'solid',
    'Pinghu': 'solid',
    'SC_avg': 'solid',          # Average uses solid line
}


def make_line_chart_with_data(df_data, week_cols, selected_sites, font_size=16, height=400):
    """Create line chart with selected sites, using improved color scheme"""
    traces = []
    x_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    if df_data.empty:
        # 创建一个空图表
        fig = go.Figure()
        fig.update_layout(
            title="No data available. Please upload data first.",
            xaxis_title='Week',
            yaxis_title='Score (%)',
            yaxis=dict(range=[75, 105]),
            plot_bgcolor='#FAFAFA',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=font_size, color='#374151'),
        )
        return dcc.Graph(
            figure=fig,
            style={"height": f"{height}px", "width": "100%", "margin": "0 auto"},
            config={"responsive": True, "displayModeBar": False}
        )

    
    # Only show selected sites
    for site in selected_sites:
        if site in df_data.index:
            yvals, marker_colors, marker_sizes = [], [], []
            for i, wk in enumerate(week_cols):
                s = df_data.loc[site, wk]
                if pd.isnull(s):
                    yvals.append(None)
                    marker_colors.append('#D1D5DB')
                    marker_sizes.append(6)
                elif s >= 90:
                    yvals.append(s)
                    marker_colors.append(color_map.get(site, "#6B7280"))
                    marker_sizes.append(10)  # Larger markers for high scores
                elif s >= 80:
                    yvals.append(s)
                    marker_colors.append(color_map.get(site, "#6B7280"))
                    marker_sizes.append(8)
                else:
                    yvals.append(s)
                    marker_colors.append('#9CA3AF')
                    marker_sizes.append(6)
            
            # Special styling settings
            # 特殊样式设置
            if site in ['HK_avg', 'SC_avg']:
                line_style = dict(
                    color=color_map.get(site, "#DC2626"), 
                    width=3,  # 减细线条宽度
                    dash='solid'  # 全部实线
                )
                marker_symbol = 'diamond'  # 改为菱形更突出
                marker_line_width = 2
                opacity = 1.0
            else:
                line_style = dict(
                    color=color_map.get(site, "#6B7280"), 
                    width=2.5,  # 更细的线条
                    dash='solid'  # 全部实线
                )
                marker_symbol = 'circle'
                marker_line_width = 1.5
                opacity = 0.9
            
                    
            traces.append(go.Scatter(
                x=x_labels,
                y=yvals,
                mode='lines+markers',
                name=get_display_name(site),  # CHANGED: was just 'site'
                line=line_style,
                marker=dict(
                    color=marker_colors, 
                    size=marker_sizes, 
                    line=dict(width=marker_line_width, color='white'),
                    symbol=marker_symbol
                ),
                opacity=opacity,
                connectgaps=True,

                hovertemplate=format_hover_template(site),
            ))
    
    fig = go.Figure(traces)
    fig.update_layout(
        xaxis_title='Week',
        yaxis_title='Score (%)',
        yaxis=dict(
            range=[75, 105], 
            dtick=5, 
            tickfont={'size': font_size, 'family': 'Arial, sans-serif', 'color': '#374151'},
            gridcolor='#E5E7EB',
            gridwidth=1,
            showgrid=True
        ),
        xaxis=dict(
            tickfont={'size': font_size, 'family': 'Arial, sans-serif', 'color': '#374151'}, 
            tickmode="array", 
            tickvals=x_labels,
            gridcolor='#E5E7EB',
            gridwidth=1,
            showgrid=True
        ),
        legend=dict(
            font=dict(size=font_size-1, family='Arial, sans-serif'), 
            orientation='h',
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            bgcolor='rgba(255,255,255,0.95)', 
            bordercolor="#D1D5DB", 
            borderwidth=1
        ),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='white',
        autosize=True,
        margin=dict(l=60, r=40, t=80, b=60),
        font=dict(family="Arial, sans-serif", size=font_size, color='#374151'),
        title=dict(
            text="",
            x=0.5,
            font=dict(size=font_size+4, family='Arial, sans-serif', color='#1F2937')
        )
    )
    
    # Add target line with clear styling
    fig.add_hline(
        y=90, 
        line_dash="dash", 
        line_color="#16A34A",  # Green color
        line_width=3,
        annotation_text="Target Line (90%)", 
        annotation_position="bottom right",
        annotation=dict(
            font=dict(size=font_size-1, color="#16A34A", family="Arial, sans-serif")
        )
    )
    
    return dcc.Graph(
        figure=fig,
        style={"height": f"{height}px", "width": "100%", "margin": "0 auto"},
        config={"responsive": True, "displayModeBar": False}
    )

def make_gauge(siteinfo, width=180, font_small=12):
    """Create gauge component"""

    # Add this mapping at the beginning
    display_names = {
        'HK_avg': 'Hong Kong Average',
        'SC_avg': 'South China Average'
    }


    # 检查是否有数据
    if not siteinfo or 'Monthly Performance' not in siteinfo:

        value = siteinfo['Monthly Performance']
        original_site_name = siteinfo['Site']
        site_name = get_display_name(original_site_name)  # CHANGED: Use display name

        return html.Div([
            html.Div("No Data", style={
                'textAlign': 'center',
                'color': '#6B7280',
                'fontSize': f'{font_small+3}px',
                'fontFamily': 'Arial, sans-serif',
                'padding': '50px 20px'
            })
        ], style={
            'width': f'{width}px',
            'minHeight': '280px',
            'display': 'inline-block',
            'background': 'white',
            'borderRadius': '12px',
            'border': '2px solid #E5E7EB',
            'margin': '8px',
            'padding': '16px',
            'textAlign': 'center',
            'justifyContent': 'center',
            'alignItems': 'center'
        })



    value = siteinfo['Monthly Performance']
    site_name = display_names.get(siteinfo['Site'], siteinfo['Site'])
    
    # Determine color based on score
    if value >= 90:
        color = '#16A34A'  # Green - Excellent
        status = 'Excellent'
    elif value >= 40:
        color = '#EA580C'  # Orange - Fair
        status = 'Fair'
    else:
        color = '#DC2626'  # Red - Critical
        status = 'Critical'
    
    # Special styling for average sites
    if site_name in ['HK_avg', 'SC_avg']:
        border_color = color_map.get(site_name, '#DC2626')
        box_shadow = f'0 4px 12px rgba({",".join(str(int(border_color[i:i+2], 16)) for i in (1, 3, 5))}, 0.3)'
        site_color = color_map.get(site_name, '#DC2626')
    else:
        border_color = '#E5E7EB'
        box_shadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        site_color = '#1F2937'
    
    return html.Div([
        # Site Name
        html.Div(site_name, style={
            'color': site_color, 
            'fontWeight': 'bold', 
            'fontSize': f'{font_small+3}px',
            'textAlign': 'center', 
            'marginBottom': '15px',
            'fontFamily': 'Arial, sans-serif'
        }),
        
        # Gauge Chart
        dcc.Graph(
            figure=go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={
                        'suffix': "%", 
                        'font': {
                            'size': int(font_small*2.2), 
                            'color': color,
                            'family': 'Arial, sans-serif',
                        }
                    },
                    gauge={
                        'shape': "angular",
                        'axis': {
                            'range': [0, 100],
                            'tickwidth': 2,
                            'tickcolor': '#374151',
                            'tickmode': 'array',
                            'tickvals': [0, 20, 40, 60, 80, 100],
                            'ticktext': ['0', '20%', '40%', '60%', '80%', '100%'],
                            'tickfont': {'size': font_small-1, 'family': 'Arial, sans-serif', 'color': '#1F2937'},
                            'tickcolor': '#1F2937',
                        },
                        'bgcolor': '#F9FAFB',
                        'bar': {'color': color, 'thickness': 0.15},
                        'steps': [
                            {'range': [0, 40], 'color': '#FEE2E2'},    # Red zone
                            {'range': [40, 90], 'color': '#FEF3C7'},   # Yellow zone
                            {'range': [90, 100], 'color': '#D1FAE5'},  # Green zone
                        ],
                        'threshold': {
                            'line': {'color': '#1F2937', 'width': 3},
                            'thickness': 0.75,
                            'value': value
                        },
                        'borderwidth': 2,
                        'bordercolor': border_color,
                    },
                )
            ).update_layout(
                margin=dict(t=10, b=10, l=15, r=15),
                height=160,
                paper_bgcolor='white',
                font={'family': 'Arial, sans-serif', 'color': '#374151'},
            ),
            config={'displayModeBar': False},
            style={'height': '160px', 'width': '100%'}
        ),
        
        # Status Label
        html.Div(status, style={
            'backgroundColor': color,
            'color': 'white',
            'padding': '6px 12px',
            'borderRadius': '12px',
            'fontSize': f'{font_small}px',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'margin': '10px auto 15px auto',
            'display': 'inline-block',
            'fontFamily': 'Arial, sans-serif'
        }),
        
        # Detailed Information
        html.Div([
            html.Div([
                html.Span("Target: ", style={'fontWeight': 'bold', 'color': '#6B7280'}),
                html.Span(str(siteinfo['Max/Month']), style={'color': '#1F2937'})
            ], style={'marginBottom': '4px'}),
            html.Div([
                html.Span("Completed: ", style={'fontWeight': 'bold', 'color': '#16A34A'}),
                html.Span(str(siteinfo['Completed']), style={'color': '#1F2937'}),
                html.Span(" | ", style={'color': '#D1D5DB', 'margin': '0 8px'}),
                html.Span("Missing: ", style={'fontWeight': 'bold', 'color': '#DC2626'}),
                html.Span(str(siteinfo['Missing']), style={'color': '#1F2937'})
            ])
        ], style={
            'fontSize': f'{font_small}px', 
            'textAlign': 'center',
            'fontFamily': 'Arial, sans-serif',
            'lineHeight': '1.6'
        })
    ], style={
        'width': f'{width}px',
        'minHeight': '280px',
        'display': 'inline-block',
        'background': 'white',
        'borderRadius': '12px',
        'border': f'2px solid {border_color}',
        'boxShadow': box_shadow,
        'margin': '8px',
        'padding': '16px',
        'transition': 'transform 0.2s, box-shadow 0.2s'
    })

def make_sidebar():
    """Create sidebar component with dynamic month selection"""
    from github_storage_manager import GitHubDataManager
    data_manager = GitHubDataManager()
    
    # Get month options
    month_options = data_manager.generate_month_options()
    
    def get_last_month():
        """Get last month's year-month string"""
        today = datetime.now()
        if today.month == 1:
            last_month = datetime(today.year - 1, 12, 1)
        else:
            last_month = datetime(today.year, today.month - 1, 1)
        return last_month.strftime("%Y-%m")

    default_month = get_last_month()  # Default to last month
    
    # Updated site options list

    all_site_options = [
        {'label': 'Hong Kong Average', 'value': 'HK_avg'},
        {'label': 'South China Average', 'value': 'SC_avg'},
        {'label': '--- Hong Kong Sites ---', 'value': '', 'disabled': True},
        {'label': 'ELC', 'value': 'ELC'},
        {'label': 'GGW', 'value': 'GGW'},
        {'label': 'HSK', 'value': 'HSK'},
        {'label': 'LFS', 'value': 'LFS'},
        {'label': 'MAP', 'value': 'MAP'},
        {'label': 'CS1', 'value': 'CS1'},  # was MTL
        {'label': 'ST1', 'value': 'ST1'},  # was STLC
        {'label': '--- South China Sites ---', 'value': '', 'disabled': True},
        {'label': 'GZ1', 'value': 'GZ1'},  # was GuangZhou
        {'label': 'YT1', 'value': 'YT1'},  # was Yantian (ZhongTong)
        {'label': 'CD1', 'value': 'CD1'},  # was Chengdu
        {'label': 'SZ2', 'value': 'SZ2'}   # was Pinghu
    ]
    
    return html.Div([
        # Sidebar Content
        html.Div([
            # Close Button
            html.Div([
                html.Button('×', id='close-sidebar',
                           style={
                               'backgroundColor': 'transparent',
                               'border': 'none',
                               'fontSize': '24px',
                               'color': '#6B7280',
                               'cursor': 'pointer',
                               'float': 'right',
                               'padding': '0',
                               'width': '30px',
                               'height': '30px'
                           })
            ], style={'marginBottom': '20px'}),
            
            # Title
            html.H3("Data Manager", style={
                'color': '#1F2937',
                'fontSize': '1.5rem',
                'marginBottom': '20px',
                'fontFamily': 'Arial, sans-serif'
            }),
            
            # GitHub Status Indicator
            html.Div([
                html.Div([
                    html.I(className='fas fa-cloud', style={
                        'fontSize': '16px',
                        'marginRight': '8px',
                        'color': '#16A34A' if data_manager.github_token else '#DC2626'
                    }),
                    html.Span(
                        "GitHub Cloud Storage Enabled" if data_manager.github_token else "GitHub Cloud Storage Not Configured",
                        style={
                            'fontSize': '14px',
                            'color': '#16A34A' if data_manager.github_token else '#DC2626',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'marginBottom': '15px'}),
                html.P(
                    f"Data Repository: {data_manager.repo_owner}/{data_manager.repo_name}" if data_manager.github_token 
                    else "Local Storage Mode (Data will be lost after restart)",
                    style={
                        'fontSize': '12px',
                        'color': '#6B7280',
                        'fontStyle': 'italic',
                        'margin': '0'
                    }
                )
            ], style={
                'backgroundColor': '#F9FAFB',
                'border': f'1px solid {"#D1FAE5" if data_manager.github_token else "#FEE2E2"}',
                'borderRadius': '6px',
                'padding': '12px',
                'marginBottom': '20px'
            }),
            
            # Month Selection Section - Updated with better description
            html.Div([
                html.H4("View Historical Data", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.P("Select a month to view historical 5S performance data", style={
                    'fontSize': '13px',
                    'color': '#6B7280',
                    'margin': '0 0 10px 0',
                    'fontFamily': 'Arial, sans-serif'
                }),
                dcc.Dropdown(
                    id='month-selector',
                    options=month_options,
                    value=default_month,  # Set default value
                    placeholder="Select Year-Month",
                    style={'marginBottom': '10px'},
                    clearable=False  # Prevent clearing the selection
                ),
                html.Div([
                    html.I(className='fas fa-info-circle', style={
                        'fontSize': '12px',
                        'marginRight': '5px',
                        'color': '#6B7280'
                    }),
                    html.Span(f"Default: {default_month} (Last Month)", style={
                        'fontSize': '12px',
                        'color': '#6B7280',
                        'fontStyle': 'italic'
                    })
                ], style={'marginBottom': '10px'}),
                html.Div([
                    html.I(className='fas fa-refresh', style={
                        'fontSize': '12px',
                        'marginRight': '5px',
                        'color': '#059669'
                    }),
                    html.Span("Refresh page to return to default month", style={
                        'fontSize': '12px',
                        'color': '#059669',
                        'fontStyle': 'italic'
                    })
                ])
            ], style={'marginBottom': '30px'}),

            # components.py - Part 2 (Lines 701-1400)

            # Site Selection Section for Line Chart
            html.Div([
                html.H4("Line Chart Site Selection", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                dcc.Dropdown(
                    id='site-selector',
                    options=all_site_options,
                    value=['HK_avg', 'SC_avg'],
                    multi=True,
                    placeholder="Select sites to display",
                    style={'marginBottom': '15px'}
                ),
                html.P("Note: HK_avg and SC_avg will always be displayed", style={
                    'fontSize': '12px',
                    'color': '#6B7280',
                    'fontStyle': 'italic'
                })
            ], style={'marginBottom': '30px'}),
            
            # Gauge Selection Section
            html.Div([
                html.H4("Gauge Display Selection", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                dcc.Dropdown(
                    id='gauge-selector',
                    options=all_site_options,
                    value=['HK_avg', 'SC_avg'],
                    multi=True,
                    placeholder="Select gauges to display",
                    style={'marginBottom': '15px'}
                ),
                html.P("Default display: HK_avg and SC_avg", style={
                    'fontSize': '12px',
                    'color': '#6B7280',
                    'fontStyle': 'italic'
                })
            ], style={'marginBottom': '30px'}),
            
            # Quick Selection Buttons
            html.Div([
                html.H4("Quick Selection", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.Div([
                    html.Button('Hong Kong Sites', id='select-hk-sites',
                               style={
                                   'backgroundColor': '#DC2626',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '8px 12px',
                                   'borderRadius': '4px',
                                   'fontSize': '12px',
                                   'cursor': 'pointer',
                                   'margin': '2px',
                                   'fontFamily': 'Arial, sans-serif'
                               }),
                    html.Button('South China Sites', id='select-sc-sites',
                               style={
                                   'backgroundColor': '#7C3AED',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '8px 12px',
                                   'borderRadius': '4px',
                                   'fontSize': '12px',
                                   'cursor': 'pointer',
                                   'margin': '2px',
                                   'fontFamily': 'Arial, sans-serif'
                               }),
                    html.Button('All Sites', id='select-all-sites',
                               style={
                                   'backgroundColor': '#059669',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '8px 12px',
                                   'borderRadius': '4px',
                                   'fontSize': '12px',
                                   'cursor': 'pointer',
                                   'margin': '2px',
                                   'fontFamily': 'Arial, sans-serif'
                               })
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '4px'})
            ], style={'marginBottom': '30px'}),
            
            # Upload Section
            html.Div([
                html.H4("Upload New Data", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                
                # Upload month selector
                html.Div([
                    html.Label("Select Upload Month:", style={
                        'fontSize': '14px',
                        'color': '#374151',
                        'fontWeight': 'bold',
                        'marginBottom': '5px',
                        'display': 'block'
                    }),
                    dcc.Dropdown(
                        id='upload-month-selector',
                        options=month_options,
                        value=default_month,
                        placeholder="Select Year-Month",
                        style={'marginBottom': '15px'}
                    ),
                ], style={'marginBottom': '15px'}),
                
                # Upload Area
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.I(className='fas fa-cloud-upload-alt', style={
                            'fontSize': '2rem',
                            'color': '#0369A1',
                            'marginBottom': '8px'
                        }),
                        html.P('Drag and drop or click to select Excel file', style={
                            'margin': '0',
                            'fontSize': '14px',
                            'color': '#6B7280',
                            'textAlign': 'center'
                        }),
                        html.P('Supported formats: .xlsx, .xls', style={
                            'margin': '4px 0 0 0',
                            'fontSize': '12px',
                            'color': '#9CA3AF',
                            'textAlign': 'center'
                        })
                    ]),
                    style={
                        'width': '100%',
                        'height': '120px',
                        'lineHeight': '120px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderColor': '#D1D5DB',
                        'borderRadius': '8px',
                        'textAlign': 'center',
                        'backgroundColor': '#F9FAFB',
                        'cursor': 'pointer',
                        'transition': 'all 0.3s ease',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    },
                    multiple=False
                ),
                
                # Upload Status
                html.Div(id='upload-status', style={
                    'marginTop': '15px',
                    'fontSize': '14px'
                }),
            ], style={'marginBottom': '30px'}),
            
            # Download Template Button
            html.Button('Download Template File', 
                       id='download-template',
                       style={
                           'backgroundColor': '#0369A1',
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 16px',
                           'borderRadius': '6px',
                           'fontSize': '14px',
                           'cursor': 'pointer',
                           'width': '100%',
                           'fontFamily': 'Arial, sans-serif',
                           'marginBottom': '15px'
                       }),
            dcc.Download(id='download-template-file'),
            
            # Instructions
            html.Div([
                html.H4("Required Columns:", style={
                    'fontSize': '16px',
                    'color': '#1F2937',
                    'marginTop': '20px',
                    'marginBottom': '10px'
                }),
                html.Ul([
                    html.Li("Site"),
                    html.Li("Monthly Performance"),
                    html.Li("Max/Month"),
                    html.Li("Completed"),
                    html.Li("Missing"),
                    html.Li("Week 1"),
                    html.Li("Week 2"),
                    html.Li("Week 3"),
                    html.Li("Week 4")
                ], style={
                    'fontSize': '12px',
                    'color': '#6B7280',
                    'paddingLeft': '20px'
                }),

            ])
        ], style={
            'padding': '20px',
            'height': '100%',
            'overflowY': 'auto'
        })
    ], id='sidebar',
       style={
           'position': 'fixed',
           'top': '0',
           'right': '-400px',  # Initially hidden
           'width': '400px',
           'height': '100vh',
           'backgroundColor': 'white',
           'boxShadow': '-2px 0 5px rgba(0,0,0,0.1)',
           'transition': 'right 0.3s ease',
           'zIndex': '1000',
           'fontFamily': 'Arial, sans-serif'
       })

def make_sidebar_toggle_pc():
    """PC version sidebar toggle button"""
    return html.Button([
        html.I(className='fas fa-cog', style={'marginRight': '8px'}),
        'Data Manager'
    ], id='open-sidebar',
       style={
           'position': 'fixed',
           'top': '20px',
           'right': '20px',
           'backgroundColor': '#0369A1',
           'color': 'white',
           'border': 'none',
           'padding': '12px 20px',
           'borderRadius': '8px',
           'fontSize': '14px',
           'cursor': 'pointer',
           'zIndex': '999',
           'fontFamily': 'Arial, sans-serif',
           'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
       })

def make_sidebar_toggle_mobile():
    """Mobile version sidebar toggle button"""
    return html.Button([
        html.I(className='fas fa-cog')
    ], id='open-sidebar-mobile',
       style={
           'position': 'fixed',
           'top': '15px',
           'right': '15px',
           'backgroundColor': '#0369A1',
           'color': 'white',
           'border': 'none',
           'padding': '10px',
           'borderRadius': '50%',
           'fontSize': '16px',
           'cursor': 'pointer',
           'zIndex': '999',
           'width': '45px',
           'height': '45px',
           'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
       })

def prepare_dashboard_data(df_data, selected_gauges):
    """Prepare dashboard data for selected gauges only"""
    # Check if data is empty
    if df_data.empty:
        return []
    
    # Only show selected gauges
    data = []
    for k in df_data.index:
        if k in selected_gauges:
            site_data = {
                'Site': k,
                'Max/Month': df_data.loc[k]["Max/Month"],
                'Completed': int(df_data.loc[k]["Completed"]) if pd.notna(df_data.loc[k]["Completed"]) else 0,
                'Missing': df_data.loc[k]["Missing"] if pd.notna(df_data.loc[k]["Missing"]) else 0,
                'Monthly Performance': df_data.loc[k]["Monthly Performance"] if pd.notna(df_data.loc[k]["Monthly Performance"]) else 0
            }
            data.append(site_data)
    
    return data

def prepare_ranking_data(df_data, selected_sites):
    """Prepare ranking data for selected sites only"""
    # Check if data is empty
    if df_data.empty:
        return pd.DataFrame(columns=['Rank', 'Site', 'Score'])
    
    # Filter data to only include selected sites
    filtered_df = df_data.loc[df_data.index.intersection(selected_sites)]
    
    if filtered_df.empty:
        return pd.DataFrame(columns=['Rank', 'Site', 'Score'])
    
    # Sort data by Monthly Performance for ranking
    df_sorted = filtered_df.sort_values(by="Monthly Performance", ascending=False)


    rank_data = pd.DataFrame({
        'Rank': range(1, len(df_sorted) + 1),
        'Site': [get_display_name(site) for site in df_sorted.index],  # CHANGED
        'Score': df_sorted['Monthly Performance'].round(2)
    })
    
    return rank_data

def prepare_missing_data(df_data, selected_sites):
    """Prepare missing clock data for selected sites only"""
    # Check if data is empty
    if df_data.empty:
        return pd.DataFrame(columns=['Rank', 'Site', 'Missing'])
    
    # Filter data to only include selected sites
    filtered_df = df_data.loc[df_data.index.intersection(selected_sites)]
    
    if filtered_df.empty:
        return pd.DataFrame(columns=['Rank', 'Site', 'Missing'])
    

    sorted_sites = filtered_df.sort_values(by="Missing", ascending=True).index
    missing_clock_data = pd.DataFrame({
        'Rank': range(1, len(filtered_df) + 1),
        'Site': [get_display_name(site) for site in sorted_sites],  # CHANGED
        'Missing': filtered_df.sort_values(by="Missing", ascending=True)["Missing"].values
    })
    
    return missing_clock_data


# components.py - Part 3 (Lines 1401-2100)

def layout_pc(df_data, week_cols, selected_sites, selected_gauges, current_month, available_months):
    """PC version layout"""
    
    # Check if data is empty
    if df_data.empty:
        return html.Div([
            make_sidebar(),
            make_sidebar_toggle_pc(),
            html.Div([
                make_sidebar_toggle_mobile()
            ], style={'display': 'none'}),
            html.Div([
                html.Div([
                    html.H1("5S Score Dashboard", style={
                        'textAlign': 'center',
                        'color': 'white',
                        'marginTop': '0',
                        'marginBottom': '8px',
                        'fontSize': '2.5rem',
                        'fontFamily': 'Arial, sans-serif',
                        'fontWeight': 'bold'
                    }),
                    html.P(f"No data available for {current_month}. Please upload data first.", style={
                        'textAlign': 'center',
                        'color': 'white',
                        'fontSize': '1.1rem',
                        'margin': '0 0 32px 0',
                        'fontFamily': 'Arial, sans-serif'
                    })
                ], style={
                    'background': 'linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)',
                    'color': 'white',
                    'padding': '32px 20px',
                    'marginBottom': '32px'
                }),
                html.Div([
                    html.H2("Please upload data using the Data Manager", style={
                        'textAlign': 'center',
                        'color': '#1F2937',
                        'fontSize': '1.8rem',
                        'marginBottom': '24px',
                        'fontFamily': 'Arial, sans-serif'
                    }),
                ], style={'textAlign': 'center', 'padding': '50px'})
            ])
        ], style={
            'background': '#F9FAFB',
            'minHeight': '100vh',
            'fontFamily': 'Arial, sans-serif'
        })
    
    # If data exists, continue normal rendering
    data = prepare_dashboard_data(df_data, selected_gauges)
    rank_data = prepare_ranking_data(df_data, selected_sites)
    missing_clock_data = prepare_missing_data(df_data, selected_sites)
    
    return html.Div([
        # Sidebar
        make_sidebar(),
        
        # Sidebar Toggle Button (PC version visible, mobile hidden)
        make_sidebar_toggle_pc(),
        
        # Mobile button (hidden on PC)
        html.Div([
            make_sidebar_toggle_mobile()
        ], style={'display': 'none'}),
        
        # Main Content
        html.Div([
            # Header
            html.Div([
                html.H1("5S Score Dashboard", style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginTop': '0',
                    'marginBottom': '8px',
                    'fontSize': '2.5rem',
                    'fontFamily': 'Arial, sans-serif',
                    'fontWeight': 'bold'
                }),
                html.P(f"Workplace Organization Performance Monitoring - {current_month}", style={
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': '1.1rem',
                    'margin': '0 0 32px 0',
                    'fontFamily': 'Arial, sans-serif'
                })
            ], style={
                'background': 'linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)',
                'color': 'white',
                'padding': '32px 20px',
                'marginBottom': '32px'
            }),
            
            # Trend Chart Area
            html.Div([
                html.Div([
                    html.H3("Weekly Trend Line Chart", style={
                        'margin': '0 0 20px 0',
                        'color': '#1F2937',
                        'fontSize': '1.4rem',
                        'fontFamily': 'Arial, sans-serif'
                    }),
                    html.P("Default shows Hong Kong Average and South China Average. You can add more sites in the data manager", style={
                        'margin': '0 0 15px 0',
                        'color': '#6B7280',
                        'fontSize': '0.9rem',
                        'fontStyle': 'italic'
                    })
                ], style={'textAlign': 'center'}),
                make_line_chart_with_data(df_data, week_cols, selected_sites, font_size=14, height=400)
            ], style={
                'width': '95%',
                'maxWidth': '1000px',
                'margin': '0 auto 40px auto',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'padding': '20px'
            }),
            
            # Gauge Chart Area
            html.Div([
                html.H2("5S Site Performance", style={
                    'textAlign': 'center',
                    'color': '#1F2937',
                    'fontSize': '1.8rem',
                    'marginBottom': '24px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.Div([make_gauge(d, width=200, font_small=12) for d in data],
                         style={
                             'display': 'flex',
                             'flexWrap': 'wrap',
                             'justifyContent': 'center',
                             'alignItems': 'flex-start',
                             'gap': '16px',
                             'padding': '0 20px'
                         })
            ], style={'marginBottom': '40px'}),
            
            # Ranking Table Area
            html.Div([
                html.H2("Performance Ranking (Selected Sites)", style={
                    'textAlign': 'center',
                    'color': '#1F2937',
                    'fontSize': '1.8rem',
                    'marginBottom': '24px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                dash_table.DataTable(
                    data=rank_data.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in rank_data.columns],
                    style_table={
                        'overflowY': 'auto',
                        'width': '100%',
                        'maxWidth': '600px',
                        'margin': 'auto',
                        'borderRadius': '8px',
                        'overflow': 'hidden'
                    },
                    style_cell={
                        'padding': '16px',
                        'textAlign': 'center',
                        'fontSize': '14px',
                        'fontFamily': 'Arial, sans-serif',
                        'border': 'none'
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': '#F3F4F6',
                        'color': '#1F2937',
                        'fontSize': '15px',
                        'border': 'none'
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#F9FAFB"
                        },
                        {
                            "if": {"filter_query": "{Rank} = 1"},
                            "backgroundColor": "#DCFCE7",
                            "color": "#16A34A",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {"filter_query": "{Site} = 'Hong Kong Average'"},
                            "backgroundColor": "#FEE2E2",
                            "color": "#DC2626",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {"filter_query": "{Site} = 'South China Average'"},
                            "backgroundColor": "#F3E8FF",
                            "color": "#7C3AED",
                            "fontWeight": "bold"
                        }
                    ]
                ),
            ], style={
                'width': '95%',
                'maxWidth': '600px',
                'margin': '0 auto',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'padding': '24px',
                'marginBottom': '40px'
            }),
            
            # Missing Clock Ranking Table
            html.Div([
                html.H2("Missing Clock Ranking (Selected Sites)", style={
                    'textAlign': 'center',
                    'color': '#1F2937',
                    'fontSize': '1.8rem',
                    'marginBottom': '24px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                dash_table.DataTable(
                    data=missing_clock_data.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in missing_clock_data.columns],
                    style_table={
                        'overflowY': 'auto',
                        'width': '100%',
                        'maxWidth': '600px',
                        'margin': 'auto',
                        'borderRadius': '8px',
                        'overflow': 'hidden'
                    },
                    style_cell={
                        'padding': '16px',
                        'textAlign': 'center',
                        'fontSize': '14px',
                        'fontFamily': 'Arial, sans-serif',
                        'border': 'none'
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': '#F3F4F6',
                        'color': '#1F2937',
                        'fontSize': '15px',
                        'border': 'none'
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#F9FAFB"
                        },
                        {
                            "if": {"filter_query": "{Rank} = 1"},
                            "backgroundColor": "#DCFCE7",
                            "color": "#16A34A",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {"filter_query": "{Site} = 'Hong Kong Average'"},
                            "backgroundColor": "#FEE2E2",
                            "color": "#DC2626",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {"filter_query": "{Site} = 'South China Average'"},
                            "backgroundColor": "#F3E8FF",
                            "color": "#7C3AED",
                            "fontWeight": "bold"
                        }
                    ]
                ),
            ], style={
                'width': '95%',
                'maxWidth': '600px',
                'margin': '0 auto',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'padding': '24px',
                'marginBottom': '40px'
            }),
        ], id='main-content')
    ], style={
        'background': '#F9FAFB',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })

# components.py - Part 4 (Lines 2101-end)

def layout_mobile(df_data, week_cols, selected_sites, selected_gauges, current_month, available_months):
    """Mobile version layout"""
    
    # Check if data is empty
    if df_data.empty:
        return html.Div([
            make_sidebar(),
            html.Div([
                make_sidebar_toggle_pc()
            ], style={'display': 'none'}),
            make_sidebar_toggle_mobile(),
            html.Div([
                html.H1("5S Score Dashboard", style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginTop': '0',
                    'marginBottom': '4px',
                    'fontSize': '6vw',
                    'fontFamily': 'Arial, sans-serif',
                    'fontWeight': 'bold'
                }),
                html.P(f"No data for {current_month}", style={
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': '3.5vw',
                    'margin': '0',
                    'fontFamily': 'Arial, sans-serif'
                })
            ], style={
                'background': 'linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)',
                'padding': '20px 15px',
                'marginBottom': '20px'
            }),
            html.Div([
                html.H2("Please upload data", style={
                    'textAlign': 'center',
                    'color': '#1F2937',
                    'fontSize': '4.5vw',
                    'marginBottom': '15px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.P("Use the settings button to upload your data.", style={
                    'textAlign': 'center',
                    'color': '#6B7280',
                    'fontSize': '3.5vw',
                    'fontFamily': 'Arial, sans-serif'
                })
            ], style={'textAlign': 'center', 'padding': '30px'})
        ], style={
            'background': '#F9FAFB',
            'minHeight': '100vh',
            'fontFamily': 'Arial, sans-serif'
        })

    # If data exists, continue normal rendering
    data = prepare_dashboard_data(df_data, selected_gauges)
    rank_data = prepare_ranking_data(df_data, selected_sites)
    missing_clock_data = prepare_missing_data(df_data, selected_sites)

    # Check if there are valid selections
    available_sites = df_data.index.tolist()
    valid_sites_for_chart = [site for site in selected_sites if site in available_sites]

    return html.Div([
        # Sidebar
        make_sidebar(),
        
        # PC button (hidden on mobile)
        html.Div([
            make_sidebar_toggle_pc()
        ], style={'display': 'none'}),
        
        # Sidebar Toggle Button (mobile version visible, PC hidden)
        make_sidebar_toggle_mobile(),
        
        # Header
        html.Div([
            html.H1("5S Score Dashboard", style={
                'textAlign': 'center',
                'color': 'white',
                'marginTop': '0',
                'marginBottom': '4px',
                'fontSize': '6vw',
                'fontFamily': 'Arial, sans-serif',
                'fontWeight': 'bold'
            }),
            html.P(f"Workplace Organization - {current_month}", style={
                'textAlign': 'center',
                'color': 'white',
                'fontSize': '3.5vw',
                'margin': '0',
                'fontFamily': 'Arial, sans-serif'
            })
        ], style={
            'background': 'linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)',
            'padding': '20px 15px',
            'marginBottom': '20px'
        }),
        
        # Trend Chart Area (Mobile)
        html.Div([
            html.Div([
                html.H3("Weekly Trend Chart", style={
                    'margin': '0 0 10px 0',
                    'color': '#1F2937',
                    'fontSize': '4.5vw',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.P(f"Showing {len(valid_sites_for_chart)} sites" if valid_sites_for_chart else "No sites selected", style={
                    'margin': '0 0 10px 0',
                    'color': '#6B7280',
                    'fontSize': '3vw',
                    'fontStyle': 'italic'
                })
            ], style={'textAlign': 'center'}),
            make_line_chart_with_data(df_data, week_cols, selected_sites, font_size=10, height=300)
        ], style={
            'margin': '0 10px 20px 10px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px'
        }),
        
        # Gauge Charts
        html.Div([
            html.H2("5S Site Performance", style={
                'textAlign': 'center',
                'color': '#1F2937',
                'fontSize': '4.5vw',
                'marginBottom': '15px',
                'fontFamily': 'Arial, sans-serif'
            }),
            html.Div([make_gauge(d, width=140, font_small=9) for d in data] if data else [
                html.P("No gauges to display", style={
                    'textAlign': 'center',
                    'color': '#6B7280',
                    'fontSize': '3.5vw',
                    'fontFamily': 'Arial, sans-serif',
                    'padding': '30px'
                })
            ],
                     style={
                         'display': 'flex',
                         'flexWrap': 'wrap',
                         'justifyContent': 'center',
                         'gap': '8px',
                         'padding': '0 5px'
                     })
        ], style={'marginBottom': '20px'}),
        
        # Ranking Table
        html.Div([
            html.H2("Performance Ranking", style={
                'textAlign': 'center',
                'color': '#1F2937',
                'fontSize': '4.5vw',
                'marginBottom': '15px',
                'fontFamily': 'Arial, sans-serif'
            }),
            dash_table.DataTable(
                data=rank_data.to_dict('records') if not rank_data.empty else [],
                columns=[{'name': col, 'id': col} for col in ['Rank', 'Site', 'Score']],
                style_table={
                    'overflowY': 'auto',
                    'width': '100%',
                    'borderRadius': '8px',
                    'overflow': 'hidden'
                },
                style_cell={
                    'padding': '12px 8px',
                    'textAlign': 'center',
                    'fontSize': '3.2vw',
                    'fontFamily': 'Arial, sans-serif',
                    'border': 'none',
                    'minWidth': '25vw'
                },
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': '#F3F4F6',
                    'color': '#1F2937',
                    'fontSize': '3.5vw',
                    'border': 'none'
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#F9FAFB"
                    },
                    {
                        "if": {"filter_query": "{Rank} = 1"},
                        "backgroundColor": "#DCFCE7",
                        "color": "#16A34A",
                        "fontWeight": "bold"
                    },
                    {
                        "if": {"filter_query": "{Site} = 'Hong Kong Average'"},
                        "backgroundColor": "#FEE2E2",
                        "color": "#DC2626",
                        "fontWeight": "bold"
                    },
                    {
                        "if": {"filter_query": "{Site} = 'South China Average'"},
                        "backgroundColor": "#F3E8FF",
                        "color": "#7C3AED",
                        "fontWeight": "bold"
                    }
                ]
            ) if not rank_data.empty else html.P("No ranking data available.", style={
                'textAlign': 'center',
                'color': '#6B7280',
                'fontSize': '3.5vw',
                'fontFamily': 'Arial, sans-serif',
                'padding': '30px'
            }),
        ], style={
            'margin': '0 10px 20px 10px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px'
        }),
        
        # Missing Clock Ranking Table (Mobile)
        html.Div([
            html.H2("Missing Clock Ranking", style={
                'textAlign': 'center',
                'color': '#1F2937',
                'fontSize': '4.5vw',
                'marginBottom': '15px',
                'fontFamily': 'Arial, sans-serif'
            }),
            dash_table.DataTable(
                data=missing_clock_data.to_dict('records') if not missing_clock_data.empty else [],
                columns=[{'name': col, 'id': col} for col in ['Rank', 'Site', 'Missing']],
                style_table={
                    'overflowY': 'auto',
                    'width': '100%',
                    'borderRadius': '8px',
                    'overflow': 'hidden'
                },
                style_cell={
                    'padding': '12px 8px',
                    'textAlign': 'center',
                    'fontSize': '3.2vw',
                    'fontFamily': 'Arial, sans-serif',
                    'border': 'none',
                    'minWidth': '25vw'
                },
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': '#F3F4F6',
                    'color': '#1F2937',
                    'fontSize': '3.5vw',
                    'border': 'none'
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#F9FAFB"
                    },
                    {
                        "if": {"filter_query": "{Rank} = 1"},
                        "backgroundColor": "#DCFCE7",
                        "color": "#16A34A",
                        "fontWeight": "bold"
                    },
                    {
                        "if": {"filter_query": "{Site} = 'Hong Kong Average'"},
                        "backgroundColor": "#FEE2E2",
                        "color": "#DC2626",
                        "fontWeight": "bold"
                    },
                    {
                        "if": {"filter_query": "{Site} = 'South China Average'"},
                        "backgroundColor": "#F3E8FF",
                        "color": "#7C3AED",
                        "fontWeight": "bold"
                    }
                ]
            ) if not missing_clock_data.empty else html.P("No missing clock data available.", style={
                'textAlign': 'center',
                'color': '#6B7280',
                'fontSize': '3.5vw',
                'fontFamily': 'Arial, sans-serif',
                'padding': '30px'
            }),
        ], style={
            'margin': '0 10px 30px 10px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px'
        }),
    ], style={
        'background': '#F9FAFB',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })

def format_hover_template(site_code):
    """Format hover template with display name"""
    display_name = get_display_name(site_code)
    return f"<b>{display_name}</b><br>%{{x}}<br>Score: %{{y:.1f}}%<extra></extra>"
