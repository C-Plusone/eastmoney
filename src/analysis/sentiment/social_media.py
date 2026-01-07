import akshare as ak
import pandas as pd

class SocialSentinel:
    def get_social_sentiment(self):
        """
        获取市场舆情热度数据
        """
        try:
            # 东方财富个股人气榜
            df = ak.stock_hot_rank_em()
            if df is None or df.empty:
                return {}
            
            # 简化列名，防止乱码困扰 (假设顺序: 排名, 代码, 名称, 最新价, 涨跌幅...)
            # 通常 df.columns 是中文，我们重命名一下以便后续处理
            # 观察 debug 输出: ['当前排名', '代码', '股票名称', '最新价', '涨跌额', '涨跌幅', ...]
            rename_map = {
                df.columns[0]: 'rank',
                df.columns[1]: 'code',
                df.columns[2]: 'name',
                df.columns[3]: 'price',
                df.columns[5]: 'pct_change' # 涨跌幅
            }
            df = df.rename(columns=rename_map)
            
            # --- 分析逻辑 ---
            
            # 1. 散户大本营 (Top 5)
            # 这些票热度最高，如果是高位滞涨，风险极大
            top_5 = df.head(5)[['rank', 'name', 'code', 'pct_change']].to_dict(orient='records')
            
            # 2. 情绪核心 (Top 20 中涨幅 > 9% 的票)
            # 代表市场最认可的赚钱效应方向
            emotion_core = df[
                (df['rank'] <= 20) & 
                (df['pct_change'] > 9.0)
            ][['rank', 'name', 'code', 'pct_change']].to_dict(orient='records')
            
            # 3. 抄底大军 (Top 20 中跌幅 < -5% 的票)
            # 散户在接飞刀
            catch_knife = df[
                (df['rank'] <= 20) & 
                (df['pct_change'] < -5.0)
            ][['rank', 'name', 'code', 'pct_change']].to_dict(orient='records')

            return {
                "top_hot": top_5,          # 人气Top5
                "emotion_core": emotion_core, # 强势人气股
                "catch_knife": catch_knife    # 弱势人气股
            }
            
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    sentinel = SocialSentinel()
    data = sentinel.get_social_sentiment()
    print(data)
