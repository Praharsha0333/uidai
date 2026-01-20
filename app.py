import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="UIDAI Strategic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .metric-card {
        background-color: #262730;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 8px;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("aadhaar_dashboard_data.csv")
        
        # 🧹 CLEAN STATE NAMES
        df['state'] = df['state'].astype(str).str.strip().str.title()
        state_corrections = {
            'Westbengal': 'West Bengal', 'West Bangal': 'West Bengal', 'Westbenga': 'West Bengal',
            'Telengana': 'Telangana', 'Orissa': 'Odisha', 'Chattisgarh': 'Chhattisgarh',
            'Jammu And Kashmir': 'Jammu & Kashmir', 'Daman And Diu': 'Daman & Diu',
            'Dadra And Nagar Haveli': 'Dadra & Nagar Haveli'
        }
        df['state'] = df['state'].replace(state_corrections)
        return df
    except FileNotFoundError:
        st.error("Data file not found! Run the Notebook Export step first.")
        st.stop()

df = load_data()

# --- SIDEBAR COMMAND CENTER ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=150)
st.sidebar.title("Command Center")

# 1. Region Filter
selected_state = st.sidebar.selectbox("Filter by Region", ["All India"] + sorted(df['state'].unique().tolist()))

# Filter Logic
if selected_state != "All India":
    dashboard_df = df[df['state'] == selected_state].copy()
else:
    dashboard_df = df.copy()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Policy Simulator")

# 2. SIMULATION MODE SELECTOR
sim_mode = st.sidebar.radio("Simulation Goal:", ["🔴 Stress Test (Break It)", "🟢 Deploy Solutions (Fix It)"])

if sim_mode == "🔴 Stress Test (Break It)":
    # --- STRESS TEST MODE (The "Collapse" Alert) ---
    load_multiplier = st.sidebar.slider("Update Load Multiplier", 1.0, 5.0, 1.0, help="Simulate a surge in update requests (e.g., new government mandate).")
    
    if load_multiplier > 1.0:
        # Increase Stress
        dashboard_df['assi'] = dashboard_df['assi'] * load_multiplier
        
        # Count Collapsed Districts (Stress > 5.0 is a crash)
        collapsed_count = dashboard_df[dashboard_df['assi'] > 5.0].shape[0]
        
        # DISPLAY THE RED ALERT
        st.sidebar.error(f"⚠️ **ALERT:** {collapsed_count} Districts COLLAPSE at {load_multiplier}x Load!")
    else:
        st.sidebar.info("Increase load to test system resilience.")

else:
    # --- SOLUTION MODE (Deploy Kits) ---
    new_kits = st.sidebar.slider("Deploy New Kits (Per District)", 0, 50, 0)
    staff_boost = st.sidebar.slider("Increase Staff Efficiency", 0, 100, 0, format="%d%%")
    
    if new_kits > 0 or staff_boost > 0:
        # Calculate Impact (Capped at 90% to prevent crash)
        impact = min((new_kits * 0.02) + (staff_boost * 0.01), 0.90)
        
        # Reduce Stress
        dashboard_df['assi'] = (dashboard_df['assi'] * (1 - impact)).clip(lower=0.1)
        
        st.sidebar.success(f"✅ **SUCCESS:** System Stress reduced by {impact:.0%}")
    else:
        st.sidebar.info("Deploy resources to fix the system.")

# --- MAIN PAGE ---
st.title("Aadhaar Strategic Resilience System")
st.markdown(f"**System Intelligence Level 4:** Prescriptive Strategy & Anomaly Detection | Region: **{selected_state}**")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Executive Overview", "The Sentinel (AI)", "District Deep-Dive", "Strategic Execution Board"])

# --- TAB 1: OVERVIEW ---
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    # Recalculate metrics based on simulation
    critical_count = dashboard_df[dashboard_df['Priority'] == 'CRITICAL'].shape[0]
    median_stress = dashboard_df['assi'].median() # This changes with the simulator!
    mbu_total = dashboard_df['future_mbu_demand'].sum()
    security_alerts = dashboard_df[dashboard_df['security_status'] != 'Normal'].shape[0]

    c1.metric("Critical Hotspots", critical_count, "Require Intervention", delta_color="inverse")
    c2.metric("Median System Stress", f"{median_stress:.2f}", "Updates per Enrolment")
    c3.metric("MBU Storm Forecast", f"{mbu_total:,.0f}", "Children turning 5")
    c4.metric("Sentinel Alerts", security_alerts, "Anomalies Detected", delta_color="inverse")

    st.markdown("---")
    vc1, vc2 = st.columns([2, 1])
    
    with vc1:
        st.subheader("The Sentinel: Anomaly Detection Radar")
        fig_scatter = px.scatter(
            dashboard_df, x="assi_acceleration", y="age_18_greater", 
            color="security_status", size="assi", hover_name="district",
            color_discrete_map={"Normal": "#00CC96", "Sentinel Alert: Audit Required": "#FF4B4B"},
            title="Red Dots = Suspicious Adult Enrolment Spikes"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with vc2:
        st.subheader("Stress Zone Distribution")
        if 'district_type' not in dashboard_df.columns: dashboard_df['district_type'] = 'Unknown'
        fig_pie = px.pie(dashboard_df, names='district_type', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: SENTINEL ---
with tab2:
    st.subheader("Security Operations Center")
    st.markdown("AI-detected anomalies indicating potential document fraud or illegal migration patterns.")
    sentinel_data = dashboard_df[dashboard_df['security_status'] != 'Normal'].sort_values('assi', ascending=False)
    if not sentinel_data.empty:
        cols = ['state', 'district', 'assi', 'age_18_greater', 'District_Playbook']
        valid_cols = [c for c in cols if c in sentinel_data.columns]
        st.dataframe(sentinel_data[valid_cols], use_container_width=True)
    else:
        st.success("No Security Anomalies Detected.")

# --- TAB 3: DEEP DIVE ---
with tab3:
    c_search, c_info = st.columns([1, 2])
    with c_search:
        st.markdown("### Search District")
        dist_list = dashboard_df['district'].unique()
        if len(dist_list) > 0:
            sel_dist = st.selectbox("Select District", sorted(dist_list))
            d_data = dashboard_df[dashboard_df['district'] == sel_dist].iloc[0]
        else:
            st.warning("No districts found.")
            st.stop()
    
    with c_info:
        st.markdown(f"## {d_data['district']}, {d_data['state']}")
        priority = d_data.get('Priority', 'Normal')
        if priority == 'CRITICAL': st.error(f"PRIORITY STATUS: {priority}")
        elif priority == 'High': st.warning(f"PRIORITY STATUS: {priority}")
        else: st.success(f"PRIORITY STATUS: {priority}")
            
        m1, m2 = st.columns(2)
        score = d_data.get('Preparedness_Index', 0)
        color = "#00CC96"
        if score < 40: color = "#FF4B4B"
        elif score < 70: color = "#FFA500"
            
        m1.markdown("Preparedness Index")
        m1.markdown(f"<h1 style='color:{color}'>{score:.1f}/100</h1>", unsafe_allow_html=True)
        m2.metric("Projected Biometric Updates", f"{int(d_data['future_mbu_demand']):,}")
        st.info(f"**OFFICIAL ORDER:** {d_data.get('District_Playbook', 'Maintain Operations')}")
        st.caption("Current Stress Level vs. Capacity")
        st.progress(min(d_data['assi'] / 5.0, 1.0))

# --- TAB 4: ACTION BOARD ---
with tab4:
    st.markdown("## Strategic Execution Board")
    st.subheader("Priority Intervention Zones (Top 20 Vulnerable Districts)")
    
    if 'Preparedness_Index' in dashboard_df.columns:
        chart_data = dashboard_df.sort_values('Preparedness_Index', ascending=True).head(20).copy()
        chart_data['Label'] = chart_data['district'] + ", " + chart_data['state']
        def get_color(score):
            if score < 40: return '#8b0000'
            elif score < 50: return '#d63031'
            return '#fdcb6e'

        chart_data['Color'] = chart_data['Preparedness_Index'].apply(get_color)
        fig = px.bar(chart_data, x='Preparedness_Index', y='Label', orientation='h', text='Preparedness_Index', title="Lowest Preparedness Scores")
        fig.update_traces(marker_color=chart_data['Color'], texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="Preparedness Score (0-100)", height=600)
        fig.add_vline(x=50, line_width=2, line_dash="dash", line_color="white", annotation_text="Failure Threshold (50)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Detailed Deployment Schedule")
    action_plan = dashboard_df[dashboard_df['Priority'].isin(['CRITICAL', 'High'])].copy()
    if 'Preparedness_Index' in action_plan.columns:
        action_plan = action_plan.sort_values('Preparedness_Index', ascending=True)
    cols_table = ['state', 'district', 'Priority', 'assi', 'future_mbu_demand', 'District_Playbook', 'Preparedness_Index']
    valid_cols_table = [c for c in cols_table if c in action_plan.columns]
    st.dataframe(action_plan[valid_cols_table], use_container_width=True, hide_index=True, height=500)
    csv = action_plan.to_csv(index=False).encode('utf-8')
    st.download_button("Download Official Orders (CSV)", data=csv, file_name="UIDAI_Orders_2026.csv", mime="text/csv", type="primary")