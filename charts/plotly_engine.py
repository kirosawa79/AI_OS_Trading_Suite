import plotly.graph_objects as go

def market_chart(data, ticker: str):
    d=data.tail(80)
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=d.index,open=d['Open'],high=d['High'],low=d['Low'],close=d['Close'],name=ticker))
    for col in ['EMA9','EMA20','EMA40','EMA100','EMA200']:
        fig.add_trace(go.Scatter(x=d.index,y=d[col],mode='lines',name=col))
    fig.add_trace(go.Scatter(x=d.index,y=d['BB_Sup'],mode='lines',name='BB superior',line={'dash':'dash'}))
    fig.add_trace(go.Scatter(x=d.index,y=d['BB_Inf'],mode='lines',name='BB inferior',line={'dash':'dash'}))
    fig.update_layout(height=500,xaxis_rangeslider_visible=False,margin=dict(l=10,r=10,t=35,b=10),template='plotly_dark')
    return fig
