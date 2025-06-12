import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 设置页面标题和布局
st.set_page_config(page_title="跨境电商风控系统", layout="wide")
st.title("跨境电商风控仪表板")

# 侧边栏 - 部门选择和时间筛选
with st.sidebar:
    st.header("控制面板")
    department = st.selectbox("选择部门", ["全部", "项目部", "产品部", "采购部", "品质部", "数据部", "仓库部", "物流部"])
    
    # 时间筛选
    today = datetime(2025, 6, 11)  # 当前日期
    date_range = st.date_input("选择时间范围", 
                              [today - pd.DateOffset(months=6), today])
    
    # 风险阈值设置
    st.subheader("风险阈值配置")
    delay_threshold = st.slider("新品延迟天数阈值", 7, 30, 15)
    qualified_threshold = st.slider("合格率阈值(%)", 70, 95, 85)
    inventory_threshold = st.slider("滞销库存率阈值(%)", 5, 30, 15)

# 生成模拟数据函数
def generate_mock_data():
    # 生成时间序列数据
    dates = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
    
    # 生成部门数据
    data = {
        "日期": np.random.choice(dates, 500),
        "部门": np.random.choice(["项目部", "产品部", "采购部", "品质部", "数据部", "仓库部", "物流部"], 500),
        "项目负责人": np.random.choice(["张明", "李燕燕", "啊飞", "赵华", "刘伟"], 500),
        "新品开发延迟天数": np.random.randint(0, 60, 500),
        "新品开发成功率": np.random.uniform(0.5, 1.0, 500),
        "寻源周期达标率": np.random.uniform(0.6, 0.95, 500),
        "交期达标率": np.random.uniform(0.7, 0.98, 500),
        "一验合格率": np.random.uniform(0.7, 0.97, 500),
        "二验合格率": np.random.uniform(0.75, 0.99, 500),
        "库存周转天数": np.random.randint(30, 180, 500),
        "滞销库存率": np.random.uniform(0.05, 0.35, 500),
        "物流延迟天数": np.random.randint(0, 15, 500)
    }
    
    return pd.DataFrame(data)

# 加载数据
df = generate_mock_data()

# 根据部门筛选数据
if department != "全部":
    df = df[df["部门"] == department]

# 计算关键指标
def calculate_kpis(df):
    kpis = {
        "新品平均延迟天数": df["新品开发延迟天数"].mean(),
        "新品开发成功率": df["新品开发成功率"].mean(),
        "寻源周期达标率": df["寻源周期达标率"].mean(),
        "一验合格率": df["一验合格率"].mean(),
        "库存周转天数": df["库存周转天数"].mean(),
        "滞销库存率": df["滞销库存率"].mean(),
        "物流延迟天数": df["物流延迟天数"].mean()
    }
    return kpis

# 风险预警函数
def risk_alerts(kpis):
    alerts = []
    
    if kpis["新品平均延迟天数"] > delay_threshold:
        alerts.append(f"🚨 新品平均延迟天数({kpis['新品平均延迟天数']:.1f}天)超过阈值({delay_threshold}天)")
    
    if kpis["新品开发成功率"] * 100 < qualified_threshold:
        alerts.append(f"⚠️ 新品开发成功率({kpis['新品开发成功率']*100:.1f}%)低于阈值({qualified_threshold}%)")
    
    if kpis["一验合格率"] * 100 < qualified_threshold:
        alerts.append(f"⚠️ 一验合格率({kpis['一验合格率']*100:.1f}%)低于阈值({qualified_threshold}%)")
    
    if kpis["滞销库存率"] * 100 > inventory_threshold:
        alerts.append(f"🚨 滞销库存率({kpis['滞销库存率']*100:.1f}%)超过阈值({inventory_threshold}%)")
    
    return alerts

# 显示KPI指标
kpis = calculate_kpis(df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("新品平均延迟天数", f"{kpis['新品平均延迟天数']:.1f}天", 
           delta_color="inverse", delta=f"{delay_threshold}天阈值")
col2.metric("新品开发成功率", f"{kpis['新品开发成功率']*100:.1f}%", 
           delta_color="inverse", delta=f"{qualified_threshold}%阈值")
col3.metric("一验合格率", f"{kpis['一验合格率']*100:.1f}%", 
           delta_color="inverse", delta=f"{qualified_threshold}%阈值")
col4.metric("滞销库存率", f"{kpis['滞销库存率']*100:.1f}%", 
           delta_color="inverse", delta=f"{inventory_threshold}%阈值")

# 显示风险预警
st.subheader("风险预警")
alerts = risk_alerts(kpis)
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("当前无高风险预警")

# 部门指标可视化
st.subheader(f"{department}核心指标趋势")

# 按日期聚合数据
trend_df = df.groupby("日期").agg({
    "新品开发延迟天数": "mean",
    "新品开发成功率": "mean",
    "寻源周期达标率": "mean",
    "一验合格率": "mean",
    "二验合格率": "mean",
    "库存周转天数": "mean",
    "滞销库存率": "mean",
    "物流延迟天数": "mean"
}).reset_index()

# 绘制趋势图
fig = px.line(trend_df, x="日期", y=trend_df.columns[1:],
              title="核心指标随时间变化趋势",
              labels={"value": "指标值", "variable": "指标"},
              height=500)
st.plotly_chart(fig, use_container_width=True)

# 按负责人展示数据
st.subheader("按负责人分析")
owner = st.selectbox("选择负责人", df["项目负责人"].unique())
owner_df = df[df["项目负责人"] == owner]

# 负责人KPI指标
st.write(f"### {owner}的绩效指标")
owner_kpis = calculate_kpis(owner_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("新品延迟天数", f"{owner_kpis['新品平均延迟天数']:.1f}天")
col2.metric("开发成功率", f"{owner_kpis['新品开发成功率']*100:.1f}%")
col3.metric("一验合格率", f"{owner_kpis['一验合格率']*100:.1f}%")
col4.metric("物流延迟", f"{owner_kpis['物流延迟天数']:.1f}天")

# 负责人项目明细
st.write("#### 项目详情")
st.dataframe(owner_df.sort_values("日期", ascending=False).head(10))

# 问题项目识别
st.subheader("高风险项目识别")
st.write("#### 延迟严重的项目")
delayed_projects = df[df["新品开发延迟天数"] > delay_threshold].sort_values("新品开发延迟天数", ascending=False)
st.dataframe(delayed_projects[["日期", "项目负责人", "新品开发延迟天数"]].head(10))

st.write("#### 合格率低的项目")
low_quality = df[df["一验合格率"] < qualified_threshold/100].sort_values("一验合格率")
st.dataframe(low_quality[["日期", "项目负责人", "一验合格率"]].head(10))

# 数据导出功能
st.sidebar.download_button(
    label="导出当前数据",
    data=df.to_csv().encode('utf-8'),
    file_name=f"风控数据_{department}_{date_range[0]}_{date_range[1]}.csv",
    mime="text/csv"
)
