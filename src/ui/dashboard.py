import pandas as pd
import plotly.express as px
from mystique.database import InteractionManager

import streamlit as st

# Initialize Database Connection
db = InteractionManager()

st.title("🧠 Cerebro: Control Board")

# 1. Fetch Data
history_data = db.history_table.all()

if not history_data:
    st.info("No mission data found. Engage Mystique to generate logs.")
    st.stop()

# 2. Preprocess Data
df = pd.DataFrame(history_data)

# Flatten the 'usage' dictionary into separate columns
usage_df = pd.json_normalize(df["usage"])
df = pd.concat([df.drop(["usage"], axis=1), usage_df], axis=1)

# Convert timestamp to datetime objects
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 3. KPI Metrics (The "Heads Up Display")
col1, col2, col3, col4 = st.columns(4)

total_cost = df["cost_usd"].sum()
total_tokens = df["total_tokens"].sum()
total_interactions = len(df)
# Calculate favorite model safely
fav_model = df["model"].mode()[0] if not df["model"].empty else "N/A"

col1.metric("Total Spend", f"${total_cost:.5f}")
col2.metric("Total Tokens", f"{total_tokens:,}")
col3.metric("Interactions", total_interactions)
col4.metric("Favorite Model", fav_model)

st.divider()

# 4. Interactive Visualizations
c1, c2 = st.columns(2)

with c1:
    st.subheader("💰 Spend by Model")
    if total_cost > 0:
        cost_by_model = df.groupby("model")["cost_usd"].sum().reset_index()
        fig_pie = px.pie(
            cost_by_model,
            values="cost_usd",
            names="model",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Magma,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.caption("No cost data available to display.")

with c2:
    st.subheader("📈 Usage Over Time")
    # Group by Date (Day)
    daily_usage = (
        df.set_index("timestamp").resample("D")["total_tokens"].sum().reset_index()
    )

    if not daily_usage.empty:
        fig_line = px.bar(
            daily_usage,
            x="timestamp",
            y="total_tokens",
            labels={"total_tokens": "Tokens Consumed", "timestamp": "Date"},
            color_discrete_sequence=["#4B0082"],  # Indigo
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.caption("Not enough data for time series.")

# 5. Detailed Mission Logs
st.subheader("🗂️ Mission Logs")

# Filter options
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_provider_filter = st.multiselect(
        "Filter by Provider", options=df["provider"].unique()
    )
with filter_col2:
    selected_model_filter = st.multiselect(
        "Filter by Model", options=df["model"].unique()
    )

filtered_df = df.copy()
if selected_provider_filter:
    filtered_df = filtered_df[filtered_df["provider"].isin(selected_provider_filter)]
if selected_model_filter:
    filtered_df = filtered_df[filtered_df["model"].isin(selected_model_filter)]

# Display table
st.dataframe(
    filtered_df[
        ["timestamp", "provider", "model", "total_tokens", "cost_usd", "messages"]
    ],
    use_container_width=True,
    column_config={
        "timestamp": st.column_config.DatetimeColumn(
            "Time", format="D MMM YYYY, h:mm a"
        ),
        "cost_usd": st.column_config.NumberColumn("Cost ($)", format="$%.5f"),
        "messages": "Context",  # Rename column for display
    },
    height=400,
)
