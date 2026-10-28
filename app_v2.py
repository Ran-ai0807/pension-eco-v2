import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="养老生态全链条评估沙盘 V2", layout="wide")

st.title("养老生态全链条评估沙盘 (V2 升级版)")
st.caption("金融 · 健康 · 情感 三维联动 | 仅用于学术演示，不构成投资建议")

with st.sidebar:
    st.header("1. 选择评估模式")
    mode = st.radio("面向人群", ["年轻预备役（积累期）", "银发一族（消耗期）"])
    
    st.header("2. 老人档案")
    if mode == "年轻预备役（积累期）":
        age = st.slider("当前年龄", 22, 50, 30)
        gender = st.selectbox("性别", ["男", "女"])
        savings = st.number_input("当前养老储备（万元）", 0, 500, 20)
        monthly_income = st.number_input("预计退休后月收入（元）", 2000, 20000, 6000)
        monthly_spend = st.number_input("预计退休后月支出（元）", 2000, 20000, 5000)
        health = st.select_slider("家族健康预期", ["较差", "一般", "良好"], value="良好")
        lonely = st.selectbox("未来陪伴情况", ["独居", "偶尔探望", "家人陪伴"])
    else:
        age = st.slider("当前年龄", 60, 85, 65)
        gender = st.selectbox("性别", ["男", "女"])
        savings = st.number_input("当前养老储备（万元）", 10, 500, 80)
        monthly_income = st.number_input("每月退休金（元）", 2000, 20000, 5000)
        monthly_spend = st.number_input("当前每月支出（元）", 2000, 20000, 4500)
        health = st.select_slider("当前健康自评", ["较差", "一般", "良好"], value="一般")
        lonely = st.selectbox("日常陪伴情况", ["独居，很少与人交流", "偶尔有人探望", "家人日常陪伴"])
        
    run = st.button("生成生态评估", type="primary")

def mock_finance_audit(gender, savings, age):
    base_eq = 40 if mode == "年轻预备役（积累期）" else 20
    if gender == "女":
        base_eq -= 5
    warning_msg = ""
    if mode == "年轻预备役（积累期）":
        warning_msg = "【算法审计预警】参考NBER研究：AI倾向于给女性更低的权益配置。若长期持有低收益资产，60岁时财富可能缩水约6%-10%。"
    else:
        warning_msg = "【算法审计预警】参考Earnest案：AI可能基于历史数据产生歧视。请务必人工复核，警惕‘报喜不报忧’的隐藏条款。"
    return {
        "建议权益比例": f"{base_eq}%",
        "建议固收比例": f"{100 - base_eq}%",
        "审计警报": warning_msg,
    }

def mock_health_audit(age, health):
    score = {"较差": 30, "一般": 60, "良好": 85}[health] - max(0, (age - 65)) * 1.0
    score = max(0, min(100, score))
    level = "高" if score < 40 else ("中" if score < 70 else "低")
    advice = "建议接入智能监护设备（防跌倒），并在合同中明确AI决策不能作为拒赔唯一依据。" if level == "高" else "维持现有健康管理节奏。"
    return {"健康风险分": f"{score:.0f}/100", "风险等级": level, "健康建议": advice}

def mock_emotion_audit(lonely):
    if "独居" in lonely:
        return "强", "【防幻觉预警】AI陪伴虽好，但警惕近期‘AI乱给打赏码’事件，涉及资金支付必须人工介入。"
    elif "偶尔" in lonely:
        return "中", "可使用AI语音助手辅助用药提醒。"
    else:
        return "弱", "重点关注防诈骗风险。"

if run:
    fin = mock_finance_audit(gender, savings, age)
    hea = mock_health_audit(age, health)
    emo_level, emo_advice = mock_emotion_audit(lonely)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("金融链：AI配置与审计")
        st.metric("建议权益类比例", fin["建议权益比例"])
        st.metric("建议固收类比例", fin["建议固收比例"])
        st.error(fin["审计警报"])

    with col2:
        st.subheader("健康链：风险前置")
        st.metric("健康风险分", hea["健康风险分"])
        st.metric("综合风险等级", hea["风险等级"])
        st.info(hea["健康建议"])

    with col3:
        st.subheader("情感链：陪伴与安全")
        st.metric("陪伴需求强度", emo_level)
        st.warning(emo_advice)

    st.divider()

    st.subheader("生态健康度与长寿风险总览")
    
    fin_score = int(fin["建议权益比例"].strip("%")) * 2
    hea_score = int(hea["健康风险分"].split("/")[0])
    emo_score = {"强": 30, "中": 65, "弱": 90}[emo_level]

    radar = go.Figure(data=go.Scatterpolar(
        r=[fin_score, hea_score, emo_score, fin_score],
        theta=["金融稳健度", "健康安全度", "情感满足度", "金融稳健度"],
        fill="toself",
    ))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350)
    st.plotly_chart(radar, use_container_width=True)

    st.subheader("养老金耗尽年龄模拟（基于你输入的月支出）")
    np.random.seed(42)
    n_sim = 500
    annual_spend = monthly_spend * 12
    annual_income = monthly_income * 12
    net_withdraw = max(0, annual_spend - annual_income)
    
    returns = np.random.normal(0.04, 0.08, (n_sim, 40))
    balances = np.zeros((n_sim, 41))
    balances[:, 0] = savings * 10000
    
    for t in range(1, 41):
        withdraw = net_withdraw * (1.03 ** (t - 1))
        balances[:, t] = balances[:, t-1] * (1 + returns[:, t-1]) - withdraw
        balances[:, t] = np.maximum(balances[:, t], 0)
        
    depletion = []
    for i in range(n_sim):
        zero = np.where(balances[i] <= 0)[0]
        depletion.append(age + (zero[0] if len(zero) > 0 else 40))
        
    fig = px.histogram(x=depletion, nbins=20, labels={"x": "资金耗尽年龄", "y": "模拟频次"})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"数据解读：每月缺口 {net_withdraw} 元，在500次模拟中，养老金中位数在 {int(np.median(depletion))} 岁耗尽。")

else:
    st.info("请在左侧选择人群模式、填写档案后，点击「生成生态评估」。")