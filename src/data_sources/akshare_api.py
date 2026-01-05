import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import inspect
from typing import Dict, List, Optional

# ============================================================================
# SECTION 1: 全球宏观市场数据 (Global Macro Data)
# ============================================================================

def get_us_market_overview() -> Dict:
    """
    获取隔夜美股市场概览：三大指数 + 中概股指数
    Returns: {指数名: {最新价, 涨跌幅, ...}}
    """
    result = {}
    try:
        # 美股主要指数 - 使用东方财富接口
        df = ak.stock_us_famous_spot_em()
        if not df.empty:
            for col in df.columns:
                df[col] = df[col].astype(str) if df[col].dtype == 'object' else df[col]
            
            key_indices = ["道琼斯", "纳斯达克", "标普500"]
            name_col = next((c for c in df.columns if '名称' in c or 'name' in c.lower()), df.columns[0])
            
            for idx_name in key_indices:
                row = df[df[name_col].str.contains(idx_name, na=False)]
                if not row.empty:
                    result[idx_name] = row.iloc[0].to_dict()
    except Exception as e:
        print(f"Error fetching US market: {e}")
    
    return result

def get_a50_futures() -> Dict:
    """
    获取富时A50期货数据（新加坡交易所）
    用于预判A股开盘方向
    """
    try:
        # 尝试获取新加坡A50期货
        df = ak.futures_global_spot()
        if not df.empty:
            a50_row = df[df.iloc[:, 0].astype(str).str.contains('A50|富时|FTSE', na=False, case=False)]
            if not a50_row.empty:
                return a50_row.iloc[0].to_dict()
    except Exception as e:
        print(f"Error fetching A50 futures: {e}")
    
    # 备用方案：返回空但不影响流程
    return {"说明": "A50期货数据暂时无法获取，请关注盘前竞价"}

def get_forex_rates() -> Dict:
    """
    获取关键汇率：美元/人民币
    """
    try:
        df = ak.fx_spot_quote()
        if not df.empty:
            usdcny = df[df['货币对'].str.contains('USD/CNY|美元/人民币', na=False)]
            if not usdcny.empty:
                return {"美元/人民币": usdcny.iloc[0].to_dict()}
    except Exception as e:
        print(f"Error fetching forex: {e}")
    return {}

def get_global_macro_summary() -> Dict:
    """
    汇总全球宏观数据 - 盘前分析核心输入
    """
    return {
        "美股市场": get_us_market_overview(),
        "A50期货": get_a50_futures(),
        "汇率": get_forex_rates()
    }

# ============================================================================
# SECTION 2: 北向资金与资金流向 (Capital Flow)
# ============================================================================

def get_northbound_flow() -> Dict:
    """
    获取北向资金（沪股通+深股通）净流入数据
    """
    result = {}
    try:
        # 尝试多个可能的API
        df = None
        api_funcs = [
            lambda: ak.stock_hsgt_hist_em(symbol="北向资金"),
            lambda: ak.stock_em_hsgt_north_net_flow_in(indicator="沪股通"),
        ]
        
        for func in api_funcs:
            try:
                df = func()
                if df is not None and not df.empty:
                    break
            except:
                continue
        
        if df is not None and not df.empty:
            # 最近5个交易日
            recent = df.tail(5)
            result['近5日数据'] = recent.to_dict('records')
            result['最新净流入'] = df.iloc[-1].to_dict()
            
            # 尝试计算5日累计
            for col in df.columns:
                if '净' in str(col) and '流' in str(col):
                    try:
                        result['5日累计净流入'] = round(recent[col].astype(float).sum(), 2)
                    except:
                        pass
                    break
    except Exception as e:
        print(f"Error fetching northbound flow: {e}")
    return result

def get_industry_capital_flow(industry: str = None) -> Dict:
    """
    获取行业资金流向
    """
    try:
        df = ak.stock_sector_fund_flow_rank()
        if not df.empty:
            if industry:
                filtered = df[df['名称'].str.contains(industry, na=False)]
                if not filtered.empty:
                    return filtered.iloc[0].to_dict()
            # 返回前10行业
            return {"行业资金流向Top10": df.head(10).to_dict('records')}
    except Exception as e:
        print(f"Error fetching industry capital flow: {e}")
    return {}

# ============================================================================
# SECTION 3: 个股深度数据 (Stock Deep Dive)
# ============================================================================

def get_stock_announcement(stock_code: str, stock_name: str) -> List[Dict]:
    """
    获取个股最新公告（东方财富）
    """
    announcements = []
    try:
        # 尝试获取公告
        df = ak.stock_notice_report(symbol=stock_code)
        if not df.empty:
            # 最近7天的公告
            recent = df.head(5)
            announcements = recent.to_dict('records')
    except Exception as e:
        print(f"Error fetching announcements for {stock_name}: {e}")
    return announcements

def get_stock_realtime_quote(stock_code: str) -> Dict:
    """
    获取个股实时/最新行情
    """
    try:
        # 根据股票代码判断市场
        if stock_code.startswith('6'):
            full_code = f"sh{stock_code}"
        elif stock_code.startswith(('0', '3')):
            full_code = f"sz{stock_code}"
        else:
            full_code = stock_code
            
        df = ak.stock_zh_a_spot_em()
        if not df.empty:
            stock = df[df['代码'] == stock_code]
            if not stock.empty:
                return stock.iloc[0].to_dict()
    except Exception as e:
        print(f"Error fetching realtime quote for {stock_code}: {e}")
    return {}

def get_stock_news_sentiment(stock_name: str) -> List[Dict]:
    """
    获取个股相关新闻（东方财富）
    """
    try:
        df = ak.stock_news_em(symbol=stock_name)
        if not df.empty:
            return df.head(5).to_dict('records')
    except Exception as e:
        print(f"Error fetching news for {stock_name}: {e}")
    return []

# ============================================================================
# SECTION 4: 行业与板块数据 (Sector Data)
# ============================================================================

def get_sector_performance(sector_name: str = None) -> Dict:
    """
    获取板块行情表现
    """
    try:
        df = ak.stock_board_industry_name_em()
        if not df.empty:
            if sector_name:
                filtered = df[df['板块名称'].str.contains(sector_name, na=False)]
                if not filtered.empty:
                    return filtered.iloc[0].to_dict()
            return {"板块涨幅榜": df.head(10).to_dict('records')}
    except Exception as e:
        print(f"Error fetching sector performance: {e}")
    return {}

def get_concept_board_performance(concept: str = None) -> Dict:
    """
    获取概念板块表现（如：AI、新能源等）
    """
    try:
        df = ak.stock_board_concept_name_em()
        if not df.empty:
            if concept:
                filtered = df[df['板块名称'].str.contains(concept, na=False)]
                if not filtered.empty:
                    return filtered.to_dict('records')
            return {"概念板块Top10": df.head(10).to_dict('records')}
    except Exception as e:
        print(f"Error fetching concept board: {e}")
    return {}

# ============================================================================
# SECTION 5: 原有函数（保留并优化）
# ============================================================================

def get_fund_info(fund_code: str):
    """
    Fetch basic fund information and net value history.
    Uses akshare's fund_open_fund_info_em or similar.
    """
    try:
        # Fetching net value history
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        # Expected columns: 净值日期, 单位净值, 日增长率
        # Sort by date descending so iloc[0] is the latest NAV
        if not df.empty and '净值日期' in df.columns:
            df = df.sort_values('净值日期', ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error fetching fund info for {fund_code}: {e}")
        return pd.DataFrame()

def get_fund_holdings(fund_code: str, year: str = None):
    """
    Fetch the latest top 10 holdings for the fund.
    Defaults to the current year if not specified.
    """
    current_year = str(datetime.now().year)
    if not year:
        year = current_year
    
    try:
        # fund_portfolio_hold_em signature varies by AkShare version.
        # In the installed AkShare (2024/06+), it is: fund_portfolio_hold_em(symbol, date)
        sig = None
        try:
            sig = inspect.signature(ak.fund_portfolio_hold_em)
        except Exception:
            sig = None

        def _call_holdings(target_year: str):
            if sig and "symbol" in sig.parameters:
                return ak.fund_portfolio_hold_em(symbol=fund_code, date=target_year)
            # Fallback for older/newer variants: try positional to avoid keyword mismatches
            try:
                return ak.fund_portfolio_hold_em(fund_code, target_year)
            except TypeError:
                # Last-resort: try legacy keywords if positional fails
                return ak.fund_portfolio_hold_em(code=fund_code, year=target_year)

        # fund_portfolio_hold_em: returns holding details
        df = _call_holdings(year)
        
        # Fallback to previous year if current year is empty (common in early Jan)
        if df.empty and year == current_year:
            prev_year = str(int(year) - 1)
            print(f"DEBUG: No data for {year}, trying {prev_year}...")
            df = _call_holdings(prev_year)

        # We generally want the latest quarter available
        if not df.empty:
            # Sort by date/quarter to get the latest
            # This API usually returns all quarters for the year.
            # We might need to filter for the latest '季度'
            return df
        return df
    except Exception as e:
        print(f"Error fetching holdings for {fund_code}: {e}")
        return pd.DataFrame()

def get_market_indices():
    """
    Fetch key market indices for context (A50, Shanghai Composite, etc.)
    Note: Real-time data might require different APIs. 
    Here we fetch daily historical data to get yesterday's close.
    """
    indices = {
        "sh000001": "上证指数",
        "sz399006": "创业板指"
    }
    
    market_data = {}
    try:
        for symbol, name in indices.items():
            # stock_zh_index_daily_em returns historical data
            df = ak.stock_zh_index_daily_em(symbol=symbol)
            if not df.empty:
                # Get the last row (most recent trading day)
                latest = df.iloc[-1].to_dict()
                market_data[name] = latest
        return market_data
    except Exception as e:
        print(f"Error fetching market indices: {e}")
        return {}