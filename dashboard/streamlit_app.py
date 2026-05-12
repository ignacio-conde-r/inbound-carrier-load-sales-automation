import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(page_title="HappyRobot Carrier Sales", page_icon="🚛", layout="wide")
st.title("🚛 HappyRobot Inbound Carrier Sales — Operations Dashboard")
st.caption(f"Live data from backend API · Refreshed at {datetime.now().strftime('%H:%M:%S')}")


@st.cache_data(ttl=30)
def fetch(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


summary = fetch("/metrics/summary")
calls = fetch("/metrics/calls")
negotiations = fetch("/metrics/negotiations")

if summary:
    st.subheader("📊 Key Performance Indicators")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Calls", summary["total_calls"])
    c2.metric("Booked", summary["booked"])
    c3.metric("Booking Rate", f"{summary['booking_rate']*100:.1f}%")
    c4.metric("Ineligible Carriers", summary["ineligible"])
    c5.metric("No Match", summary["no_match"])
    c6.metric("Price Rejected", summary["price_rejected"])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        avg_p = f"${summary['avg_agreed_price']:,.2f}" if summary.get('avg_agreed_price') else "N/A"
        avg_r = f"{summary['avg_negotiation_rounds']:.1f}" if summary.get('avg_negotiation_rounds') else "N/A"
        st.metric("Avg Agreed Price", avg_p)
        st.metric("Avg Negotiation Rounds", avg_r)
    with col2:
        pos = summary.get("positive_sentiment", 0)
        neg = summary.get("negative_sentiment", 0)
        total = summary.get("total_calls", 0)
        neutral = max(0, total - pos - neg)
        if total > 0:
            import plotly.graph_objects as go
            fig = go.Figure(go.Pie(
                labels=["Positive", "Neutral", "Negative"],
                values=[pos, neutral, neg],
                hole=0.4,
                marker_colors=["#22c55e", "#94a3b8", "#ef4444"],
            ))
            fig.update_layout(title="Carrier Sentiment", height=280, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)

if calls:
    st.subheader("📞 Recent Calls")
    df = pd.DataFrame(calls)
    if not df.empty:
        # Normalize column names from API
        rename_map = {
            "carrier_mc_number": "carrier_mc",
            "selected_load_id": "load_id",
        }
        df = df.rename(columns=rename_map)

        outcome_colors = {
            "booked": "🟢",
            "carrier_not_eligible": "🔴",
            "no_matching_load": "🟡",
            "price_rejected": "🔴",
            "carrier_not_interested": "🟠",
            "transferred": "🟢",
            "failed": "🔴",
        }
        df["status"] = df["outcome"].map(
            lambda x: f"{outcome_colors.get(x, '⚪')} {x}" if pd.notna(x) else "⚪ unknown"
        )
        sentiment_map = {"positive": "😊", "neutral": "😐", "negative": "😞"}
        df["mood"] = df["sentiment"].map(
            lambda x: sentiment_map.get(x, "❓") if pd.notna(x) else "❓"
        )
        # Format final_offer
        if "final_offer" in df.columns:
            df["final_offer"] = df["final_offer"].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
            )

        display_cols = ["created_at", "carrier_mc", "carrier_name", "load_id", "final_offer", "status", "mood"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], use_container_width=True, hide_index=True)

if negotiations:
    st.subheader("💰 Negotiation Events")
    df_neg = pd.DataFrame(negotiations)
    if not df_neg.empty:
        import plotly.express as px
        decision_counts = df_neg["decision"].value_counts().reset_index()
        decision_counts.columns = ["decision", "count"]
        fig2 = px.bar(
            decision_counts,
            x="decision",
            y="count",
            color="decision",
            color_discrete_map={"accept": "#22c55e", "counter": "#f59e0b", "reject": "#ef4444"},
            title="Negotiation Outcomes by Decision",
        )
        fig2.update_layout(height=300, showlegend=False, margin=dict(t=40, b=0))
        st.plotly_chart(fig2, use_container_width=True)

        # Shorten call_id for display
        df_neg["call_id"] = df_neg["call_id"].apply(
            lambda x: x[:8] + "..." if isinstance(x, str) and len(x) > 8 else x
        )
        st.dataframe(
            df_neg[["call_id", "load_id", "round", "carrier_offer", "counter_offer", "decision"]],
            use_container_width=True,
            hide_index=True,
        )

st.divider()
if st.button("🔄 Refresh data"):
    st.cache_data.clear()
    st.rerun()