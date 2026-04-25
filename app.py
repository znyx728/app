"""
app.py - Streamlit查询界面
"""
import streamlit as st
import pandas as pd
import os

# 读取数据
@st.cache_data
def load_data():
    # 支持exe打包后的路径查找
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_path, "poker_equity_corrected.xlsx")
    return pd.read_excel(file_path)

# 页面配置
st.set_page_config(
    page_title="德州扑克胜率查询器",
    page_icon="♠️",
    layout="centered"
)

st.title("♠️ 德州扑克翻前胜率查询器")
st.markdown("---")

try:
    df = load_data()
except:
    st.error("找不到数据文件 poker_equity_corrected.xlsx")
    st.stop()

# 选择手牌
hand = st.selectbox(
    "🎴 你的手牌",
    df['手牌'].tolist(),
    help="选择你发到的两张牌"
)

# 选择范围
range_options = {
    "绝对胜率_%": "对抗随机牌",
    "vs_all_pairs_胜率_%": "对抗口袋对",
    "vs_broadway_胜率_%": "对抗百老汇牌",
    "vs_top20pct_胜率_%": "对抗前20%强牌"
}

range_type = st.selectbox(
    "🎯 对手范围",
    list(range_options.keys()),
    format_func=lambda x: range_options[x],
    help="对手可能持有的手牌范围"
)

# 查询胜率
equity = df[df['手牌'] == hand][range_type].values[0]

# 显示结果
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("你的胜率", f"{equity}%", delta=None)

# 行动建议
if equity >= 60:
    advice = "✅ 建议加注 / All-in"
    color = "green"
elif equity >= 45:
    advice = "⚠️ 可跟注，谨慎加注"
    color = "orange"
else:
    advice = "❌ 建议弃牌"
    color = "red"

with col2:
    st.markdown(f"<h3 style='color:{color}'>{advice}</h3>", unsafe_allow_html=True)

# 进度条可视化
st.progress(equity / 100)
st.caption(f"胜率 {equity}%，数值越高越值得玩")

st.markdown("---")
st.caption("数据来源：蒙特卡洛模拟（每手牌10,000次迭代）")