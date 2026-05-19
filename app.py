from __future__ import annotations

import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from src.audit_logger import read_audit_log, write_audit_event
from src.config import CHANNELS, COUNTRIES, CUSTOMER_SEGMENTS, DEVICE_TYPES, INCOME_BANDS, MERCHANT_CATEGORIES, TENURE_BANDS, TRAVEL_PROFILES
from src.data_generator import default_transaction, generate_transactions
from src.explainability import generate_reason_codes
from src.llm_explainer import generate_explanation_with_optional_claude
from src.model import FraudModel, score_dataset
from src.rai_engine import (
    checks_to_frame,
    compute_fairness_dashboard,
    final_governance_decision,
    mask_sensitive_transaction,
    monitoring_metrics,
    responsible_ai_score,
    run_responsible_ai_checks,
)
from src.ui_components import fraud_gauge, hero, inject_css, metric_card, risk_badge, scorecard_gauge, section_title, style_plotly_chart

st.set_page_config(
    page_title="Responsible AI Banking Control Tower",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


@st.cache_resource(show_spinner=False)
def load_model_and_data():
    df = generate_transactions(n=4500, seed=7)
    model = FraudModel()
    model.train(df)
    scored = score_dataset(model, df.sample(900, random_state=21).reset_index(drop=True))
    return model, df, scored


model, base_df, scored_df = load_model_and_data()

if "transaction" not in st.session_state:
    tx = default_transaction()
    tx["transaction_id"] = "TXN-DEMO-" + str(uuid.uuid4())[:8].upper()
    st.session_state.transaction = tx

hero()

with st.sidebar:
    st.markdown("## 🏦 Demo Control Panel")
    st.caption("Synthetic data only. No real customer information is used.")
    scenario = st.selectbox(
        "Choose demo scenario",
        [
            "High-risk cross-border electronics purchase",
            "Genuine customer travelling abroad",
            "Low-risk domestic grocery purchase",
            "Velocity attack with failed authentication",
            "Manual custom transaction",
        ],
    )

    scenario_map = {
        "High-risk cross-border electronics purchase": {
            "amount_bhd": 1200.0,
            "customer_avg_spend_bhd": 35.0,
            "merchant_category": "Electronics",
            "transaction_hour": 2,
            "country": "UK",
            "device_type": "New Device",
            "channel": "Online",
            "velocity_10m": 4,
            "failed_auth_count": 2,
            "customer_segment": "Affluent",
            "tenure_band": "5+ years",
            "income_band": "Upper Middle",
            "travel_profile": "Occasional International",
        },
        "Genuine customer travelling abroad": {
            "amount_bhd": 380.0,
            "customer_avg_spend_bhd": 220.0,
            "merchant_category": "Travel",
            "transaction_hour": 15,
            "country": "UAE",
            "device_type": "Known Device",
            "channel": "POS",
            "velocity_10m": 1,
            "failed_auth_count": 0,
            "customer_segment": "Premium",
            "tenure_band": "5+ years",
            "income_band": "High",
            "travel_profile": "Frequent International",
        },
        "Low-risk domestic grocery purchase": {
            "amount_bhd": 28.0,
            "customer_avg_spend_bhd": 35.0,
            "merchant_category": "Groceries",
            "transaction_hour": 18,
            "country": "Bahrain",
            "device_type": "Known Device",
            "channel": "POS",
            "velocity_10m": 1,
            "failed_auth_count": 0,
            "customer_segment": "Mass",
            "tenure_band": "2-5 years",
            "income_band": "Middle",
            "travel_profile": "Domestic Mostly",
        },
        "Velocity attack with failed authentication": {
            "amount_bhd": 640.0,
            "customer_avg_spend_bhd": 60.0,
            "merchant_category": "Digital Goods",
            "transaction_hour": 1,
            "country": "Unknown",
            "device_type": "New Device",
            "channel": "Online",
            "velocity_10m": 8,
            "failed_auth_count": 4,
            "customer_segment": "Mass",
            "tenure_band": "6-24 months",
            "income_band": "Middle",
            "travel_profile": "Domestic Mostly",
        },
    }

    if scenario != "Manual custom transaction":
        if st.button("Load selected scenario", use_container_width=True):
            tx = scenario_map[scenario]
            tx["transaction_id"] = "TXN-DEMO-" + str(uuid.uuid4())[:8].upper()
            st.session_state.transaction = tx
            st.rerun()

    st.markdown("---")
    st.markdown("### Boardroom message")
    st.info(
        "This demo shows how a bank governs AI decisions through explainability, fairness checks, privacy masking, human oversight, audit logs, and monitoring."
    )

# Main transaction form
st.markdown("## 1. Transaction Simulator")
st.markdown("Use the simulator to see how a bank applies Responsible AI controls around a fraud model.")

current = st.session_state.transaction
with st.form("transaction_form"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        amount_bhd = st.number_input("Transaction amount (BHD)", min_value=1.0, max_value=5000.0, value=float(current["amount_bhd"]), step=10.0)
        customer_avg_spend_bhd = st.number_input("Customer avg spend (BHD)", min_value=1.0, max_value=3000.0, value=float(current["customer_avg_spend_bhd"]), step=5.0)
        transaction_hour = st.slider("Transaction hour", 0, 23, int(current["transaction_hour"]))
    with c2:
        merchant_category = st.selectbox("Merchant category", MERCHANT_CATEGORIES, index=MERCHANT_CATEGORIES.index(current["merchant_category"]))
        country = st.selectbox("Transaction country", COUNTRIES, index=COUNTRIES.index(current["country"]))
        channel = st.selectbox("Channel", CHANNELS, index=CHANNELS.index(current["channel"]))
    with c3:
        device_type = st.selectbox("Device", DEVICE_TYPES, index=DEVICE_TYPES.index(current["device_type"]))
        velocity_10m = st.slider("Transactions in last 10 minutes", 0, 10, int(current["velocity_10m"]))
        failed_auth_count = st.slider("Failed authentication attempts", 0, 6, int(current["failed_auth_count"]))
    with c4:
        customer_segment = st.selectbox("Customer segment", CUSTOMER_SEGMENTS, index=CUSTOMER_SEGMENTS.index(current["customer_segment"]))
        tenure_band = st.selectbox("Customer tenure", TENURE_BANDS, index=TENURE_BANDS.index(current["tenure_band"]))
        income_band = st.selectbox("Income band", INCOME_BANDS, index=INCOME_BANDS.index(current["income_band"]))
        travel_profile = st.selectbox("Travel profile", TRAVEL_PROFILES, index=TRAVEL_PROFILES.index(current["travel_profile"]))

    submitted = st.form_submit_button("Run Responsible AI Fraud Check", use_container_width=True)

if submitted:
    st.session_state.transaction = {
        "transaction_id": "TXN-DEMO-" + str(uuid.uuid4())[:8].upper(),
        "amount_bhd": amount_bhd,
        "customer_avg_spend_bhd": customer_avg_spend_bhd,
        "merchant_category": merchant_category,
        "transaction_hour": transaction_hour,
        "country": country,
        "device_type": device_type,
        "channel": channel,
        "velocity_10m": velocity_10m,
        "failed_auth_count": failed_auth_count,
        "customer_segment": customer_segment,
        "tenure_band": tenure_band,
        "income_band": income_band,
        "travel_profile": travel_profile,
    }
    current = st.session_state.transaction

transaction = st.session_state.transaction
prediction = model.predict(transaction)
reason_df = generate_reason_codes(transaction)
checks = run_responsible_ai_checks(transaction, prediction, reason_df)
checks_df = checks_to_frame(checks)
fairness_df = compute_fairness_dashboard(scored_df, group_col="travel_profile")
metrics = monitoring_metrics(scored_df)
scorecard = responsible_ai_score(checks, fairness_df, metrics)
readiness_avg = float(scorecard["score"].mean())
governance_decision = final_governance_decision(scorecard)

st.markdown("## 2. AI Fraud Prediction + Governance Result")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    metric_card("Risk Level", risk_badge(prediction.risk_level), "AI-assisted risk classification")
with mc2:
    metric_card("Recommended Action", prediction.recommended_action.split("+")[0].strip(), "Final action still governed")
with mc3:
    metric_card("Human Review", "Required" if prediction.human_review_required else "Not Required", "Based on customer-impact risk")
with mc4:
    metric_card("Governance Decision", governance_decision, "Responsible AI readiness")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🔍 Decision",
        "🧠 Explainability",
        "🛡️ RAI Controls",
        "⚖️ Fairness",
        "👤 Human Review",
        "📜 Audit Log",
        "📈 Monitoring",
    ]
)

with tab1:
    left, right = st.columns([0.95, 1.05])
    with left:
        st.plotly_chart(fraud_gauge(prediction.fraud_score), use_container_width=True)
    with right:
        section_title("Decision package", "The model supports a decision. It does not replace governance.")
        safe_tx = mask_sensitive_transaction(transaction)
        display_df = pd.DataFrame(
            [
                ["Transaction ID", safe_tx.get("transaction_id")],
                ["Masked Card", safe_tx.get("card_number")],
                ["Amount", f"BHD {safe_tx.get('amount_bhd'):,.2f}"],
                ["Country", safe_tx.get("country")],
                ["Merchant", safe_tx.get("merchant_category")],
                ["Channel", safe_tx.get("channel")],
                ["Device", safe_tx.get("device_type")],
                ["Customer tenure", safe_tx.get("tenure_band")],
            ],
            columns=["Field", "Value"],
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.success(f"Recommended action: {prediction.recommended_action}")

with tab2:
    section_title("Explainability panel", "Reason codes help fraud analysts, customer support, auditors, and regulators understand the decision.")
    col_a, col_b = st.columns([1.2, 0.8])
    with col_a:
        st.dataframe(
            reason_df.assign(contribution=lambda d: (d["contribution"] * 100).round(1).astype(str) + "%"),
            use_container_width=True,
            hide_index=True,
        )
    with col_b:
        chart_df = reason_df.copy()
        chart_df["abs_contribution"] = chart_df["contribution"].abs()
        fig = px.bar(
            chart_df,
            x="abs_contribution",
            y="reason",
            orientation="h",
            title="Reason-code contribution",
            labels={"abs_contribution": "Contribution", "reason": ""},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        style_plotly_chart(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    reason_text = reason_df[["reason", "direction", "detail"]].to_string(index=False)
    explanations = generate_explanation_with_optional_claude(transaction, prediction, reason_text)
    st.markdown("#### Business-friendly explanation")
    st.info(explanations["analyst"])
    st.caption(explanations["mode"])

with tab3:
    section_title("Responsible AI control checklist", "This is the difference between an AI model and a bank-ready AI operating model.")
    status_style = {
        "Passed": "✅ Passed",
        "Warning": "⚠️ Warning",
        "Failed": "❌ Failed",
        "Triggered": "👤 Triggered",
    }
    show_checks = checks_df.copy()
    show_checks["status"] = show_checks["status"].map(status_style).fillna(show_checks["status"])
    st.dataframe(show_checks, use_container_width=True, hide_index=True)

    col1, col2 = st.columns([0.8, 1.2])
    with col1:
        st.plotly_chart(scorecard_gauge(readiness_avg), use_container_width=True)
    with col2:
        fig = px.bar(scorecard, x="score", y="dimension", orientation="h", text="score", title="Responsible AI Scorecard")
        fig.update_traces(textposition="outside", textfont={"color": "#111827", "size": 11})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        style_plotly_chart(fig, height=360, xaxis_range=[0, 105])
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    section_title("Bias and fairness monitoring", "Sensitive attributes are not used for scoring. Governance teams may monitor outcomes across approved segments to detect customer harm.")
    group_col = st.selectbox("Monitor fairness by", ["travel_profile", "income_band", "tenure_band", "customer_segment", "country", "channel"], index=0)
    dyn_fairness = compute_fairness_dashboard(scored_df, group_col=group_col)
    show = dyn_fairness.copy()
    for col in ["flag_rate", "false_positive_rate", "true_fraud_detection_rate", "relative_flag_rate"]:
        show[col] = show[col].map(lambda x: f"{x:.2%}" if col != "relative_flag_rate" else f"{x:.2f}x")
    st.dataframe(show, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(dyn_fairness, x="segment", y="false_positive_rate", color="status", title="False positive rate by segment")
        style_plotly_chart(fig, height=370)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(dyn_fairness, x="segment", y="relative_flag_rate", color="status", title="Relative flag rate by segment")
        style_plotly_chart(fig, height=370)
        st.plotly_chart(fig, use_container_width=True)
    st.warning("Workshop talking point: fairness monitoring is a governance control. It should not become a way to use protected attributes for operational decisioning.")

with tab5:
    section_title("Human-in-the-loop review", "High-impact cases should be reviewed, overridden, or escalated with a reason trail.")
    queue = scored_df.sort_values("fraud_score", ascending=False).head(12).copy()
    queue["ai_recommendation"] = queue["fraud_score"].apply(lambda s: model.classify(float(s))[1])
    st.dataframe(
        queue[["transaction_id", "amount_bhd", "merchant_category", "country", "device_type", "fraud_score", "ai_recommendation"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Review current transaction")
    r1, r2 = st.columns([1, 1])
    with r1:
        final_action = st.selectbox(
            "Final human decision",
            [
                prediction.recommended_action,
                "Approve after customer verification",
                "Decline and open fraud case",
                "Temporary hold and escalate to senior analyst",
                "Approve — false positive confirmed",
            ],
        )
        reviewer = st.text_input("Reviewer", value="Fraud Ops Analyst")
    with r2:
        review_reason = st.text_area(
            "Reason for final decision / override",
            value="Decision reviewed using transaction pattern, reason codes, customer history, and Responsible AI controls.",
            height=125,
        )

    if st.button("Write decision to audit log", use_container_width=True):
        summary = "; ".join(reason_df.head(4)["reason"].tolist()) + " | " + review_reason
        write_audit_event(transaction, prediction, summary, final_action, reviewer)
        st.success("Audit event written. Open the Audit Log tab to view the evidence trail.")

with tab6:
    section_title("Audit evidence trail", "The bank should be able to reconstruct what happened, why it happened, who reviewed it, and which model version was used.")
    audit_df = read_audit_log()
    if audit_df.empty:
        st.info("No audit events yet. Go to Human Review and write the current decision to the audit log.")
    else:
        st.dataframe(audit_df.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
        st.download_button(
            "Download audit log CSV",
            data=audit_df.to_csv(index=False).encode("utf-8"),
            file_name="responsible_ai_audit_log.csv",
            mime="text/csv",
            use_container_width=True,
        )

with tab7:
    section_title("Model monitoring dashboard", "Responsible AI continues after deployment through drift, performance, customer harm, and fairness monitoring.")
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        metric_card("Precision", f"{metrics['precision']:.1%}", "Of flagged cases, how many are fraud")
    with n2:
        metric_card("Recall", f"{metrics['recall']:.1%}", "Of fraud cases, how many are caught")
    with n3:
        metric_card("False Positive Rate", f"{metrics['false_positive_rate']:.1%}", "Customer harm proxy")
    with n4:
        metric_card("Analyst Queue", f"{metrics['analyst_queue']:,}", "Cases needing review")

    m1, m2 = st.columns(2)
    with m1:
        fig = px.histogram(scored_df, x="fraud_score", nbins=35, title="Fraud score distribution")
        style_plotly_chart(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
    with m2:
        drift_df = pd.DataFrame(
            {
                "week": ["W-5", "W-4", "W-3", "W-2", "W-1", "Current"],
                "false_positive_rate": [0.061, 0.064, 0.066, 0.071, 0.078, metrics["false_positive_rate"]],
                "customer_complaints": [34, 38, 42, 41, 49, 57],
            }
        )
        fig = px.line(drift_df, x="week", y=["false_positive_rate", "customer_complaints"], markers=True, title="Monitoring trend: false positives and complaints")
        style_plotly_chart(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.error("Example alert: false positives for cross-border frequent travelers should be reviewed if they exceed the bank's governance threshold.")

st.markdown("---")
st.caption(
    "Demo disclaimer: This is a synthetic Responsible AI simulator for education and client workshops. It is not a production banking system, legal opinion, or regulatory certification."
)
