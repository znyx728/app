"""
app.py - 德州扑克胜率查询器（支持Streamlit Cloud部署）
"""
import streamlit as st
import pandas as pd
import os
import sys

# 页面配置（必须是第一个Streamlit命令）
st.set_page_config(
    page_title="德州扑克胜率查询器",
    page_icon="♠️",
    layout="centered"
)

# 查找数据文件的函数
def find_data_file():
    """
    在多个可能的位置查找数据文件
    支持：本地运行、打包成exe、Streamlit Cloud部署
    """
    filename = "poker_equity_corrected.xlsx"
    
    # 位置1：当前工作目录
    if os.path.exists(filename):
        return filename
    
    # 位置2：脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path2 = os.path.join(script_dir, filename)
    if os.path.exists(path2):
        return path2
    
    # 位置3：上一级目录
    parent_dir = os.path.dirname(script_dir)
    path3 = os.path.join(parent_dir, filename)
    if os.path.exists(path3):
        return path3
    
    # 位置4：exe打包后的临时目录
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        path4 = os.path.join(exe_dir, filename)
        if os.path.exists(path4):
            return path4
    
    # 位置5：Streamlit Cloud的默认路径
    import pathlib
    for path in pathlib.Path('.').glob(f'**/{filename}'):
        return str(path)
    
    return None

# 加载数据
@st.cache_data
def load_data():
    file_path = find_data_file()
    if file_path is None:
        st.error("❌ 找不到数据文件 poker_equity_corrected.xlsx")
        st.info("""
        **请确保以下文件在仓库根目录：**
        - app.py
        - poker_equity_corrected.xlsx
        - requirements.txt
        
        如果文件已存在，请检查文件名大小写是否完全一致。
        """)
        st.stop()
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"读取文件失败: {e}")
        st.stop()

# ========== 主界面 ==========
st.title("♠️ 德州扑克翻前胜率查询器")
st.markdown("---")

# 加载数据
df = load_data()

# 选择手牌
hand = st.selectbox(
    "🎴 你的手牌",
    df['手牌'].tolist(),
    help="选择你发到的两张牌"
)

# 对手范围选项
range_options = {
    "绝对胜率_%": "对抗随机牌（任何两张）",
    "vs_all_pairs_胜率_%": "对抗口袋对（22-AA）",
    "vs_broadway_胜率_%": "对抗百老汇牌（TJQKA组合）",
    "vs_top20pct_胜率_%": "对抗前20%强牌"
}

range_type = st.selectbox(
    "🎯 对手范围",
    list(range_options.keys()),
    format_func=lambda x: range_options[x]
)

# 查询胜率
equity = df[df['手牌'] == hand][range_type].values[0]

# 显示结果
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.metric("📊 胜率", f"{equity}%")

# 行动建议
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

# 进度条
st.progress(equity / 100)
st.caption(f"胜率 {equity}%，数值越高越值得投入筹码")

st.markdown("---")
st.caption("数据来源：蒙特卡洛模拟（每手牌10,000次迭代）| 误差范围 ±1-2%")
