import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}

central = pytz.timezone("America/Chicago")
now_ct = datetime.now(central)

st.set_page_config(page_title="HappyRobot Carrier Sales", page_icon="🚛", layout="wide")
st.title("🚛 HappyRobot Inbound Carrier Sales — Operations Dashboard")
st.caption(f"Live data from backend API · Refreshed at {now_ct.strftime('%H:%M:%S')} CT")


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

# ── KPIs ──────────────────────────────────────────────────────────────────────
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

        # Outcome distribution
        if summary["total_calls"] > 0:
            import plotly.express as px
            outcome_data = {
                "Outcome": ["Booked", "Ineligible", "No Match", "Price Rejected"],
                "Count": [
                    summary.get("booked", 0),
                    summary.get("ineligible", 0),
                    summary.get("no_match", 0),
                    summary.get("price_rejected", 0),
                ]
            }
            df_outcomes = pd.DataFrame(outcome_data)
            df_outcomes = df_outcomes[df_outcomes["Count"] > 0]
            if not df_outcomes.empty:
                fig_out = px.bar(
                    df_outcomes,
                    x="Outcome",
                    y="Count",
                    color="Outcome",
                    color_discrete_map={
                        "Booked": "#22c55e",
                        "Ineligible": "#ef4444",
                        "No Match": "#f59e0b",
                        "Price Rejected": "#ef4444",
                    },
                    title="Call Outcome Distribution",
                )
                fig_out.update_layout(height=260, showlegend=False, margin=dict(t=40, b=0))
                st.plotly_chart(fig_out, use_container_width=True)

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

        # Margin saved metric
        if negotiations:
            df_neg_raw = pd.DataFrame(negotiations)
            if not df_neg_raw.empty and "max_authorized_price" in df_neg_raw.columns:
                accepted = df_neg_raw[df_neg_raw["decision"] == "accept"].copy()
                if not accepted.empty:
                    accepted["margin_saved"] = accepted["max_authorized_price"] - accepted["carrier_offer"]
                    total_saved = accepted["margin_saved"].sum()
                    avg_saved = accepted["margin_saved"].mean()
                    ms1, ms2 = st.columns(2)
                    ms1.metric("Total Margin Saved", f"${total_saved:,.0f}")
                    ms2.metric("Avg Margin Saved / Deal", f"${avg_saved:,.0f}")

# ── RECENT CALLS ──────────────────────────────────────────────────────────────
if calls:
    st.subheader("📞 Recent Calls")
    df = pd.DataFrame(calls)
    if not df.empty:
        rename_map = {
            "carrier_mc_number": "carrier_mc",
            "selected_load_id": "load_id",
        }
        df = df.rename(columns=rename_map)

        if "created_at" in df.columns:
            df["created_at"] = (
                pd.to_datetime(df["created_at"], utc=True)
                .dt.tz_convert("America/Chicago")
                .dt.strftime("%Y-%m-%d %H:%M:%S (CT)")
            )

        outcome_labels = {
            "booked": "✅ Booked",
            "carrier_not_eligible": "🚫 Ineligible",
            "no_matching_load": "🔍 No Match",
            "price_rejected": "❌ Price Rejected",
            "carrier_not_interested": "📵 Not Interested",
            "transferred": "↗️ Transferred",
            "failed": "⚠️ Failed",
        }
        df["status"] = df["outcome"].map(
            lambda x: outcome_labels.get(x, f"⚪ {x}") if pd.notna(x) else "⚪ Unknown"
        )

        sentiment_labels = {
            "positive": "Positive",
            "neutral": "Neutral",
            "negative": "Negative",
        }
        df["sentiment_label"] = df["sentiment"].map(
            lambda x: sentiment_labels.get(x, "Unknown") if pd.notna(x) else "Unknown"
        )

        if "final_offer" in df.columns:
            df["final_offer"] = df["final_offer"].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "—"
            )

        display_cols = ["created_at", "carrier_mc", "carrier_name", "load_id", "final_offer", "status", "sentiment_label"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[existing].rename(columns={"sentiment_label": "sentiment"}),
            use_container_width=True,
            hide_index=True
        )

# ── NEGOTIATION EVENTS ────────────────────────────────────────────────────────
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

        df_neg["call_id"] = df_neg["call_id"].apply(
            lambda x: x[:8] + "..." if isinstance(x, str) and len(x) > 8 else x
        )

        display_neg_cols = ["call_id", "load_id", "round", "carrier_offer", "counter_offer", "decision"]
        if "max_authorized_price" in df_neg.columns:
            display_neg_cols.append("max_authorized_price")

        st.dataframe(
            df_neg[[c for c in display_neg_cols if c in df_neg.columns]],
            use_container_width=True,
            hide_index=True,
        )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
col_refresh, col_reset = st.columns([1, 1])

with col_refresh:
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

with col_reset:
    with st.expander("⚠️ Danger Zone"):
        st.warning("This will delete ALL call logs and negotiation events from the database.")
        if st.button("🗑️ Reset Dashboard Data", type="primary"):
            try:
                r = requests.delete(
                    f"{API_BASE}/admin/reset",
                    headers=HEADERS,
                    timeout=5
                )
                if r.status_code == 200:
                    st.success("✅ Data reset successfully.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {r.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")