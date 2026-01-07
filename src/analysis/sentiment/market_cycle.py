import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime

class MarketCycleAnalyst:
    def __init__(self, date_str: str = None):
        """
        :param date_str: YYYYMMDD format. If None, uses today.
        """
        if date_str:
            self.date_str = date_str
        else:
            self.date_str = datetime.now().strftime("%Y%m%d")
            
    def get_cycle_metrics(self):
        """
        获取市场情绪周期核心指标
        """
        try:
            # 1. 获取涨停池 (Limit Up Pool)
            df_zt = ak.stock_zt_pool_em(date=self.date_str)
            
            # 2. 获取炸板池 (Broken Limit Pool)
            df_zb = ak.stock_zt_pool_zbgc_em(date=self.date_str)
            
            # 3. 获取昨日涨停今日表现 (Yesterday Limit Up Performance)
            df_prev_zt = ak.stock_zt_pool_previous_em(date=self.date_str)
            
            # 基础计数
            zt_count = len(df_zt) if df_zt is not None else 0
            zb_count = len(df_zb) if df_zb is not None else 0
            total_attempt = zt_count + zb_count
            
            # --- 核心指标计算 ---
            
            # A. 封板率 (Seal Rate)
            seal_rate = (zt_count / total_attempt * 100) if total_attempt > 0 else 0
            
            # B. 连板高度 (Height)
            # 假设列名包含 '连板数'
            market_height = 0
            height_map = {} # {2: 10, 3: 5...}
            if df_zt is not None and not df_zt.empty and '连板数' in df_zt.columns:
                market_height = df_zt['连板数'].max()
                # 统计连板分布
                height_counts = df_zt['连板数'].value_counts().sort_index(ascending=False)
                height_map = height_counts.to_dict()
                
            # C. 赚钱效应 (Money Effect)
            # 计算昨日涨停股今天的平均涨幅
            avg_profit = 0.0
            profit_rate = 0.0 # 红盘率
            if df_prev_zt is not None and not df_prev_zt.empty:
                # 列名通常是 '涨跌幅'
                if '涨跌幅' in df_prev_zt.columns:
                    avg_profit = df_prev_zt['涨跌幅'].mean()
                    profit_rate = (len(df_prev_zt[df_prev_zt['涨跌幅'] > 0]) / len(df_prev_zt)) * 100

            # D. 跌停数 (核按钮) - 暂时用 ak.stock_zt_pool_dtgc_em (跌停股池)
            # 注: akshare 可能没有直接的 stock_zt_pool_dtgc_em (这是跌停), 
            # 通常跌停数据不如涨停好找，可以用实时行情筛选
            dt_count = 0
            try:
                # 尝试获取跌停池，如果没有则忽略或通过行情筛选
                df_dt = ak.stock_zt_pool_dtgc_em(date=self.date_str)
                dt_count = len(df_dt) if df_dt is not None else 0
            except:
                pass

            return {
                "date": self.date_str,
                "zt_count": int(zt_count), # 涨停数
                "zb_count": int(zb_count), # 炸板数
                "dt_count": int(dt_count), # 跌停数
                "seal_rate": round(seal_rate, 2), # 封板率 %
                "market_height": int(market_height), # 最高板
                "height_dist": height_map, # 连板梯队
                "avg_profit": round(avg_profit, 2), # 昨日涨停今日平均溢价
                "profit_rate": round(profit_rate, 2) # 昨日涨停今日红盘率
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "date": self.date_str
            }

    def determine_cycle_phase(self, metrics):
        """
        根据指标简单判断所处周期阶段 (LLM可进一步润色)
        """
        if "error" in metrics:
            return "Unknown (Data Error)"
            
        seal_rate = metrics['seal_rate']
        zt_count = metrics['zt_count']
        zb_count = metrics['zb_count']
        dt_count = metrics['dt_count']
        
        # 简单规则引擎
        if dt_count > 20 and zt_count < 30:
            return "Ice Point (冰点/退潮)"
        elif seal_rate < 60 and zb_count > 20:
            return "Divergence (强分歧/炸板潮)"
        elif seal_rate > 75 and zt_count > 50:
            return "Climax (高潮/主升)"
        elif zt_count > 40 and metrics['market_height'] >= 3:
             return "Fermentation (发酵/启动)"
        else:
            return "Rotation (震荡/轮动)"

if __name__ == "__main__":
    # Test
    analyst = MarketCycleAnalyst()
    metrics = analyst.get_cycle_metrics()
    print("Metrics:", metrics)
    print("Phase:", analyst.determine_cycle_phase(metrics))
