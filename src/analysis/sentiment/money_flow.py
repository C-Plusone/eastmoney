import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import requests

class MoneyFlowAnalyst:
    def get_money_flow(self):
        data = {
            "north_money": 0.0, # 单位：亿元
            "institution_buy": [],
            "north_date": None,
            "institution_date": None,
        }
        
        # 1. 北向资金
        try:
            # 兜底：历史北向（仅在“最近N天内有有效值”时使用，避免拿到很久以前的旧数据）
            if not data["north_money"]:
                hist_df = ak.stock_hsgt_hist_em(symbol="北向资金")
                if hist_df is not None and not hist_df.empty:
                    if "日期" in hist_df.columns:
                        hist_df = hist_df.copy()
                        hist_df["日期"] = pd.to_datetime(hist_df["日期"], errors="coerce")

                        flow_col = None
                        for col in ["当日成交净买额", "当日资金流入", "资金流入", "当日净流入"]:
                            if col in hist_df.columns:
                                s = pd.to_numeric(hist_df[col], errors="coerce")
                                if s.notna().any():
                                    flow_col = col
                                    break

                        if flow_col:
                            hist_df[flow_col] = pd.to_numeric(hist_df[flow_col], errors="coerce")
                            cutoff = datetime.now() - timedelta(days=10)
                            recent = hist_df[(hist_df["日期"].notna()) & (hist_df["日期"] >= cutoff) & (hist_df[flow_col].notna())]
                            if not recent.empty:
                                last = recent.sort_values("日期").iloc[-1]
                                data["north_money"] = round(float(last.get(flow_col)), 2)
                                data["north_date"] = last.get("日期").strftime("%Y-%m-%d")
                
        except Exception as e:
            print(f"North money error: {e}")

        # 2. 机构龙虎榜
        try:
            # 首选：Sina 的机构席位明细（按交易日，更新更及时）
            df_jg = ak.stock_lhb_jgmx_sina()
            if df_jg is not None and not df_jg.empty and "交易日期" in df_jg.columns:
                df_jg = df_jg.copy()
                df_jg["交易日期"] = pd.to_datetime(df_jg["交易日期"], errors="coerce")
                latest_date = df_jg["交易日期"].max()
                if pd.notna(latest_date):
                    data["institution_date"] = latest_date.strftime("%Y-%m-%d")
                    df_jg = df_jg[df_jg["交易日期"] == latest_date]

                buy_col = "机构席位买入额" if "机构席位买入额" in df_jg.columns else None
                sell_col = "机构席位卖出额" if "机构席位卖出额" in df_jg.columns else None
                name_col = "股票名称" if "股票名称" in df_jg.columns else None
                code_col = "股票代码" if "股票代码" in df_jg.columns else None

                if buy_col and sell_col and name_col:
                    buy = pd.to_numeric(df_jg[buy_col], errors="coerce").fillna(0)
                    sell = pd.to_numeric(df_jg[sell_col], errors="coerce").fillna(0)
                    df_jg["机构净买入额"] = buy - sell

                    group_cols = [name_col]
                    if code_col:
                        group_cols = [code_col, name_col]
                    grouped = df_jg.groupby(group_cols, as_index=False)["机构净买入额"].sum()
                    top_buy = grouped.sort_values(by="机构净买入额", ascending=False).head(5)

                    res = []
                    for _, row in top_buy.iterrows():
                        # Sina 该口径通常为“万元”，换算为“亿元”
                        net_wan = row.get("机构净买入额")
                        net_yi = None
                        try:
                            net_yi = round(float(net_wan) / 10000.0, 2)
                        except Exception:
                            net_yi = None

                        item = {"name": row.get(name_col), "net_buy": net_yi}
                        if code_col:
                            item["code"] = row.get(code_col)
                        res.append(item)
                    data["institution_buy"] = res

            # 兜底：东方财富汇总口径（有时会滞后/历史为主）
            if not data.get("institution_buy"):
                df_jg = ak.stock_lhb_jgmmtj_em()
                if df_jg is not None and not df_jg.empty:
                    date_col = "上榜日期" if "上榜日期" in df_jg.columns else None
                    if date_col:
                        df_jg[date_col] = pd.to_datetime(df_jg[date_col], errors="coerce")
                        latest_date = df_jg[date_col].max()
                        if pd.notna(latest_date):
                            data["institution_date"] = latest_date.strftime("%Y-%m-%d")
                            df_jg = df_jg[df_jg[date_col] == latest_date]

                    net_buy_col = None
                    for col in ["机构买入净额", "净买入", "净额"]:
                        if col in df_jg.columns:
                            net_buy_col = col
                            break
                    if net_buy_col is None:
                        for col in df_jg.columns:
                            if "净额" in str(col) or "净买入" in str(col):
                                net_buy_col = col
                                break

                    name_col = "名称" if "名称" in df_jg.columns else None
                    code_col = "代码" if "代码" in df_jg.columns else None

                    if net_buy_col and name_col:
                        df_jg[net_buy_col] = pd.to_numeric(df_jg[net_buy_col], errors="coerce")
                        top_buy = df_jg.sort_values(by=net_buy_col, ascending=False).head(5)

                        res = []
                        for _, row in top_buy.iterrows():
                            net_val = row.get(net_buy_col)
                            net_yi = None
                            try:
                                if pd.notna(net_val):
                                    net_yi = round(float(net_val) / 1e8, 2)
                            except Exception:
                                net_yi = None

                            item = {"name": row.get(name_col), "net_buy": net_yi}
                            if code_col:
                                item["code"] = row.get(code_col)
                            res.append(item)
                        data["institution_buy"] = res
                    
        except Exception as e:
            print(f"Institution error: {e}")
            
        return data

if __name__ == "__main__":
    analyst = MoneyFlowAnalyst()
    print(analyst.get_money_flow())