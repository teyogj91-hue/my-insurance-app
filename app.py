import streamlit as st
import json

# 页面基础配置
st.set_page_config(page_title="大东方保单精算与分析系统", page_icon="📋", layout="wide")

st.title("📋 大东方保单精算与分析系统 (Policy Summary Generator)")
st.markdown("填入投保方案数据，一键生成结构化的专业保单分析报告与 XML 结构化数据。")

# 侧边栏：基础产品选择
st.sidebar.header("1. 产品选择")
basic_plan = st.sidebar.selectbox("主险方案 (Basic Plan)", ["SPJ", "SPY", "SRM"], help="SPJ: SmartProtect Junior | SPY: SmartProtect Junior & You | SRM: Smart Revive Max")

# 主界面：分栏填写数据
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 客户基本信息")
    name = st.text_input("客户姓名", "张三")
    dob = st.date_input("出生日期 (DOB)").strftime("%Y-%m-%d")
    anb = st.number_input("下个生日年龄 (ANB)", min_value=0, max_value=99, value=30)
    gender = st.selectbox("性别", ["男 Male", "女 Female"])
    smoker = st.selectbox("吸烟状况", ["不吸烟 Non-smoker", "吸烟 Smoker"])
    occ_class = st.selectbox("职业等级 (Class)", [1, 3, 4])
    notes = st.text_area("备注信息", "配置基础保障与医疗方案")

    st.subheader("🛡️ 主险保障详情")
    sum_assured = st.number_input("基本保额 (BSA, RM)", min_value=0, value=100000, step=10000)
    
    if basic_plan in ["SPJ", "SPY"]:
        premium_term = st.number_input("供期 (年)", min_value=1, value=20)
        monthly_premium = st.number_input("主险月缴保费 (RM)", min_value=0.0, value=150.0)
        srm_coverage_term = 0
        srm_ppt = 0
        srm_annual_premium = 0.0
    else:  # SRM
        srm_coverage_term = st.selectbox("保障至 ANB 岁数", [70, 80, 90])
        srm_ppt = st.selectbox("供期年数 (PPT)", [5, 10, 20])
        srm_annual_premium = st.number_input("SRM 年缴保费 (RM)", min_value=0.0, value=2400.0)
        monthly_premium = srm_annual_premium / 12.0
        premium_term = srm_ppt

    st.subheader("👶 母婴保障 (Baby Shield Plus)")
    baby_tier = st.selectbox("保障级别", ["None", "E", "S", "G"])
    baby_monthly_premium = st.number_input("母婴附加险月缴保费 (RM)", min_value=0.0, value=0.0)

with col2:
    st.subheader("🏥 严重疾病保障 (Critical Illness)")
    ci50_enabled = st.checkbox("启用 50种重疾 (CI 50)", value=True)
    ci50_sa = st.number_input("CI 50 保额 (RM)", min_value=0, value=100000) if ci50_enabled else 0
    ci50_premium = st.number_input("CI 50 月保费 (RM)", min_value=0.0, value=50.0) if ci50_enabled else 0.0

    sep_enabled = st.checkbox("启用 精明早期预支 (Smart Early Payout)", value=False)
    sep_sa = st.number_input("精明早期保额 (RM)", min_value=0, value=0) if sep_enabled else 0
    sep_premium = st.number_input("精明早期月保费 (RM)", min_value=0.0, value=0.0) if sep_enabled else 0.0

    smcc_enabled = st.checkbox("启用 多重重疾 (Smart Multi Critical Care)", value=False)
    smcc_sa = st.number_input("多重重疾 RSA 保额 (RM)", min_value=0, value=0) if smcc_enabled else 0
    smcc_premium = st.number_input("多重重疾月保费 (RM)", min_value=0.0, value=0.0) if smcc_enabled else 0.0

    st.subheader("🚑 医疗卡 (Medical Card)")
    med_plan = st.selectbox("计划类型", ["None", "SMS150", "SMS250", "SMS400", "GMS150", "SHP200", "SHP300", "GMV"], index=7)
    med_deductible = st.selectbox("自付额 (Deductible, RM)", [500, 2500, 5000, 20000, "20000R"])
    med_extender = st.checkbox("包含 Plus Extender", value=False)
    med_premium = st.number_input("医疗卡月保费 (RM)", min_value=0.0, value=120.0)

    st.subheader("💼 其他附加险 & 保费豁免")
    acc_enabled = st.checkbox("意外保障 (CAB Xtra)", value=True)
    acc_sa = st.number_input("意外保额 (RM)", min_value=0, value=100000) if acc_enabled else 0
    acc_premium = st.number_input("意外月保费 (RM)", min_value=0.0, value=20.0) if acc_enabled else 0.0

    st.markdown("**豁免权益 (Waiver Benefits)**")
    w_la_ci = st.checkbox("受保人 50种重疾豁免", value=True)
    w_la_tpd = st.checkbox("受保人 TPD 豁免", value=True)
    w_payer_ci = st.checkbox("付款人 50种重疾豁免", value=False)
    w_payer_tpd = st.checkbox("付款人 TPD/身故豁免", value=False)
    waiver_premium = st.number_input("豁免附加险月保费 (RM)", min_value=0.0, value=15.0)

# 计算总月缴保费
total_monthly_premium = monthly_premium + baby_monthly_premium + ci50_premium + sep_premium + smcc_premium + acc_premium + waiver_premium + med_premium

st.divider()

# 数据汇总提交与生成 XML
if st.button("🚀 生成保单分析 XML 与数据摘要", type="primary", use_container_width=True):
    xml_output = f"""<input>
  <product_selection>
    <basic_plan>{basic_plan}</basic_plan>
  </product_selection>

  <customer_info>
    <name>{name}</name>
    <dob>{dob}</dob>
    <anb>{anb}</anb>
    <gender>{gender}</gender>
    <smoker>{smoker}</smoker>
    <occ_class>{occ_class}</occ_class>
    <notes>{notes}</notes>
  </customer_info>

  <basic_plan_details>
    <sum_assured>{sum_assured}</sum_assured>
    <premium_term>{premium_term}</premium_term>
    <monthly_premium>{monthly_premium:.2f}</monthly_premium>
    <srm_coverage_term>{srm_coverage_term}</srm_coverage_term>
    <srm_ppt>{srm_ppt}</srm_ppt>
    <srm_annual_premium>{srm_annual_premium:.2f}</srm_annual_premium>
  </basic_plan_details>

  <baby_shield_plus_rider>
    <tier>{baby_tier}</tier>
    <monthly_premium>{baby_monthly_premium:.2f}</monthly_premium>
  </baby_shield_plus_rider>

  <critical_illness_riders>
    <ci_50>
      <enabled>{str(ci50_enabled).lower()}</enabled>
      <sum_assured>{ci50_sa}</sum_assured>
      <monthly_premium>{ci50_premium:.2f}</monthly_premium>
    </ci_50>
    <smart_early_payout>
      <enabled>{str(sep_enabled).lower()}</enabled>
      <sum_assured>{sep_sa}</sum_assured>
      <monthly_premium>{sep_premium:.2f}</monthly_premium>
    </smart_early_payout>
    <smart_multi_critical_care>
      <enabled>{str(smcc_enabled).lower()}</enabled>
      <rsa_sum_assured>{smcc_sa}</rsa_sum_assured>
      <monthly_premium>{smcc_premium:.2f}</monthly_premium>
    </smart_multi_critical_care>
  </critical_illness_riders>

  <other_riders>
    <hospital_benefit>
      <enabled>false</enabled>
      <daily_cash>0</daily_cash>
      <monthly_premium>0</monthly_premium>
    </hospital_benefit>
    <cab_xtra_accident>
      <enabled>{str(acc_enabled).lower()}</enabled>
      <sum_assured>{acc_sa}</sum_assured>
      <monthly_premium>{acc_premium:.2f}</monthly_premium>
    </cab_xtra_accident>
    <waiver_benefits>
      <life_assured_50ci_waiver>{str(w_la_ci).lower()}</life_assured_50ci_waiver>
      <life_assured_tpd_waiver>{str(w_la_tpd).lower()}</life_assured_tpd_waiver>
      <payer_50ci_waiver>{str(w_payer_ci).lower()}</payer_50ci_waiver>
      <payer_tpd_death_waiver>{str(w_payer_tpd).lower()}</payer_tpd_death_waiver>
      <monthly_premium>{waiver_premium:.2f}</monthly_premium>
    </waiver_benefits>
  </other_riders>

  <medical_card>
    <plan_type>{med_plan}</plan_type>
    <deductible>{med_deductible}</deductible>
    <has_plus_extender>{str(med_extender).lower()}</has_plus_extender>
    <monthly_premium>{med_premium:.2f}</monthly_premium>
  </medical_card>
</input>"""

    st.success(f"计算成功！预计总月缴保费：RM {total_monthly_premium:.2f} (折算年缴约 RM {total_monthly_premium*12:.2f})")
    
    st.subheader("生成的 XML 参数文本")
    st.code(xml_output, language="xml")
    st.info("提示：您可以直接复制上方的 XML 代码输入给 AI 助手，以即时生成排版完美的保单分析报告。")
