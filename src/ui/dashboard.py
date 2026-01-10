# src/ui/dashboard.py

import pandas as pd
import plotly.express as px

import streamlit as st
from calango.database import InteractionManager

db = InteractionManager()

st.title("🦎 A Cuca (The Brain)")
st.caption("She sees everything. Track your costs, tokens, and digital memories here.")

history_data = db.history_table.all()

if not history_data:
    st.warning("🦎 The Cuca is hungry! Start chatting to feed her some data.")
    st.stop()

df = pd.DataFrame(history_data)
usage_df = pd.json_normalize(df["usage"])
df = pd.concat([df.drop(["usage"], axis=1), usage_df], axis=1)

# CORREÇÃO: Usar format='mixed' para lidar com os formatos ISO antigo e o novo yyyy-mm-dd HH:mm:ss
df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")

col1, col2, col3, col4 = st.columns(4)

total_cost = df["cost_usd"].sum()
total_tokens = df["total_tokens"].sum()
total_interactions = len(df)
fav_model = df["model"].mode()[0] if not df["model"].empty else "N/A"

col1.metric("Total Treasure ($)", f"${total_cost:.5f}")
col2.metric("Tokens Consumed", f"{total_tokens:,}")
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

st.subheader("📜 The Cauldron (Logs)")

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    selected_provider_filter = st.multiselect("Realm (Provider)", options=df["provider"].unique())
with filter_col2:
    selected_model_filter = st.multiselect("Spirit (Model)", options=df["model"].unique())
with filter_col3:
    # Adicionado filtro de Persona que você implementou anteriormente
    selected_persona_filter = st.multiselect(
        "Identity (Persona)", options=df["persona"].unique() if "persona" in df.columns else []
    )

filtered_df = df.copy()
if selected_provider_filter:
    filtered_df = filtered_df[filtered_df["provider"].isin(selected_provider_filter)]
if selected_model_filter:
    filtered_df = filtered_df[filtered_df["model"].isin(selected_model_filter)]
if "persona" in filtered_df.columns and selected_persona_filter:
    filtered_df = filtered_df[filtered_df["persona"].isin(selected_persona_filter)]

filtered_df = filtered_df.sort_values(by="timestamp", ascending=False)

# Adicionado a coluna "persona" na visualização da tabela
cols_to_show = ["timestamp", "provider", "model", "persona", "total_tokens", "cost_usd", "messages"]
display_df = filtered_df[[c for c in cols_to_show if c in filtered_df.columns]]

st.dataframe(
    display_df,
    use_container_width=True,
    column_config={
        "timestamp": st.column_config.DatetimeColumn("Time", format="YYYY-MM-DD HH:mm:ss"),
        "cost_usd": st.column_config.NumberColumn("Cost", format="$%.5f"),
        "total_tokens": st.column_config.NumberColumn("Tokens"),
        "persona": "Persona Used",
        "messages": "Conversation Context",
    },
    height=400,
    hide_index=True,
)
