import sys
import os
from datetime import datetime

# Add project root to sys.path if run directly
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.analysis.sentiment.market_cycle import MarketCycleAnalyst
from src.analysis.sentiment.news_mining import NewsMiner
from src.analysis.sentiment.social_media import SocialSentinel
from src.analysis.sentiment.money_flow import MoneyFlowAnalyst
from src.llm.client import get_llm_client

class SentimentDashboard:
    def __init__(self):
        self.llm = get_llm_client()
        self.cycle_analyst = MarketCycleAnalyst()
        self.news_miner = NewsMiner()
        self.social_sentinel = SocialSentinel()
        self.money_analyst = MoneyFlowAnalyst()

    def run_analysis(self):
        print("1. Analyzing Market Cycle...")
        cycle_data = self.cycle_analyst.get_cycle_metrics()
        cycle_phase = self.cycle_analyst.determine_cycle_phase(cycle_data)
        
        print("2. Mining News...")
        news_items = self.news_miner.fetch_recent_news(limit=15)
        news_report = self.news_miner.analyze_news_sentiment(news_items)
        
        print("3. Checking Social Sentiment...")
        social_data = self.social_sentinel.get_social_sentiment()
        
        print("4. Tracking Money Flow...")
        money_data = self.money_analyst.get_money_flow()
        
        print("5. Generating Final Dashboard Report...")
        final_report = self.generate_final_report(cycle_data, cycle_phase, news_report, social_data, money_data)
        
        return final_report

    def generate_final_report(self, cycle, phase, news_analysis, social, money):
        def _fmt_list(items, limit: int = 5) -> str:
            if not items:
                return "(无)"
            lines = []
            for i, item in enumerate(items[:limit], 1):
                if isinstance(item, dict):
                    name = item.get("name") or item.get("股票名称") or item.get("title") or "N/A"
                    code = item.get("code") or item.get("股票代码")
                    pct = item.get("pct_change")
                    net_buy = item.get("net_buy")
                    parts = [f"{i}. {name}"]
                    if code:
                        parts.append(f"({code})")
                    if pct is not None:
                        parts.append(f"{pct}%")
                    if net_buy is not None:
                        parts.append(f"净买入{net_buy}亿")
                    lines.append(" ".join(str(p) for p in parts if p is not None))
                else:
                    lines.append(f"{i}. {item}")
            return "\n".join(lines)

        report_date = datetime.now().strftime('%Y-%m-%d')
        north_date = (money or {}).get("north_date")
        inst_date = (money or {}).get("institution_date")

        # Normalize key inputs for prompt readability
        zt_count = cycle.get('zt_count')
        zb_count = cycle.get('zb_count')
        seal_rate = cycle.get('seal_rate')
        market_height = cycle.get('market_height')
        avg_profit = cycle.get('avg_profit')

        top_hot = (social or {}).get('top_hot')
        emotion_core = (social or {}).get('emotion_core')
        catch_knife = (social or {}).get('catch_knife')
        institution_buy = (money or {}).get('institution_buy')
        north_money = (money or {}).get('north_money')

        prompt = f"""
        【角色设定】
        你是一位身经百战的A股超短游资大佬，风格犀利，厌恶废话，擅长捕捉情绪周期的拐点。
        请根据以下数据，为散户兄弟们写一份【实战情绪日报】。

        【核心原则（必须遵守）】
        1) 只能基于输入数据做判断；不允许编造个股消息、资金数值、政策细节。
        2) 每个结论必须引用至少 2 个不同维度的证据：周期指标 + 资金/舆情/消息面之一。
        3) 遇到缺失/为0/明显滞后的数据，要明确标注“数据可能滞后/缺失”，不要强行解读。
        4) 输出要“短句+结论”，但逻辑要完整：先定性→再给关键证据→最后给可执行策略。
        
        【1. 市场周期数据 (客观指标)】
        - 阶段判定: {phase} (基于数据的算法判定，仅供参考，请结合数据修正)
        - 涨停数: {zt_count} (多<30偏冰点，>60偏活跃)
        - 炸板数: {zb_count}
        - 封板率: {seal_rate}% (⚠️ 低于65%意味着大面概率上升)
        - 连板高度: {market_height}板 (代表投机空间)
        - 赚钱效应(昨日涨停溢价): {avg_profit}% (正值代表接力更易赚钱)
        
        【2. 资金博弈 (Smart Money)】
        - 北向资金(当日净流入): {north_money} 亿元 (数据日期: {north_date})
        - 机构净买入Top5(龙虎榜口径): (数据日期: {inst_date})
        {_fmt_list(institution_buy, 5)}
        
        【3. 社区舆情 (散户反向指标)】
        - ⚠️ 人气Top5 (警惕高位接盘):
        {_fmt_list(top_hot, 5)}
        - 🔥 情绪核心 (Top20里强势>9%):
        {_fmt_list(emotion_core, 5)}
        - 🧊 接飞刀名单 (Top20里<-5%):
        {_fmt_list(catch_knife, 5)}
        
        【4. 消息面核心驱动 (AI初筛结果)】
        {news_analysis}
        
        ---
        【写作要求】
        请输出 Markdown 格式，结构如下：
        
        # 🐂 A股情绪实战日报 ({report_date})
        
        ## 🔥 核心结论
        (用一句话定性：今天是“情绪主升/吃肉”、“分歧退潮/吃面”还是“冰点试错/抄底”？)
        
        ## 1️⃣ 周期定位与博弈
        - **当前水位**: **{phase}**
        - **数据解读**: (必须点名使用：涨停数、封板率、溢价率/赚钱效应、连板高度；并给出你判断的“主线/风险点”。)
        
        ## 2️⃣ 舆情与主力透视
        - **散户都在买什么**: (点评Top5人气股，如果是高位股，大喊“快跑”；如果是低位启动，提示“关注”。)
        - **机构/游资动向**: (必须说明北向与机构数据是否“当日/滞后”；若北向为0或日期不一致，明确写“数据可能未更新”，不要强行归因。)
        
        ## 3️⃣ 消息面核心逻辑
        (从消息面初筛结果中，挑出明天最可能延续的一个板块：给出“为什么能延续”的两条硬理由 + “一条反证风险”。)
        
        ## 💡 明日操盘策略
        - **激进型 (打板/接力)**: (给出1条可执行规则：例如“只做首板/只做换手二板/只做趋势回踩”，并说明触发条件和止损。)
        - **稳健型 (低吸/趋势)**: (给出1条可执行规则：例如“只做指数共振/只做情绪核心回踩”，并说明触发条件和止损。)
        """
        
        print("DEBUG: Final prompt for LLM generated.",prompt)

        return self.llm.generate_content(prompt)

if __name__ == "__main__":
    dashboard = SentimentDashboard()
    report = dashboard.run_analysis()
    
    # Ensure reports dir exists
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/sentiment_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {os.path.abspath(filename)}")
