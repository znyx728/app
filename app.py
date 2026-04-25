"""
app.py - 德州扑克胜率查询器（使用 CSV，不需要 openpyxl）
"""
import streamlit as st
import pandas as pd
import os
import sys

st.set_page_config(
    page_title="德州扑克胜率查询器",
    page_icon="♠️",
    layout="centered"
)

def find_data_file():
    """查找数据文件（支持 CSV 和 Excel）"""
    # 优先使用 CSV
    for filename in ["poker_equity_corrected.csv", "poker_equity_corrected.xlsx"]:
        # 当前目录
        if os.path.exists(filename):
            return filename
        
        # 脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, filename)
        if os.path.exists(path):
            return path
        
        # 全局搜索
        import pathlib
        for p in pathlib.Path('.').glob(f'**/{filename}'):
            return str(p)
    
    return None

@st.cache_data
def load_data():
    file_path = find_data_file()
    if file_path is None:
        st.error("❌ 找不到数据文件")
        st.info("请确保 poker_equity_corrected.csv 或 poker_equity_corrected.xlsx 在仓库根目录")
        st.stop()
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"读取文件失败: {e}")
        st.stop()

# ========== 主界面 ==========
st.title("♠️ 德州扑克翻前胜率查询器")
st.markdown("---")

df = load_data()

# 显示列名（调试用，部署后可以删除这一行）
with st.expander("数据预览（可忽略）"):
    st.write(df.head(3))

hand = st.selectbox("🎴 你的手牌", df['手牌'].tolist())

range_options = {
    "绝对胜率_%": "对抗随机牌",
    "vs_all_pairs_胜率_%": "对抗口袋对",
    "vs_broadway_胜率_%": "对抗百老汇牌",
    "vs_top20pct_胜率_%": "对抗前20%强牌"
}

range_type = st.selectbox(
    "🎯 对手范围",
    list(range_options.keys()),
    format_func=lambda x: range_options[x]
)

equity = df[df['手牌'] == hand][range_type].values[0]

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.metric("📊 胜率", f"{equity}%")

if equity >= 60:
    advice = "✅ 强烈建议：加注 / All-in"
    color = "green"
elif equity >= 45:
    advice = "⚠️ 建议：跟注，谨慎加注"
    color = "orange"
elif equity >= 35:
    advice = "🤔 建议：弃牌或仅在大盲位跟注"
    color = "red"
else:
    advice = "❌ 强烈建议：弃牌"
    color = "red"

with col2:
    st.markdown(f"<h3 style='color:{color}'>{advice}</h3>", unsafe_allow_html=True)

st.progress(equity / 100)
st.caption(f"胜率 {equity}%，数值越高越值得投入筹码")

st.markdown("---")
st.caption("数据来源：蒙特卡洛模拟（每手牌10,000次迭代）| 误差范围 ±1-2%")
