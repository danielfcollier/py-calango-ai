# src/ui/dashboard.py

import pandas as pd
import plotly.express as px

import streamlit as st
from calango.database import InteractionManager

# --- CSS: TEXT CONTRAST FIX ONLY ---
st.markdown(
    """
    <style>
    /* We do NOT touch background-color or border here.
      This allows the native Streamlit theme to style the box.
    */

    /* 1. Force all text inside the select widget to use the Theme's text color */
    div[data-baseweb="select"] * {
        color: var(--text-color) !important;
    }

    /* 2. Ensure the dropdown arrow icon matches the text color */
    div[data-baseweb="select"] svg {
        fill: var(--text-color) !important;
    }

    /* 3. Ensure the 'Choose options' placeholder is fully opaque and visible */
    div[data-baseweb="select"] span {
        opacity: 1 !important;
        color: var(--text-color) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

db = InteractionManager()

st.title("🦎 A Cuca (The Brain)")
st.caption("She sees everything. Track your costs, tokens, and digital memories here.")

history_data = db.history_table.all()

if not history_data:
    st.warning("🦎 The Cuca is hungry! Start chatting to feed her some data.")
    st.stop()

df = pd.DataFrame(history_data)

# --- USAGE DATA NORMALIZATION ---
if "usage" in df.columns:
    df = df.reset_index(drop=True)
    usage_df = pd.json_normalize(df["usage"])

    # Remove overlapping columns to prevent duplicates
    common_cols = [c for c in usage_df.columns if c in df.columns]
    if common_cols:
        df = df.drop(columns=common_cols)

    df = pd.concat([df.drop(["usage"], axis=1), usage_df], axis=1)

    cols_to_fill = [c for c in ["total_tokens", "prompt_tokens", "completion_tokens"] if c in df.columns]
    fill_values = {c: 0 for c in cols_to_fill}
    df = df.fillna(value=fill_values)
else:
    df["total_tokens"] = 0
    df["prompt_tokens"] = 0
    df["completion_tokens"] = 0

# --- TIMESTAMP FORMATTING ---
df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")

col1, col2, col3, col4 = st.columns(4)

total_cost = float(df["cost_usd"].sum()) if "cost_usd" in df.columns else 0.0
total_tokens = int(df["total_tokens"].sum()) if "total_tokens" in df.columns else 0
total_interactions = len(df)
fav_model = df["model"].mode()[0] if "model" in df.columns and not df["model"].empty else "N/A"

col1.metric("Total Treasure ($)", f"${total_cost:.5f}")
col2.metric("Tokens Consumed", f"{total_tokens:,.0f}")
col3.metric("Memories Stored", total_interactions)
col4.metric("Favorite Spirit", fav_model)

st.divider()

c1, c2 = st.columns(2)

THEME_PALETTE = ["#8A2BE2", "#22c55e", "#FACC15", "#DC2626", "#0284C7"]

with c1:
    st.subheader("🏺 Tribute by Model (Cost)")
    if total_cost > 0:
        cost_by_model = df.groupby("model")["cost_usd"].sum().reset_index()
        fig_pie = px.pie(
            cost_by_model,
            values="cost_usd",
            names="model",
            hole=0.4,
            color_discrete_sequence=THEME_PALETTE,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E0E0E0",
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.caption("No tributes paid yet (Cost is $0).")

with c2:
    st.subheader("📈 Activity Flow")
    if not df.empty and "total_tokens" in df.columns:
        daily_usage = df.set_index("timestamp").resample("D")["total_tokens"].sum().reset_index()

        if not daily_usage.empty:
            fig_line = px.bar(
                daily_usage,
                x="timestamp",
                y="total_tokens",
                labels={"total_tokens": "Tokens", "timestamp": "Date"},
                color_discrete_sequence=["#22c55e"],
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E0E0E0",
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.caption("Not enough time has passed.")
    else:
        st.caption("No data available.")

st.subheader("📜 The Cauldron (Logs)")

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    options = df["provider"].unique() if "provider" in df.columns else []
    selected_provider_filter = st.multiselect("Realm (Provider)", options=options)
with filter_col2:
    options = df["model"].unique() if "model" in df.columns else []
    selected_model_filter = st.multiselect("Spirit (Model)", options=options)
with filter_col3:
    options = df["persona"].unique() if "persona" in df.columns else []
    selected_persona_filter = st.multiselect("Identity (Persona)", options=options)

filtered_df = df.copy()
if selected_provider_filter:
    filtered_df = filtered_df[filtered_df["provider"].isin(selected_provider_filter)]
if selected_model_filter:
    filtered_df = filtered_df[filtered_df["model"].isin(selected_model_filter)]
if "persona" in filtered_df.columns and selected_persona_filter:
    filtered_df = filtered_df[filtered_df["persona"].isin(selected_persona_filter)]

filtered_df = filtered_df.sort_values(by="timestamp", ascending=False)

# --- TABLE COLUMNS CONFIGURATION ---
cols_to_show = [
    "timestamp",
    "provider",
    "model",
    "persona",
    "total_tokens",
    "prompt_tokens",
    "completion_tokens",
    "cost_usd",
]

display_df = filtered_df[[c for c in cols_to_show if c in filtered_df.columns]]

st.dataframe(
    display_df,
    use_container_width=True,
    column_config={
        "timestamp": st.column_config.DatetimeColumn("Time", format="YYYY-MM-DD HH:mm:ss"),
        "cost_usd": st.column_config.NumberColumn("Cost", format="$%.5f"),
        "total_tokens": st.column_config.NumberColumn("Total"),
        "prompt_tokens": st.column_config.NumberColumn("Input"),
        "completion_tokens": st.column_config.NumberColumn("Output"),
        "persona": "Persona Used",
    },
    height=400,
    hide_index=True,
)
