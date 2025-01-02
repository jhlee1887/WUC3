from dash import dcc, html, Input, Output
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

# 앱 생성
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# 상단바 스타일
NAVBAR_STYLE = {
    "backgroundColor": "#87CEEB",  # 상단바 배경 하늘색
    "padding": "10px",
    "width": "100vw",
    "display": "flex",
    "justifyContent": "space-between",
    "alignItems": "center",
}

TAB_STYLE = {
    "color": "white",
    "fontWeight": "bold",
    "padding": "10px",
    "marginLeft": "10px",
    "borderRadius": "5px",
     # 기본 탭 배경 진한 파란색
}

TAB_ACTIVE_STYLE = {
    "backgroundColor": "#1E90FF",  # 활성화된 탭 배경 색
    "color": "white",
    "fontWeight": "bold",
    "padding": "10px",
    "marginLeft": "10px",
    "borderRadius": "5px",
}

# 상단바
navbar = html.Div(
    style=NAVBAR_STYLE,
    children=[ 
        html.Span(
            "3조",
            style={"color": "white", "fontWeight": "bold", "fontSize": "18px"},
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(
            id="tabs-container",
            style={"display": "flex", "alignItems": "center"},
        ),
    ],
)

# 페이지 콘텐츠
content = html.Div(id="page-content", style={"marginTop": "70px", "padding": "20px"})

# 레이아웃 설정
app.layout = html.Div([navbar, content])

# 탭 설정
tabs = [
    {"label": "Home", "href": "/", "icon": "bi bi-house-door-fill"},
    {"label": "final", "href": "/final-data", "icon": "bi bi-sun"},
    {"label": "hourly", "href": "/hourly-data", "icon": "bi bi-diagram-3"},
    {"label": "monthly", "href": "/monthly-data", "icon": "bi bi-diagram-3"},
    {"label": "yearly", "href": "/yearly-data", "icon": "bi bi-diagram-3"},
]

# 콜백으로 탭 스타일 동적으로 적용
@app.callback(
    Output("tabs-container", "children"),
    [Input("url", "pathname")]
)
def update_tabs(pathname):
    return [
        dbc.NavLink(
            [html.I(className=tab["icon"]), f" {tab['label']}"],
            href=tab["href"],
            style=TAB_ACTIVE_STYLE if tab["href"] == pathname else TAB_STYLE,
        )
        for tab in tabs
    ]

# 데이터셋 로드
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
df2 = pd.read_csv('../data/final_df.csv')
hourly_df = pd.read_csv('../data/hourly_avg.csv')
monthly_df = pd.read_csv('../data/monthly_avg.csv')
yearly_df = pd.read_csv('../data/yearly_avg.csv')

# 페이지 콘텐츠 업데이트 콜백
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/":
        return html.Div([html.H3("Home"), html.P("프로젝트 개요 및 필요성을 설명합니다.")])
    elif pathname == "/final-data":
        return html.Div([
            html.H3("Final Data"),
            html.P("예측 데이터와 결과를 확인합니다."),
            dcc.Dropdown(
                id='dropdown-selection-stn',
                options=[{'label': stnNm, 'value': stnNm} for stnNm in df2['stnNm'].unique()],
                value='영천',
                style={'width': '50%'}
            ),
            dcc.Dropdown(
                id='data-selection',
                options=[
                    {'label': 'Temperature (ta)', 'value': 'ta'},
                    {'label': 'Rainfall (rn)', 'value': 'rn'},
                    {'label': 'Humidity (hm)', 'value': 'hm'}
                ],
                value='ta',  # 기본값: 'ta' (기온)
                style={'width': '50%'}
            ),
            dcc.Graph(id='graph-content-stn')
        ])
    elif pathname == "/hourly-data":
         return html.Div([
            html.H3("Hourly Data"),
            html.P("시간별 기상 데이터를 확인합니다."),
            dcc.Dropdown(
                id='hourly-data-selection',
                options=[
                    {'label': 'Temperature (ta)', 'value': 'ta'},
                    {'label': 'Rainfall (rn)', 'value': 'rn'},
                    {'label': 'Humidity (hm)', 'value': 'hm'},
                    {'label': 'Pressure (pa)', 'value': 'pa'},
                    {'label': 'Solar Radiation (ts)', 'value': 'ts'},
                    {'label': 'Gap (gap)', 'value': 'gap'}
                ],
                value='ta',  # 기본값: 'ta' (기온)
                style={'width': '50%'}
            ),
            dcc.Graph(id='hourly-graph')
        ])
    elif pathname == "/monthly-data":
           return html.Div([
            html.H3("Monthly Data"),
            html.P("월별 기상 데이터를 확인합니다."),
            # 'monthly-data-selection' 드롭다운 추가
            dcc.Dropdown(
                id='monthly-data-selection',
                options=[
                    {'label': 'Temperature (ta)', 'value': 'ta'},
                    {'label': 'Rainfall (rn)', 'value': 'rn'},
                    {'label': 'Humidity (hm)', 'value': 'hm'},
                    {'label': 'Pressure (pa)', 'value': 'pa'},
                    {'label': 'Solar Radiation (ts)', 'value': 'ts'},
                    {'label': 'Gap (gap)', 'value': 'gap'}
                ],
                value='ta',  # 기본값: 'ta' (기온)
                style={'width': '50%'}
            ),
            dcc.Graph(id='monthly-graph')
        ])
    elif pathname == "/yearly-data":
         return html.Div([
            html.H3("Yearly Data"),
            html.P("연도별 기상 데이터를 확인합니다."),
            dcc.Dropdown(
                id='yearly-data-selection',
                options=[
                    {'label': 'Temperature (ta)', 'value': 'ta'},
                    {'label': 'Rainfall (rn)', 'value': 'rn'},
                    {'label': 'Humidity (hm)', 'value': 'hm'},
                    {'label': 'Pressure (pa)', 'value': 'pa'},
                    {'label': 'Solar Radiation (ts)', 'value': 'ts'},
                    {'label': 'Gap (gap)', 'value': 'gap'}
                ],
                value='ta',  # 기본값: 'ta' (기온)
                style={'width': '50%'}
            ),
            dcc.Graph(id='yearly-graph')
        ])
    else:
        return html.Div([html.H3("404 에러"), html.P("페이지를 찾을 수 없습니다.")])

# 그래프 업데이트 콜백
@app.callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value')]
)
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x='year', y='pop', title=f'Population Growth of {value}')

# 그래프 업데이트 콜백 (기상 데이터 선택 탭2)
@app.callback(
    Output('graph-content-stn', 'figure'),
    [
        Input('dropdown-selection-stn', 'value'),
        Input('data-selection', 'value')
    ]
)
def update_weather_graph(stn_name, data_type):
    # 선택된 지역(stnNm)으로 데이터 필터링
    dff = df2[df2['stnNm'] == stn_name]
    
    # tm 컬럼을 datetime 형식으로 변환
    dff['date'] = pd.to_datetime(dff['tm'])
    
    # 그래프를 그리기 위한 데이터 컬럼 선택
    if data_type == 'ta':
        y_col = 'ta'  # 기온
    elif data_type == 'rn':
        y_col = 'rn'  # 강수량
    elif data_type == 'hm':
        y_col = 'hm'  # 습도
    
    # 그래프 그리기
    return px.line(dff, x='date', y=y_col, title=f'{stn_name} {data_type}')


# Hourly Data 그래프 업데이트 콜백
@app.callback(
    Output('hourly-graph', 'figure'),
    [Input('hourly-data-selection', 'value')]
)
def update_hourly_graph(data_type):
    # hourly_avg.csv에서 데이터 로드
    df = hourly_df
    
    # 시간별 x축 (hour) 설정
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,  # x축 공유
        vertical_spacing=0.1
    )

    # 선택된 데이터에 따라 그래프 추가
    fig.add_trace(
        go.Scatter(x=df['hour'], y=df[data_type], mode='lines', name=data_type),
        row=1, col=1
    )
    
    # 레이아웃 설정
    fig.update_layout(
        title=f'Hourly {data_type}',
        xaxis_title='Hour',
        yaxis_title=f'{data_type} Value',
    )

    return fig

# Monthly Data 그래프 업데이트 콜백
@app.callback(
    Output('monthly-graph', 'figure'),
    [Input('monthly-data-selection', 'value')]
)
def update_monthly_graph(data_type):
    # monthly_avg.csv에서 데이터 로드
    df = monthly_df
    
    # 월별 x축 (month) 설정
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,  # x축 공유
        vertical_spacing=0.1
    )

    # 선택된 데이터에 따라 그래프 추가
    fig.add_trace(
        go.Scatter(x=df['month'], y=df[data_type], mode='lines', name=data_type),
        row=1, col=1
    )
    
    # 레이아웃 설정
    fig.update_layout(
        title=f'Monthly {data_type}',
        xaxis_title='Month',
        yaxis_title=f'{data_type} Value',
    )

    return fig

# Yearly Data 그래프 업데이트 콜백
@app.callback(
    Output('yearly-graph', 'figure'),
    [Input('yearly-data-selection', 'value')]
)
def update_yearly_graph(data_type):
    # yearly_avg.csv에서 데이터 로드
    df = yearly_df
    
    # 연도별 x축 (year) 설정
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,  # x축 공유
        vertical_spacing=0.1
    )

    # 선택된 데이터에 따라 그래프 추가
    fig.add_trace(
        go.Scatter(x=df['year'], y=df[data_type], mode='lines', name=data_type),
        row=1, col=1
    )
    
    # 레이아웃 설정
    fig.update_layout(
        title=f'Yearly {data_type}',
        xaxis_title='Year',
        yaxis_title=f'{data_type} Value',
    )

    return fig


# 앱 실행
if __name__ == "__main__":
    app.run_server(debug=True)
