import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Operations Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Operations Dashboard")
st.caption("Interactive operational dashboard built with Streamlit + Plotly")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def first_existing(df, names):
    for name in names:
        if name in df.columns:
            return name
    return None

def safe_mean(df, col):
    return df[col].mean() if col and col in df.columns else None

def money(value):
    return f"₹{value:,.0f}" if pd.notna(value) else "N/A"

# ---------------------------------------------------------
# DATA UPLOAD
# ---------------------------------------------------------
st.sidebar.header("📁 Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload your hospital CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info(
        "Upload the master hospital CSV to start. "
        "The dashboard is designed for columns such as "
        "Patient_ID, Department_Patient/Department, Admit_Date/Admission_Date, "
        "Wait_Time_Minutes, Length_of_Stay_Days, Doctor_Name, Hospital_Name, "
        "Hospital_Type and Treatment_Cost_USD."
    )
    st.stop()

df = pd.read_csv(uploaded_file)

# ---------------------------------------------------------
# COLUMN DETECTION
# ---------------------------------------------------------
patient_col = first_existing(df, ["Patient_ID", "PatientId", "PatientID"])
dept_col = first_existing(df, ["Department_Patient", "Department"])
date_col = first_existing(df, ["Admission_Date", "Admit_Date", "Admission Date", "Admit Date"])
discharge_col = first_existing(df, ["Discharge_Date", "Discharge_Time", "Discharge Date"])
wait_col = first_existing(df, ["Wait_Time_Minutes", "Wait_Time", "Waiting_Time_Minutes"])
los_col = first_existing(df, ["Length_of_Stay_Days", "Length_of_Stay", "LOS_Days"])
doctor_col = first_existing(df, ["Doctor_Name", "Doctor"])
doctor_id_col = first_existing(df, ["Doctor_ID", "DoctorId", "DoctorID"])
nurse_id_col = first_existing(df, ["Nurse_ID", "NurseId", "NurseID"])
nurse_col = first_existing(df, ["Nurse_Name", "Nurse", "NurseName"])
staff_id_col = first_existing(df, ["Staff_ID", "StaffId", "StaffID", "Employee_ID", "EmployeeId"])
staff_col = first_existing(df, ["Staff_Name", "Staff", "Employee_Name", "Employee", "StaffName"])
staff_count_col = first_existing(df, ["Total_Staff", "Staff_Count", "Total_Employees", "Employee_Count"])
available_beds_col = first_existing(df, ["Available_Beds", "Beds_Available", "Available_Bed_Count"])
occupied_beds_col = first_existing(df, ["Occupied_Beds", "Beds_Occupied", "Occupied_Bed_Count"])
diagnosis_col = first_existing(df, ["Diagnosis"])
cost_col = first_existing(df, ["Treatment_Cost_INR", "Treatment_Cost_USD", "Treatment_Cost", "Cost"])
hospital_col = first_existing(df, ["Hospital_Name", "Hospital"])
hospital_type_col = first_existing(df, ["Hospital_Type", "Facility_Type"])
beds_col = first_existing(df, ["Total_Beds", "Beds", "Bed_Capacity"])
severity_col = first_existing(df, ["Severity_Level", "Severity"])
outcome_col = first_existing(df, ["Outcome"])
readmission_col = first_existing(df, ["Readmission_Flag", "Readmission_30_Days"])

# Convert dates
if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

if discharge_col:
    df[discharge_col] = pd.to_datetime(df[discharge_col], errors="coerce")

# Numeric conversion
for col in [wait_col, los_col, cost_col, beds_col]:
    if col:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

filtered = df.copy()

if date_col and filtered[date_col].notna().any():
    min_date = filtered[date_col].min().date()
    max_date = filtered[date_col].max().date()

    date_range = st.sidebar.date_input(
        "Admission date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered = filtered[
            (filtered[date_col].dt.date >= date_range[0]) &
            (filtered[date_col].dt.date <= date_range[1])
        ]

if dept_col:
    departments = sorted(filtered[dept_col].dropna().astype(str).unique())
    selected_dept = st.sidebar.multiselect(
        "Department",
        departments,
        default=[]
    )
    if selected_dept:
        filtered = filtered[filtered[dept_col].astype(str).isin(selected_dept)]

if hospital_type_col:
    types = sorted(filtered[hospital_type_col].dropna().astype(str).unique())
    selected_type = st.sidebar.multiselect(
        "Hospital Type",
        types,
        default=[]
    )
    if selected_type:
        filtered = filtered[
            filtered[hospital_type_col].astype(str).isin(selected_type)
        ]

if diagnosis_col:
    diagnoses = sorted(filtered[diagnosis_col].dropna().astype(str).unique())
    selected_diagnosis = st.sidebar.multiselect(
        "Diagnosis",
        diagnoses,
        default=[]
    )
    if selected_diagnosis:
        filtered = filtered[
            filtered[diagnosis_col].astype(str).isin(selected_diagnosis)
        ]

if severity_col:
    severities = sorted(filtered[severity_col].dropna().astype(str).unique())
    selected_severity = st.sidebar.multiselect(
        "Severity",
        severities,
        default=[]
    )
    if selected_severity:
        filtered = filtered[
            filtered[severity_col].astype(str).isin(selected_severity)
        ]

st.sidebar.write(f"**Records after filters:** {len(filtered):,}")
st.sidebar.caption(
    "Use the sections below to move from demand → workforce → beds → department workload → capacity and efficiency."
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------
page = st.sidebar.radio(
    "📌 Analysis Section",
    [
        "🏠 Dashboard Overview",
        "👥 Patient Flow & Outcomes",
        "🏥 Hospital & Facility Analysis",
        "📅 Admission & Demand Trends",
        "🚪 Discharge & Recovery Analysis",
        "📈 Service Demand Analysis",
        "👨‍⚕️ Workforce & Staff Utilization",
        "🛏️ Bed Occupancy Analysis",
        "🏢 Department Workload Analysis",
        "⚠️ Operational Bottlenecks",
        "🎯 Resource Capacity & Efficiency",
        "📏 Benchmark & Utilization Gap",
        "📊 Capacity Trends & Risk",
        "🏆 Hospital Resource Performance"
    ]
)

# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------
if page == "🏠 Dashboard Overview":

    st.subheader("📊 Operational Overview")

    total_patients = (
        filtered[patient_col].nunique()
        if patient_col else len(filtered)
    )

    total_doctors = (
        filtered[doctor_id_col].nunique()
        if doctor_id_col
        else filtered[doctor_col].nunique()
        if doctor_col
        else 0
    )

    avg_wait = safe_mean(filtered, wait_col)
    avg_los = safe_mean(filtered, los_col)
    total_cost = filtered[cost_col].sum() if cost_col else None

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("👥 Patients", f"{total_patients:,}")
    c2.metric("👨‍⚕️ Doctors", f"{total_doctors:,}")
    c3.metric("⏱️ Avg Wait", f"{avg_wait:.1f} min" if avg_wait is not None else "N/A")
    c4.metric("🛏️ Avg LOS", f"{avg_los:.2f} days" if avg_los is not None else "N/A")
    c5.metric("💰 Treatment Cost", money(total_cost) if total_cost is not None else "N/A")

    st.divider()

    col1, col2 = st.columns(2)

    if dept_col:
        dept = filtered[dept_col].value_counts().reset_index()
        dept.columns = ["Department", "Patients"]

        fig = px.bar(
            dept,
            x="Department",
            y="Patients",
            color="Patients",
            title="Patients by Department"
        )
        col1.plotly_chart(fig, use_container_width=True)

    if diagnosis_col:
        diag = filtered[diagnosis_col].value_counts().reset_index()
        diag.columns = ["Diagnosis", "Patients"]

        fig = px.pie(
            diag,
            names="Diagnosis",
            values="Patients",
            hole=0.45,
            title="Diagnosis Distribution"
        )
        col2.plotly_chart(fig, use_container_width=True)

    # Additional Overview plots: treatment outcomes
    if outcome_col:
        st.divider()
        st.subheader("🎯 Treatment Outcome Overview")

        outcome_series = filtered[outcome_col].fillna("Unknown").astype(str).str.strip()
        outcome_counts = outcome_series.value_counts().reset_index()
        outcome_counts.columns = ["Treatment Outcome", "Patients"]

        outcome_colors = {
            "Recovered": "#2E8B57",
            "Improved": "#1E90FF",
            "Transferred": "#FFA500",
            "Deceased": "#DC143C",
            "Unknown": "#808080"
        }

        col3, col4 = st.columns(2)

        fig = px.pie(
            outcome_counts,
            names="Treatment Outcome",
            values="Patients",
            hole=0.5,
            title="Treatment Outcome Distribution",
            color="Treatment Outcome",
            color_discrete_map=outcome_colors
        )
        col3.plotly_chart(fig, use_container_width=True)

        if dept_col:
            outcome_dept = (
                filtered.assign(_Outcome=outcome_series)
                .groupby([dept_col, "_Outcome"])
                .size()
                .reset_index(name="Patients")
            )
            outcome_dept.columns = ["Department", "Treatment Outcome", "Patients"]

            fig = px.bar(
                outcome_dept,
                x="Department",
                y="Patients",
                color="Treatment Outcome",
                barmode="stack",
                title="Treatment Outcomes by Department",
                color_discrete_map=outcome_colors
            )
            fig.update_layout(xaxis_tickangle=-35)
            col4.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PATIENT MOVEMENT
# ---------------------------------------------------------
elif page == "👥 Patient Flow & Outcomes":

    st.subheader("👥 Patient Movement Analysis")

    if dept_col:
        dept = filtered[dept_col].value_counts().reset_index()
        dept.columns = ["Department", "Patients"]

        fig = px.bar(
            dept.sort_values("Patients"),
            x="Patients",
            y="Department",
            orientation="h",
            color="Patients",
            title="Department-wise Patient Count"
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    if wait_col and dept_col:
        wait = (
            filtered.groupby(dept_col)[wait_col]
            .mean()
            .reset_index()
            .sort_values(wait_col, ascending=False)
        )

        fig = px.bar(
            wait,
            x=dept_col,
            y=wait_col,
            color=wait_col,
            title="Average Waiting Time by Department",
            labels={wait_col: "Average Wait (minutes)"}
        )
        col1.plotly_chart(fig, use_container_width=True)

    if los_col and dept_col:
        los = (
            filtered.groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(los_col, ascending=False)
        )

        fig = px.bar(
            los,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Length of Stay by Department"
        )
        col2.plotly_chart(fig, use_container_width=True)

    if diagnosis_col and dept_col:
        cross = (
            filtered.groupby([dept_col, diagnosis_col])
            .size()
            .reset_index(name="Patients")
        )

        fig = px.bar(
            cross,
            x=dept_col,
            y="Patients",
            color=diagnosis_col,
            barmode="stack",
            title="Diagnosis Distribution by Department"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Treatment outcome / recovery status
    if outcome_col:
        st.divider()
        st.subheader("🎯 Treatment Outcome & Recovery Analysis")

        outcome_series = filtered[outcome_col].fillna("Unknown").astype(str).str.strip()
        normalized = outcome_series.str.lower()

        recovered = int((normalized == "recovered").sum())
        improved = int((normalized == "improved").sum())
        transferred = int((normalized == "transferred").sum())
        total_outcomes = len(outcome_series)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("✅ Recovered", f"{recovered:,}")
        k2.metric("📈 Improved", f"{improved:,}")
        k3.metric("🔄 Transferred", f"{transferred:,}")
        k4.metric(
            "📊 Recovered + Improved",
            f"{((recovered + improved) / total_outcomes * 100):.1f}%"
            if total_outcomes else "0.0%"
        )

        outcome_colors = {
            "Recovered": "#2E8B57",
            "Improved": "#1E90FF",
            "Transferred": "#FFA500",
            "Deceased": "#DC143C",
            "Unknown": "#808080"
        }

        col3, col4 = st.columns(2)

        outcome_counts = outcome_series.value_counts().reset_index()
        outcome_counts.columns = ["Treatment Outcome", "Patients"]

        fig = px.bar(
            outcome_counts,
            x="Treatment Outcome",
            y="Patients",
            color="Treatment Outcome",
            title="Treatment Outcome Distribution",
            color_discrete_map=outcome_colors,
            text="Patients"
        )
        fig.update_traces(textposition="outside")
        col3.plotly_chart(fig, use_container_width=True)

        if dept_col:
            outcome_dept = (
                filtered.assign(_Outcome=outcome_series)
                .groupby([dept_col, "_Outcome"])
                .size()
                .reset_index(name="Patients")
            )
            outcome_dept.columns = ["Department", "Treatment Outcome", "Patients"]

            fig = px.bar(
                outcome_dept,
                x="Department",
                y="Patients",
                color="Treatment Outcome",
                barmode="stack",
                title="Recovered / Improved / Transferred by Department",
                color_discrete_map=outcome_colors
            )
            fig.update_layout(xaxis_tickangle=-35)
            col4.plotly_chart(fig, use_container_width=True)

        if date_col:
            temp = filtered.dropna(subset=[date_col]).copy()
            temp["_Outcome"] = outcome_series.loc[temp.index]
            temp["Month"] = temp[date_col].dt.to_period("M").astype(str)
            outcome_monthly = (
                temp.groupby(["Month", "_Outcome"])
                .size()
                .reset_index(name="Patients")
            )

            fig = px.line(
                outcome_monthly,
                x="Month",
                y="Patients",
                color="_Outcome",
                markers=True,
                title="Monthly Treatment Outcome Trend",
                color_discrete_map=outcome_colors
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# TREATMENT FACILITY
# ---------------------------------------------------------
elif page == "🏥 Hospital & Facility Analysis":

    st.subheader("🏥 Treatment Facility Analysis")

    col1, col2 = st.columns(2)

    if hospital_col:
        hospital = (
            filtered[hospital_col]
            .value_counts()
            .reset_index()
            .head(15)
        )
        hospital.columns = ["Hospital", "Patients"]

        fig = px.bar(
            hospital.sort_values("Patients"),
            x="Patients",
            y="Hospital",
            orientation="h",
            color="Patients",
            title="Top Hospitals by Patient Volume"
        )
        col1.plotly_chart(fig, use_container_width=True)

    if hospital_type_col:
        facility = filtered[hospital_type_col].value_counts().reset_index()
        facility.columns = ["Hospital Type", "Patients"]

        fig = px.pie(
            facility,
            names="Hospital Type",
            values="Patients",
            hole=0.45,
            title="Government vs Private"
        )
        col2.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    if dept_col and cost_col:
        cost = (
            filtered.groupby(dept_col)[cost_col]
            .mean()
            .reset_index()
            .sort_values(cost_col, ascending=False)
        )

        fig = px.bar(
            cost,
            x=dept_col,
            y=cost_col,
            color=cost_col,
            title="Average Treatment Cost by Department"
        )
        col1.plotly_chart(fig, use_container_width=True)

    if dept_col and los_col:
        stay = (
            filtered.groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(los_col, ascending=False)
        )

        fig = px.bar(
            stay,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Stay by Department"
        )
        col2.plotly_chart(fig, use_container_width=True)

    if beds_col:
        avg_beds = filtered[beds_col].mean()
        st.metric("🛏️ Average Facility Bed Capacity", f"{avg_beds:,.0f}")

# ---------------------------------------------------------
# ADMISSION TRENDS
# ---------------------------------------------------------
elif page == "📅 Admission & Demand Trends":

    st.subheader("📅 Admission Trend Analysis")

    if not date_col:
        st.warning("No admission date column was found.")
        st.stop()

    daily = (
        filtered.dropna(subset=[date_col])
        .groupby(filtered[date_col].dt.date)
        .size()
        .reset_index(name="Admissions")
    )
    daily.columns = ["Date", "Admissions"]

    monthly = (
        filtered.dropna(subset=[date_col])
        .assign(Month=filtered[date_col].dt.to_period("M").astype(str))
        .groupby("Month")
        .size()
        .reset_index(name="Admissions")
    )

    col1, col2 = st.columns(2)

    fig = px.line(
        daily,
        x="Date",
        y="Admissions",
        markers=True,
        title="Daily Admissions"
    )
    col1.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        monthly,
        x="Month",
        y="Admissions",
        markers=True,
        title="Monthly Admissions"
    )
    col2.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    peak = daily.nlargest(10, "Admissions")

    fig = px.bar(
        peak.sort_values("Admissions"),
        x="Admissions",
        y="Date",
        orientation="h",
        color="Admissions",
        title="Top 10 Peak Admission Days"
    )
    col1.plotly_chart(fig, use_container_width=True)

    weekday = (
        filtered[date_col]
        .dt.day_name()
        .value_counts()
        .reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"],
            fill_value=0
        )
        .reset_index()
    )
    weekday.columns = ["Day", "Admissions"]

    fig = px.bar(
        weekday,
        x="Day",
        y="Admissions",
        color="Admissions",
        title="Admissions by Day of Week"
    )
    col2.plotly_chart(fig, use_container_width=True)

    if len(monthly) > 1:
        monthly["Growth %"] = monthly["Admissions"].pct_change() * 100

        fig = px.bar(
            monthly,
            x="Month",
            y="Growth %",
            title="Month-over-Month Admission Growth (%)",
            text="Growth %"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# DISCHARGE ANALYSIS
# ---------------------------------------------------------
elif page == "🚪 Discharge & Recovery Analysis":
    st.subheader("🚪 Discharge Rate Analysis")

    if not outcome_col or not dept_col:
        st.warning("Outcome and Department columns are required.")
        st.stop()

    successful = filtered[outcome_col].isin(["Recovered", "Improved"])
    total = len(filtered)
    discharged = int(successful.sum())
    rate = discharged / total * 100 if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Patients", f"{total:,}")
    c2.metric("Successful Discharges", f"{discharged:,}")
    c3.metric("Overall Discharge Rate", f"{rate:.1f}%")

    if date_col:
        temp = filtered.dropna(subset=[date_col]).copy()
        temp["Month"] = temp[date_col].dt.to_period("M").astype(str)
        monthly = temp.groupby(["Month", outcome_col]).size().reset_index(name="Patients")
        fig = px.line(monthly, x="Month", y="Patients", color=outcome_col,
                      markers=True, title="Monthly Patient Outcome Trend")
        st.plotly_chart(fig, use_container_width=True)

    total_dept = filtered.groupby(dept_col).size().reset_index(name="Total Patients")
    good_dept = filtered[successful].groupby(dept_col).size().reset_index(name="Discharged Patients")
    dr = total_dept.merge(good_dept, on=dept_col, how="left").fillna({"Discharged Patients": 0})
    dr["Discharge Rate (%)"] = dr["Discharged Patients"] / dr["Total Patients"] * 100

    col1, col2 = st.columns(2)
    fig = px.bar(dr.sort_values("Discharge Rate (%)"), x=dept_col, y="Discharge Rate (%)",
                 color="Discharge Rate (%)", title="Discharge Rate by Department")
    col1.plotly_chart(fig, use_container_width=True)

    if los_col:
        avg_stay = filtered.groupby(dept_col)[los_col].mean().reset_index()
        fig = px.bar(avg_stay.sort_values(los_col), x=dept_col, y=los_col,
                     color=los_col, title="Average Length of Stay by Department",
                     labels={los_col: "Average LOS (Days)"})
        col2.plotly_chart(fig, use_container_width=True)

    fig = px.bar(dr.sort_values("Discharge Rate (%)"), x=dept_col, y="Discharge Rate (%)",
                 color="Discharge Rate (%)", title="Discharge Efficiency by Department")
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# SERVICE DEMAND
# ---------------------------------------------------------
elif page == "📈 Service Demand Analysis":
    st.subheader("📈 Service Demand Analysis")

    if dept_col:
        dept_demand = filtered.groupby(dept_col).size().reset_index(name="Patients")
        dept_demand = dept_demand.sort_values("Patients", ascending=False)
        fig = px.bar(dept_demand, x=dept_col, y="Patients", text="Patients",
                     color=dept_col, title="Patient Admissions by Department")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    if diagnosis_col:
        diag = filtered.groupby(diagnosis_col).size().reset_index(name="Patients")
        diag = diag.sort_values("Patients", ascending=False).head(10)
        fig = px.bar(diag, x=diagnosis_col, y="Patients", text="Patients",
                     color="Patients", title="Top 10 Diagnoses by Patient Demand")
        fig.update_traces(textposition="outside")
        col1.plotly_chart(fig, use_container_width=True)

    if dept_col and cost_col:
        costs = filtered.groupby(dept_col)[cost_col].agg(
            Average_Cost="mean", Total_Cost="sum", Patients="count"
        ).reset_index().sort_values("Total_Cost", ascending=False)
        fig = px.bar(costs, x=dept_col, y="Total_Cost", text_auto=".2s",
                     color=dept_col, title="Treatment Cost by Department")
        col2.plotly_chart(fig, use_container_width=True)

    if date_col:
        temp = filtered.dropna(subset=[date_col]).copy()
        month_order = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"]
        temp["Month"] = temp[date_col].dt.month_name()
        monthly = temp.groupby("Month").size().reset_index(name="Patients")
        monthly["Month"] = pd.Categorical(monthly["Month"], categories=month_order, ordered=True)
        monthly = monthly.sort_values("Month")

        col1, col2 = st.columns(2)
        fig = px.line(monthly, x="Month", y="Patients", markers=True,
                      title="Monthly Service Demand")
        col1.plotly_chart(fig, use_container_width=True)

        temp["Weekday"] = temp[date_col].dt.day_name()
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        weekday = temp.groupby("Weekday").size().reset_index(name="Patients")
        weekday["Weekday"] = pd.Categorical(weekday["Weekday"], categories=days, ordered=True)
        weekday = weekday.sort_values("Weekday")
        fig = px.bar(weekday, x="Weekday", y="Patients", text="Patients",
                     color="Patients", title="Patient Admissions by Weekday")
        fig.update_traces(textposition="outside")
        col2.plotly_chart(fig, use_container_width=True)

    admission_time = first_existing(filtered, ["Admission_Time", "Admission Time"])
    if admission_time:
        temp = filtered.copy()
        temp["_time"] = pd.to_datetime(temp[admission_time], errors="coerce")
        temp["_hour"] = temp["_time"].dt.hour
        hourly = temp.dropna(subset=["_hour"]).groupby("_hour").size().reset_index(name="Patients")
        hourly["Time"] = hourly["_hour"].astype(int).map(lambda x: f"{x:02d}:00")
        fig = px.line(hourly, x="Time", y="Patients", markers=True,
                      title="Patient Admissions by Hour")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# TREATMENT WORKLOAD
# ---------------------------------------------------------
elif page == "🏢 Department Workload Analysis":

    st.subheader("🏢 Department Workload Analysis")

    total_patients = filtered[patient_col].nunique() if patient_col else len(filtered)
    total_doctors = (
        filtered[doctor_id_col].nunique()
        if doctor_id_col
        else filtered[doctor_col].nunique()
        if doctor_col else 0
    )

    ratio = total_patients / total_doctors if total_doctors else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Patients", f"{total_patients:,}")
    c2.metric("Doctors", f"{total_doctors:,}")
    c3.metric("Patient / Doctor Ratio", f"{ratio:.2f}" if ratio else "N/A")

    col1, col2 = st.columns(2)

    if doctor_col:
        doctor = (
            filtered.groupby(doctor_col)
            .agg(Patients=("Patient_ID", "count") if patient_col else (doctor_col, "size"))
            .reset_index()
            .sort_values("Patients", ascending=False)
            .head(10)
        )

        fig = px.bar(
            doctor.sort_values("Patients"),
            x="Patients",
            y=doctor_col,
            orientation="h",
            color="Patients",
            title="Top 10 Busiest Doctors"
        )
        col1.plotly_chart(fig, use_container_width=True)

    if dept_col:
        workload = (
            filtered.groupby(dept_col)
            .size()
            .reset_index(name="Patients")
            .sort_values("Patients", ascending=False)
        )

        fig = px.bar(
            workload,
            x=dept_col,
            y="Patients",
            color="Patients",
            title="Department Workload"
        )
        col2.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    if diagnosis_col:
        treatment = (
            filtered[diagnosis_col]
            .value_counts()
            .reset_index()
        )
        treatment.columns = ["Diagnosis", "Patients"]

        fig = px.bar(
            treatment,
            x="Diagnosis",
            y="Patients",
            color="Patients",
            title="Treatment Volume by Diagnosis"
        )
        col1.plotly_chart(fig, use_container_width=True)

    if dept_col and los_col:
        duration = (
            filtered.groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(los_col, ascending=False)
        )

        fig = px.bar(
            duration,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Treatment Duration"
        )
        col2.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# OPERATIONAL BOTTLENECKS
# ---------------------------------------------------------
elif page == "⚠️ Operational Bottlenecks":

    st.subheader("⚠️ Operational Bottleneck Analysis")

    if wait_col:
        avg_wait = filtered[wait_col].mean()
        over_3hr = (filtered[wait_col] > 180).mean() * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("Average Wait", f"{avg_wait:.1f} min")
        c2.metric("Waiting > 3 Hours", f"{over_3hr:.1f}%")

        if los_col:
            c3.metric("Average LOS", f"{filtered[los_col].mean():.2f} days")

        if dept_col:
            wait_dept = (
                filtered.groupby(dept_col)[wait_col]
                .mean()
                .reset_index()
                .sort_values(wait_col, ascending=False)
            )

            fig = px.bar(
                wait_dept,
                x=dept_col,
                y=wait_col,
                color=wait_col,
                title="Average Wait Time by Department"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Wait-time categories
        bins = [0, 60, 120, 180, 240, 300, float("inf")]
        labels = ["<1 hr", "1-2 hr", "2-3 hr", "3-4 hr", "4-5 hr", "5+ hr"]

        temp = filtered.copy()
        temp["Wait_Category"] = pd.cut(
            temp[wait_col],
            bins=bins,
            labels=labels,
            include_lowest=True
        )

        queue = temp["Wait_Category"].value_counts().reindex(labels, fill_value=0)
        queue = queue.reset_index()
        queue.columns = ["Wait Category", "Patients"]

        fig = px.bar(
            queue,
            x="Wait Category",
            y="Patients",
            color="Patients",
            title="Waiting-Time Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    if los_col and severity_col:
        expected_los = filtered[severity_col].map(
            {"Low": 2, "Medium": 5, "High": 14, "Critical": 21}
        )

        delay = (filtered[los_col] - expected_los).clip(lower=0)

        delay_df = pd.DataFrame({
            "Severity": filtered[severity_col],
            "Discharge Delay": delay
        }).groupby("Severity")["Discharge Delay"].mean().reset_index()

        fig = px.bar(
            delay_df,
            x="Severity",
            y="Discharge Delay",
            color="Discharge Delay",
            title="Average Discharge Delay by Severity",
            labels={"Discharge Delay": "Delay (days)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    if readmission_col:
        readmission = filtered[readmission_col]

        if readmission.dtype == object:
            readmission = (
                readmission.astype(str)
                .str.lower()
                .isin(["1", "yes", "true", "readmitted"])
                .astype(int)
            )
        else:
            readmission = pd.to_numeric(readmission, errors="coerce").fillna(0)

        st.metric("Readmission Rate", f"{readmission.mean() * 100:.2f}%")

# ---------------------------------------------------------

# =========================================================
# DEDICATED RESOURCE ANALYSES
# =========================================================

elif page == "👨‍⚕️ Workforce & Staff Utilization":

    st.subheader("👨‍⚕️ Workforce & Staff Utilization")
    st.caption("Analyze doctors, nurses, staff workload, patient-to-resource ratios and workforce pressure.")

    group_col = dept_col if dept_col else hospital_col
    group_label = "Department" if dept_col else "Hospital"

    total_patients = filtered[patient_col].nunique() if patient_col else len(filtered)
    total_doctors = (
        filtered[doctor_id_col].nunique() if doctor_id_col
        else filtered[doctor_col].nunique() if doctor_col else 0
    )
    total_nurses = (
        filtered[nurse_id_col].nunique() if nurse_id_col
        else filtered[nurse_col].nunique() if nurse_col else 0
    )
    total_staff = (
        filtered[staff_id_col].nunique() if staff_id_col
        else filtered[staff_col].nunique() if staff_col
        else filtered[staff_count_col].max() if staff_count_col else 0
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Patients", f"{total_patients:,}")
    k2.metric("Doctors", f"{total_doctors:,}")
    k3.metric("Nurses", f"{total_nurses:,}")
    k4.metric("Other Staff", f"{int(total_staff):,}" if pd.notna(total_staff) else "N/A")

    st.divider()

    # Ratios
    c1, c2, c3 = st.columns(3)
    c1.metric("Patient / Doctor", f"{total_patients / total_doctors:.2f}" if total_doctors else "N/A")
    c2.metric("Patient / Nurse", f"{total_patients / total_nurses:.2f}" if total_nurses else "N/A")
    c3.metric("Patient / Staff", f"{total_patients / total_staff:.2f}" if total_staff else "N/A")

    if group_col:
        w = filtered.groupby(group_col).size().reset_index(name="Patients")

        if doctor_id_col:
            w = w.merge(
                filtered.groupby(group_col)[doctor_id_col].nunique().reset_index(name="Doctors"),
                on=group_col, how="left"
            )
        elif doctor_col:
            w = w.merge(
                filtered.groupby(group_col)[doctor_col].nunique().reset_index(name="Doctors"),
                on=group_col, how="left"
            )
        else:
            w["Doctors"] = 0

        if nurse_id_col:
            w = w.merge(
                filtered.groupby(group_col)[nurse_id_col].nunique().reset_index(name="Nurses"),
                on=group_col, how="left"
            )
        elif nurse_col:
            w = w.merge(
                filtered.groupby(group_col)[nurse_col].nunique().reset_index(name="Nurses"),
                on=group_col, how="left"
            )
        else:
            w["Nurses"] = 0

        if staff_id_col:
            w = w.merge(
                filtered.groupby(group_col)[staff_id_col].nunique().reset_index(name="Staff"),
                on=group_col, how="left"
            )
        elif staff_col:
            w = w.merge(
                filtered.groupby(group_col)[staff_col].nunique().reset_index(name="Staff"),
                on=group_col, how="left"
            )
        elif staff_count_col:
            w = w.merge(
                filtered.groupby(group_col)[staff_count_col].max().reset_index(name="Staff"),
                on=group_col, how="left"
            )
        else:
            w["Staff"] = 0

        for c in ["Doctors", "Nurses", "Staff"]:
            w[c] = pd.to_numeric(w[c], errors="coerce").fillna(0)

        w["Patients_per_Doctor"] = np.where(w["Doctors"] > 0, w["Patients"] / w["Doctors"], np.nan)
        w["Patients_per_Nurse"] = np.where(w["Nurses"] > 0, w["Patients"] / w["Nurses"], np.nan)
        w["Patients_per_Staff"] = np.where(w["Staff"] > 0, w["Patients"] / w["Staff"], np.nan)

        col1, col2 = st.columns(2)
        fig = px.bar(
            w.sort_values("Patients_per_Doctor", ascending=False),
            x=group_col, y="Patients_per_Doctor", color="Patients_per_Doctor",
            title=f"{group_label}-wise Patient-to-Doctor Workload"
        )
        fig.add_hline(y=15, line_dash="dash", annotation_text="15 patients/doctor reference")
        fig.update_layout(xaxis_tickangle=-45)
        col1.plotly_chart(fig, use_container_width=True)

        fig = px.bar(
            w.sort_values("Patients_per_Nurse", ascending=False),
            x=group_col, y="Patients_per_Nurse", color="Patients_per_Nurse",
            title=f"{group_label}-wise Patient-to-Nurse Workload"
        )
        fig.add_hline(y=10, line_dash="dash", annotation_text="10 patients/nurse reference")
        fig.update_layout(xaxis_tickangle=-45)
        col2.plotly_chart(fig, use_container_width=True)

        if (w["Staff"] > 0).any():
            fig = px.bar(
                w.sort_values("Patients_per_Staff", ascending=False),
                x=group_col, y="Patients_per_Staff", color="Patients_per_Staff",
                title=f"{group_label}-wise Patient-to-Staff Workload"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Workforce Utilization Summary")
        st.dataframe(
            w.sort_values("Patients", ascending=False).style.format({
                "Patients_per_Doctor": "{:.1f}",
                "Patients_per_Nurse": "{:.1f}",
                "Patients_per_Staff": "{:.1f}"
            }),
            use_container_width=True, hide_index=True
        )

    if doctor_col:
        doctor_workload = filtered.groupby(doctor_col).size().reset_index(name="Patients")
        doctor_workload = doctor_workload.sort_values("Patients", ascending=False).head(15)
        fig = px.bar(
            doctor_workload.sort_values("Patients"),
            x="Patients", y=doctor_col, orientation="h", color="Patients",
            title="Top 15 Doctors by Patient Workload"
        )
        st.plotly_chart(fig, use_container_width=True)


elif page == "🛏️ Bed Occupancy Analysis":

    st.subheader("🛏️ Bed Occupancy Analysis")
    st.caption(
        "Track daily occupied and available beds, identify peak occupancy, compare hospitals, "
        "and examine department-wise occupancy on the peak date."
    )

    required = [date_col, patient_col, beds_col]
    if not all(required):
        st.warning(
            "This analysis requires Admission Date, Patient ID and Total Beds columns. "
            "The detected dataset does not contain all required fields."
        )
    else:
        bed_df = filtered.copy()
        bed_df[date_col] = pd.to_datetime(bed_df[date_col], errors="coerce")

        # Use discharge date when available; otherwise the admission day is treated as the occupancy day.
        if discharge_col:
            bed_df[discharge_col] = pd.to_datetime(bed_df[discharge_col], errors="coerce")

        bed_df = bed_df.dropna(subset=[date_col, patient_col, beds_col])

        if bed_df.empty:
            st.warning("No valid records are available for the selected filters.")
        else:
            # Hospital bed capacity: one capacity value per hospital.
            hospital_keys = [hospital_col] if hospital_col else []
            if not hospital_keys:
                hospital_keys = ["__Hospital_Group__"]
                bed_df["__Hospital_Group__"] = "All Hospitals"

            hospital_beds = (
                bed_df.groupby(hospital_keys)[beds_col]
                .first()
                .reset_index(name="Total_Beds")
            )
            hospital_beds["Total_Beds"] = pd.to_numeric(
                hospital_beds["Total_Beds"], errors="coerce"
            ).fillna(0)

            # Create daily occupancy records from admission/discharge intervals.
            min_date = bed_df[date_col].min()
            max_date = (
                bed_df[discharge_col].max()
                if discharge_col and bed_df[discharge_col].notna().any()
                else bed_df[date_col].max()
            )
            if pd.isna(max_date) or max_date < min_date:
                max_date = min_date

            dates = pd.date_range(min_date, max_date, freq="D")
            results = []

            for current_date in dates:
                if discharge_col:
                    occupied = bed_df[
                        (bed_df[date_col] <= current_date) &
                        (bed_df[discharge_col].fillna(current_date + pd.Timedelta(days=1)) > current_date)
                    ]
                else:
                    occupied = bed_df[bed_df[date_col] == current_date]

                if hospital_col:
                    occupied_by_hospital = (
                        occupied.groupby(hospital_col)[patient_col].nunique()
                    )
                    for _, row in hospital_beds.iterrows():
                        h = row[hospital_col]
                        total = float(row["Total_Beds"])
                        occ = int(occupied_by_hospital.get(h, 0))
                        available = total - occ
                        results.append({
                            "Date": current_date,
                            hospital_col: h,
                            "Total_Beds": total,
                            "Occupied_Beds": occ,
                            "Available_Beds": available,
                            "Occupancy_Percentage": (occ / total * 100) if total > 0 else np.nan
                        })
                else:
                    total = float(hospital_beds["Total_Beds"].sum())
                    occ = int(occupied[patient_col].nunique())
                    results.append({
                        "Date": current_date,
                        "Total_Beds": total,
                        "Occupied_Beds": occ,
                        "Available_Beds": total - occ,
                        "Occupancy_Percentage": (occ / total * 100) if total > 0 else np.nan
                    })

            occupancy_df = pd.DataFrame(results)

            if occupancy_df.empty:
                st.warning("Unable to calculate daily bed occupancy from the selected data.")
            else:
                # Overall daily occupancy.
                daily_occupancy = (
                    occupancy_df.groupby("Date")
                    .agg(
                        Total_Beds=("Total_Beds", "sum"),
                        Occupied_Beds=("Occupied_Beds", "sum")
                    )
                    .reset_index()
                )
                daily_occupancy["Available_Beds"] = (
                    daily_occupancy["Total_Beds"] - daily_occupancy["Occupied_Beds"]
                )
                daily_occupancy["Occupancy_Percentage"] = np.where(
                    daily_occupancy["Total_Beds"] > 0,
                    daily_occupancy["Occupied_Beds"] / daily_occupancy["Total_Beds"] * 100,
                    np.nan
                )

                peak_day = daily_occupancy.loc[
                    daily_occupancy["Occupied_Beds"].idxmax()
                ]

                # Hospital-level average occupancy.
                if hospital_col:
                    hospital_occupancy = (
                        occupancy_df.groupby(hospital_col)
                        .agg(
                            Total_Beds=("Total_Beds", "first"),
                            Avg_Occupied_Beds=("Occupied_Beds", "mean"),
                            Avg_Available_Beds=("Available_Beds", "mean"),
                            Avg_Occupancy_Rate=("Occupancy_Percentage", "mean"),
                            Peak_Occupied_Beds=("Occupied_Beds", "max")
                        )
                        .reset_index()
                    )
                else:
                    hospital_occupancy = pd.DataFrame({
                        "Hospital": ["All Hospitals"],
                        "Total_Beds": [daily_occupancy["Total_Beds"].max()],
                        "Avg_Occupied_Beds": [daily_occupancy["Occupied_Beds"].mean()],
                        "Avg_Available_Beds": [daily_occupancy["Available_Beds"].mean()],
                        "Avg_Occupancy_Rate": [daily_occupancy["Occupancy_Percentage"].mean()],
                        "Peak_Occupied_Beds": [daily_occupancy["Occupied_Beds"].max()]
                    })

                # KPI calculations.
                total_beds = int(daily_occupancy["Total_Beds"].max())
                peak_occupied = int(peak_day["Occupied_Beds"])
                peak_available = int(peak_day["Available_Beds"])
                peak_rate = float(peak_day["Occupancy_Percentage"])
                avg_rate = float(daily_occupancy["Occupancy_Percentage"].mean())

                k1, k2, k3, k4, k5 = st.columns(5)
                k1.metric("Total Beds", f"{total_beds:,}")
                k2.metric("Peak Occupied Beds", f"{peak_occupied:,}")
                k3.metric("Available at Peak", f"{peak_available:,}")
                k4.metric("Peak Occupancy", f"{peak_rate:.2f}%")
                k5.metric("Average Occupancy", f"{avg_rate:.2f}%")

                st.info(
                    f"Peak occupancy occurred on {peak_day['Date'].strftime('%d-%b-%Y')}: "
                    f"{peak_occupied:,} beds occupied out of {total_beds:,}."
                )

                # Daily occupancy trend.
                st.subheader("📈 Daily Bed Occupancy Trend")
                fig = px.line(
                    daily_occupancy,
                    x="Date",
                    y="Occupied_Beds",
                    title="Daily Bed Occupancy Over Time",
                    labels={"Occupied_Beds": "Occupied Beds", "Date": "Date"}
                )
                fig.add_scatter(
                    x=[peak_day["Date"]],
                    y=[peak_day["Occupied_Beds"]],
                    mode="markers+text",
                    text=["Peak"],
                    textposition="top center",
                    name="Peak Occupancy"
                )
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                # Occupied vs available on peak date.
                st.subheader("🛏️ Occupied vs Available Beds at Peak")
                bed_status = pd.DataFrame({
                    "Status": ["Occupied Beds", "Available Beds"],
                    "Beds": [peak_occupied, peak_available]
                })
                fig = px.pie(
                    bed_status,
                    names="Status",
                    values="Beds",
                    hole=0.5,
                    title=f"Bed Status on {peak_day['Date'].strftime('%d-%b-%Y')}"
                )
                fig.update_traces(textinfo="label+value+percent")
                st.plotly_chart(fig, use_container_width=True)

                # Hospital comparison.
                if hospital_col:
                    st.subheader("🏥 Average Bed Occupancy by Hospital")
                    fig = px.bar(
                        hospital_occupancy.sort_values("Avg_Occupancy_Rate", ascending=False),
                        x=hospital_col,
                        y="Avg_Occupancy_Rate",
                        color="Avg_Occupancy_Rate",
                        text="Avg_Occupancy_Rate",
                        title="Average Bed Occupancy Rate by Hospital",
                        labels={"Avg_Occupancy_Rate": "Average Occupancy Rate (%)"}
                    )
                    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
                    fig.update_layout(yaxis_ticksuffix="%", xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        hospital_occupancy.style.format({
                            "Total_Beds": "{:.0f}",
                            "Avg_Occupied_Beds": "{:.1f}",
                            "Avg_Available_Beds": "{:.1f}",
                            "Avg_Occupancy_Rate": "{:.2f}%",
                            "Peak_Occupied_Beds": "{:.0f}"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                # Department occupancy on peak date.
                if dept_col:
                    if discharge_col:
                        occupied_on_peak = bed_df[
                            (bed_df[date_col] <= peak_day["Date"]) &
                            (bed_df[discharge_col].fillna(peak_day["Date"] + pd.Timedelta(days=1)) > peak_day["Date"])
                        ]
                    else:
                        occupied_on_peak = bed_df[bed_df[date_col] == peak_day["Date"]]

                    department_occupancy = (
                        occupied_on_peak.groupby(dept_col)[patient_col]
                        .nunique()
                        .reset_index(name="Occupied_Beds")
                        .sort_values("Occupied_Beds", ascending=False)
                    )

                    if not department_occupancy.empty:
                        st.subheader("🏢 Department-wise Occupied Beds at Peak")
                        fig = px.bar(
                            department_occupancy.sort_values("Occupied_Beds"),
                            x="Occupied_Beds",
                            y=dept_col,
                            orientation="h",
                            title=f"Department-wise Occupied Beds on {peak_day['Date'].strftime('%d-%b-%Y')}",
                            labels={"Occupied_Beds": "Occupied Beds", dept_col: "Department"},
                            text="Occupied_Beds"
                        )
                        fig.update_traces(textposition="outside")
                        st.plotly_chart(fig, use_container_width=True)

                        highest_department = department_occupancy.iloc[0]
                        lowest_department = department_occupancy.iloc[-1]
                        c1, c2 = st.columns(2)
                        c1.metric(
                            "Highest Occupied Department",
                            str(highest_department[dept_col]),
                            f"{int(highest_department['Occupied_Beds']):,} beds"
                        )
                        c2.metric(
                            "Lowest Occupied Department",
                            str(lowest_department[dept_col]),
                            f"{int(lowest_department['Occupied_Beds']):,} beds"
                        )

                # Download daily occupancy table.
                st.subheader("📋 Daily Occupancy Details")
                st.dataframe(
                    daily_occupancy.style.format({
                        "Total_Beds": "{:.0f}",
                        "Occupied_Beds": "{:.0f}",
                        "Available_Beds": "{:.0f}",
                        "Occupancy_Percentage": "{:.2f}%"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

                csv_data = daily_occupancy.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Daily Bed Occupancy Analysis",
                    csv_data,
                    "daily_bed_occupancy_analysis.csv",
                    "text/csv"
                )


# =========================================================
# RESOURCE CAPACITY & EFFICIENCY
# =========================================================
elif page == "🎯 Resource Capacity & Efficiency":

    st.subheader("🎯 Resource Capacity, Overload & Efficiency Analysis")
    st.caption(
        "Compare patient demand with beds and workforce to identify overloaded, near-capacity, "
        "underutilized and inefficient resource allocation."
    )

    group_col = dept_col if dept_col else hospital_col
    group_label = "Department" if dept_col else "Hospital"

    if not group_col:
        st.warning("A Department or Hospital column is required for resource allocation analysis.")
    else:
        r = filtered.groupby(group_col).size().reset_index(name="Patients")

        # Workforce
        if doctor_id_col:
            r = r.merge(filtered.groupby(group_col)[doctor_id_col].nunique().reset_index(name="Doctors"),
                        on=group_col, how="left")
        elif doctor_col:
            r = r.merge(filtered.groupby(group_col)[doctor_col].nunique().reset_index(name="Doctors"),
                        on=group_col, how="left")
        else:
            r["Doctors"] = 0

        if nurse_id_col:
            r = r.merge(filtered.groupby(group_col)[nurse_id_col].nunique().reset_index(name="Nurses"),
                        on=group_col, how="left")
        elif nurse_col:
            r = r.merge(filtered.groupby(group_col)[nurse_col].nunique().reset_index(name="Nurses"),
                        on=group_col, how="left")
        else:
            r["Nurses"] = 0

        if staff_id_col:
            r = r.merge(filtered.groupby(group_col)[staff_id_col].nunique().reset_index(name="Staff"),
                        on=group_col, how="left")
        elif staff_col:
            r = r.merge(filtered.groupby(group_col)[staff_col].nunique().reset_index(name="Staff"),
                        on=group_col, how="left")
        elif staff_count_col:
            r = r.merge(filtered.groupby(group_col)[staff_count_col].max().reset_index(name="Staff"),
                        on=group_col, how="left")
        else:
            r["Staff"] = 0

        # Beds
        if beds_col:
            r = r.merge(filtered.groupby(group_col)[beds_col].first().reset_index(name="Total_Beds"),
                        on=group_col, how="left")
        else:
            r["Total_Beds"] = np.nan

        # Patient-days and estimated occupancy
        if date_col and los_col and beds_col:
            period_days = max(
                (filtered[date_col].max() - filtered[date_col].min()).days + 1, 1
            )
            pdays = filtered.groupby(group_col)[los_col].sum().reset_index(name="Patient_Days")
            r = r.merge(pdays, on=group_col, how="left")
            r["Bed_Utilization"] = np.where(
                r["Total_Beds"] > 0,
                r["Patient_Days"] / (r["Total_Beds"] * period_days),
                np.nan
            )
        else:
            r["Patient_Days"] = np.nan
            r["Bed_Utilization"] = np.nan

        for c in ["Doctors", "Nurses", "Staff", "Total_Beds"]:
            r[c] = pd.to_numeric(r[c], errors="coerce").fillna(0)

        r["Patients_per_Doctor"] = np.where(r["Doctors"] > 0, r["Patients"] / r["Doctors"], np.nan)
        r["Patients_per_Nurse"] = np.where(r["Nurses"] > 0, r["Patients"] / r["Nurses"], np.nan)
        r["Patients_per_Staff"] = np.where(r["Staff"] > 0, r["Patients"] / r["Staff"], np.nan)

        # Demand-to-capacity gap: positive values mean demand exceeds reference capacity.
        r["Doctor_Gap"] = r["Patients_per_Doctor"] - 15
        r["Nurse_Gap"] = r["Patients_per_Nurse"] - 10
        r["Bed_Gap"] = r["Bed_Utilization"] - 0.80

        def classify(row):
            pressure = []
            if pd.notna(row["Patients_per_Doctor"]):
                pressure.append(row["Patients_per_Doctor"] / 15)
            if pd.notna(row["Patients_per_Nurse"]):
                pressure.append(row["Patients_per_Nurse"] / 10)
            if pd.notna(row["Bed_Utilization"]):
                pressure.append(row["Bed_Utilization"] / 0.80)

            if not pressure:
                return "Insufficient Data"
            p = float(np.mean(pressure))
            if p >= 1.50:
                return "🔴 Overloaded"
            if p >= 1.10:
                return "🟠 Near / Above Capacity"
            if p >= 0.75:
                return "🟢 Efficient / Balanced"
            return "🔵 Underutilized"

        r["Capacity_Status"] = r.apply(classify, axis=1)

        # Efficiency score: workforce pressure is penalized; balanced bed utilization is rewarded.
        bed_eff = 100 - (r["Bed_Utilization"].sub(0.80).abs() / 0.80 * 100)
        bed_eff = bed_eff.clip(lower=0, upper=100).fillna(50)

        doctor_eff = (100 - (r["Patients_per_Doctor"] / 15 - 1).abs() * 100).clip(0, 100).fillna(50)
        nurse_eff = (100 - (r["Patients_per_Nurse"] / 10 - 1).abs() * 100).clip(0, 100).fillna(50)

        r["Resource_Efficiency_Score"] = (
            bed_eff * 0.40 + doctor_eff * 0.30 + nurse_eff * 0.30
        ).round(1)

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Groups Analyzed", f"{len(r):,}")
        k2.metric("Overloaded", int((r["Capacity_Status"] == "🔴 Overloaded").sum()))
        k3.metric("Near / Above Capacity", int((r["Capacity_Status"] == "🟠 Near / Above Capacity").sum()))
        k4.metric("Underutilized", int((r["Capacity_Status"] == "🔵 Underutilized").sum()))

        st.divider()

        col1, col2 = st.columns(2)

        fig = px.bar(
            r.sort_values("Patients", ascending=False),
            x=group_col, y="Patients", color="Capacity_Status",
            title=f"{group_label}-wise Patient Demand and Capacity Status"
        )
        fig.update_layout(xaxis_tickangle=-45)
        col1.plotly_chart(fig, use_container_width=True)

        fig = px.bar(
            r.sort_values("Resource_Efficiency_Score"),
            x=group_col, y="Resource_Efficiency_Score",
            color="Capacity_Status", text="Resource_Efficiency_Score",
            title=f"{group_label}-wise Resource Efficiency Score"
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(xaxis_tickangle=-45, yaxis_title="Efficiency Score (0–100)")
        col2.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Demand vs Available Resources")
        gap = r[[group_col, "Patients", "Doctors", "Nurses", "Staff", "Total_Beds",
                 "Patients_per_Doctor", "Patients_per_Nurse", "Bed_Utilization",
                 "Doctor_Gap", "Nurse_Gap", "Bed_Gap", "Capacity_Status",
                 "Resource_Efficiency_Score"]].copy()

        st.dataframe(
            gap.sort_values("Resource_Efficiency_Score").style.format({
                "Patients_per_Doctor": "{:.1f}",
                "Patients_per_Nurse": "{:.1f}",
                "Bed_Utilization": "{:.1%}",
                "Doctor_Gap": "{:+.1f}",
                "Nurse_Gap": "{:+.1f}",
                "Bed_Gap": "{:+.1%}",
                "Resource_Efficiency_Score": "{:.1f}"
            }),
            use_container_width=True, hide_index=True
        )

        # Explicit inefficiency flags.
        st.subheader("🚨 Resource Allocation Inefficiencies")
        issues = []

        for _, row in r.iterrows():
            flags = []
            if pd.notna(row["Patients_per_Doctor"]) and row["Patients_per_Doctor"] > 15:
                flags.append("Doctor workload above 15:1")
            if pd.notna(row["Patients_per_Nurse"]) and row["Patients_per_Nurse"] > 10:
                flags.append("Nurse workload above 10:1")
            if pd.notna(row["Bed_Utilization"]) and row["Bed_Utilization"] > 0.90:
                flags.append("Bed utilization above 90%")
            if pd.notna(row["Bed_Utilization"]) and row["Bed_Utilization"] < 0.50:
                flags.append("Bed utilization below 50%")
            if flags:
                issues.append({
                    group_label: row[group_col],
                    "Issue": "; ".join(flags),
                    "Priority": "High" if len(flags) >= 2 else "Medium"
                })

        if issues:
            issue_df = pd.DataFrame(issues)
            st.dataframe(issue_df, use_container_width=True, hide_index=True)
        else:
            st.success("No resource-allocation inefficiencies were detected using the configured thresholds.")

        csv_data = gap.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Resource Capacity & Efficiency Analysis",
            csv_data,
            "resource_capacity_efficiency_analysis.csv",
            "text/csv"
        )

        st.info(
            "Interpretation: patient-to-doctor and patient-to-nurse thresholds are reference planning "
            "benchmarks (15:1 and 10:1). Bed utilization is estimated from patient-days when a daily "
            "occupied-bed census is unavailable, so it should not be interpreted as simultaneous occupancy."
        )


# =========================================================
# BENCHMARK & UTILIZATION GAP ANALYSIS - LEGACY
# =========================================================
elif page == "📏 Benchmark & Utilization Gap":
    st.title("📏 Benchmark & Utilization Gap Analysis")
    st.caption("Compare actual resource utilization with defined targets and quantify the utilization gap.")

    DOCTOR_BENCHMARK = 15
    NURSE_BENCHMARK = 10
    BED_BENCHMARK = 0.80

    if dept_col:
        group_col = dept_col
        label_name = "Department"
    elif hospital_col:
        group_col = hospital_col
        label_name = "Hospital"
    else:
        group_col = None
        label_name = "Group"

    if group_col:
        g = filtered.groupby(group_col, dropna=False).size().reset_index(name="Patients")

        if doctor_id_col:
            d = filtered.groupby(group_col)[doctor_id_col].nunique().reset_index(name="Doctors")
            g = g.merge(d, on=group_col, how="left")
        else:
            g["Doctors"] = 0

        if nurse_id_col:
            n = filtered.groupby(group_col)[nurse_id_col].nunique().reset_index(name="Nurses")
            g = g.merge(n, on=group_col, how="left")
        elif nurse_col:
            n = filtered.groupby(group_col)[nurse_col].nunique().reset_index(name="Nurses")
            g = g.merge(n, on=group_col, how="left")
        else:
            g["Nurses"] = 0

        bed_source = beds_col if beds_col else (
            "Total_Beds" if "Total_Beds" in filtered.columns else
            "Beds" if "Beds" in filtered.columns else None
        )
        if bed_source:
            b = filtered.groupby(group_col)[bed_source].first().reset_index(name="Beds")
            g = g.merge(b, on=group_col, how="left")
        else:
            g["Beds"] = 0

        for c in ["Doctors", "Nurses", "Beds"]:
            g[c] = pd.to_numeric(g[c], errors="coerce").fillna(0)

        g["Patients_per_Doctor"] = np.where(g["Doctors"] > 0, g["Patients"] / g["Doctors"], np.nan)
        g["Patients_per_Nurse"] = np.where(g["Nurses"] > 0, g["Patients"] / g["Nurses"], np.nan)
        g["Doctor_Gap"] = g["Patients_per_Doctor"] - DOCTOR_BENCHMARK
        g["Nurse_Gap"] = g["Patients_per_Nurse"] - NURSE_BENCHMARK

        if date_col and los_col and bed_source:
            period_days = max((filtered[date_col].max() - filtered[date_col].min()).days + 1, 1)
            tmp = filtered[[group_col, los_col]].copy()
            tmp[los_col] = pd.to_numeric(tmp[los_col], errors="coerce").fillna(0)
            pdays = tmp.groupby(group_col)[los_col].sum().reset_index(name="Patient_Days")
            g = g.merge(pdays, on=group_col, how="left")
            g["Bed_Utilization"] = np.where(
                g["Beds"] > 0,
                g["Patient_Days"] / (g["Beds"] * period_days),
                np.nan
            )
        else:
            g["Bed_Utilization"] = np.nan

        g["Bed_Gap"] = g["Bed_Utilization"] - BED_BENCHMARK

        def status(row):
            ratios = []
            if pd.notna(row["Patients_per_Doctor"]):
                ratios.append(row["Patients_per_Doctor"] / DOCTOR_BENCHMARK)
            if pd.notna(row["Patients_per_Nurse"]):
                ratios.append(row["Patients_per_Nurse"] / NURSE_BENCHMARK)
            if pd.notna(row["Bed_Utilization"]):
                ratios.append(row["Bed_Utilization"] / BED_BENCHMARK)
            if not ratios:
                return "Insufficient Data"
            s = float(np.mean(ratios))
            if s >= 1.5:
                return "🔴 Excessive Pressure"
            if s >= 1.1:
                return "🟠 Above Benchmark"
            if s >= 0.75:
                return "🟢 Optimal"
            return "🔵 Underutilized"

        g["Status"] = g.apply(status, axis=1)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🎯 Doctor Benchmark", "15:1")
        k2.metric("🎯 Nurse Benchmark", "10:1")
        k3.metric("🟢 Optimal", int((g["Status"] == "🟢 Optimal").sum()))
        k4.metric("⚠️ Above Benchmark", int(g["Status"].isin(["🔴 Excessive Pressure", "🟠 Above Benchmark"]).sum()))

        c1, c2 = st.columns(2)

        fig = px.bar(g.sort_values("Doctor_Gap", ascending=False), x=group_col, y="Patients_per_Doctor",
                     title=f"{label_name}-wise Patient-to-Doctor Ratio")
        fig.add_hline(y=DOCTOR_BENCHMARK, line_dash="dash", annotation_text="15:1 Benchmark")
        fig.update_layout(xaxis_tickangle=-45)
        c1.plotly_chart(fig, use_container_width=True)

        fig = px.bar(g.sort_values("Nurse_Gap", ascending=False), x=group_col, y="Patients_per_Nurse",
                     title=f"{label_name}-wise Patient-to-Nurse Ratio")
        fig.add_hline(y=NURSE_BENCHMARK, line_dash="dash", annotation_text="10:1 Benchmark")
        fig.update_layout(xaxis_tickangle=-45)
        c2.plotly_chart(fig, use_container_width=True)

        st.subheader("📉 Workforce Benchmark Gaps")
        gap = g[[group_col, "Doctor_Gap", "Nurse_Gap"]].melt(
            id_vars=group_col, var_name="Resource", value_name="Gap"
        )
        gap["Resource"] = gap["Resource"].map({"Doctor_Gap": "Doctor Gap", "Nurse_Gap": "Nurse Gap"})
        fig = px.bar(gap, x=group_col, y="Gap", color="Resource", barmode="group",
                     title="Benchmark Gap (+ = Above Benchmark)")
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        if g["Bed_Utilization"].notna().any():
            fig = px.bar(g.sort_values("Bed_Utilization", ascending=False), x=group_col, y="Bed_Utilization",
                         title=f"{label_name}-wise Estimated Bed Utilization")
            fig.add_hline(y=BED_BENCHMARK, line_dash="dash", annotation_text="80% Target")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Benchmark Gap Summary")
        st.dataframe(
            g.style.format({
                "Patients_per_Doctor": "{:.1f}",
                "Doctor_Gap": "{:+.1f}",
                "Patients_per_Nurse": "{:.1f}",
                "Nurse_Gap": "{:+.1f}",
                "Bed_Utilization": "{:.1%}",
                "Bed_Gap": "{:+.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("A department or hospital column is required for this analysis.")

# HOSPITAL RESOURCE PERFORMANCE ANALYSIS
# ---------------------------------------------------------
elif page == "🏆 Hospital Resource Performance":

    st.subheader("🏆 Hospital Resource Performance Analysis")
    st.caption("Compare hospitals using patient demand, bed capacity, workforce workload and operational performance.")

    # Build hospital-level resource summary
    group_cols = [hospital_col]
    if hospital_type_col:
        group_cols.append(hospital_type_col)

    hospital_summary = filtered.groupby(group_cols).agg(
        Patients=(patient_col, "nunique") if patient_col else (hospital_col, "size"),
        Total_Beds=(beds_col, "first") if beds_col else (hospital_col, "size"),
        Doctors=(doctor_id_col, "nunique") if doctor_id_col else (hospital_col, "size"),
        Nurses=(nurse_id_col, "nunique") if nurse_id_col else (nurse_col, "nunique") if nurse_col else (hospital_col, "size"),
        Avg_Wait=(wait_col, "mean") if wait_col else (hospital_col, "size"),
        Avg_LOS=(los_col, "mean") if los_col else (hospital_col, "size")
    ).reset_index()

    # Patient-days based estimated bed utilization.
    # This is preferable to patients / beds because LOS is available.
    if patient_col and los_col and beds_col and date_col:
        analysis_days = max(
            (filtered[date_col].max() - filtered[date_col].min()).days + 1,
            1
        )
        patient_days = (
            filtered.groupby(hospital_col)[los_col]
            .sum()
            .reset_index(name="Patient_Days")
        )
        hospital_summary = hospital_summary.merge(
            patient_days, on=hospital_col, how="left"
        )
        hospital_summary["Bed_Utilization_%"] = (
            hospital_summary["Patient_Days"] /
            (hospital_summary["Total_Beds"] * analysis_days)
        ) * 100
    else:
        hospital_summary["Bed_Utilization_%"] = (
            hospital_summary["Patients"] /
            hospital_summary["Total_Beds"].replace(0, pd.NA)
        ) * 100

    hospital_summary["Patients_per_Doctor"] = (
        hospital_summary["Patients"] /
        hospital_summary["Doctors"].replace(0, pd.NA)
    )
    hospital_summary["Patients_per_Nurse"] = (
        hospital_summary["Patients"] /
        hospital_summary["Nurses"].replace(0, pd.NA)
    )

    # Normalize indicators into performance components.
    # Lower workforce burden is better; utilization closer to a practical target is better.
    def minmax(series, higher_is_better=True):
        s = pd.to_numeric(series, errors="coerce")
        if s.max() == s.min():
            return pd.Series(100.0, index=s.index)
        score = (s - s.min()) / (s.max() - s.min()) * 100
        return score if higher_is_better else 100 - score

    hospital_summary["Bed_Score"] = hospital_summary["Bed_Utilization_%"].clip(0, 100)
    hospital_summary["Doctor_Score"] = minmax(hospital_summary["Patients_per_Doctor"], False)
    hospital_summary["Nurse_Score"] = minmax(hospital_summary["Patients_per_Nurse"], False)
    hospital_summary["Demand_Score"] = minmax(hospital_summary["Patients"], True)

    hospital_summary["Performance_Score"] = (
        hospital_summary["Bed_Score"] * 0.30 +
        hospital_summary["Doctor_Score"] * 0.25 +
        hospital_summary["Nurse_Score"] * 0.25 +
        hospital_summary["Demand_Score"] * 0.20
    ).round(1)

    hospital_summary["Performance"] = pd.cut(
        hospital_summary["Performance_Score"],
        bins=[-1, 40, 60, 80, 101],
        labels=["🔴 Critical", "🟠 Needs Attention", "🟡 Good", "🟢 Excellent"]
    )

    # KPI cards
    best_hospital = hospital_summary.loc[
        hospital_summary["Performance_Score"].idxmax(), hospital_col
    ]
    highest_load = hospital_summary.loc[
        hospital_summary["Patients_per_Doctor"].idxmax(), hospital_col
    ]
    highest_nurse_load = hospital_summary.loc[
        hospital_summary["Patients_per_Nurse"].idxmax(), hospital_col
    ]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏥 Hospitals", f"{hospital_summary[hospital_col].nunique():,}")
    c2.metric("👥 Total Patients", f"{hospital_summary['Patients'].sum():,}")
    c3.metric("🏆 Top Performance", str(best_hospital))
    c4.metric("⚠️ Highest Nurse Load", str(highest_nurse_load))

    st.divider()

    # Hospital ranking
    st.subheader("🏆 Hospital Performance Ranking")
    ranking = hospital_summary.sort_values("Performance_Score", ascending=False)

    fig = px.bar(
        ranking,
        x=hospital_col,
        y="Performance_Score",
        color="Performance",
        text="Performance_Score",
        title="Overall Hospital Resource Performance Score"
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(xaxis_tickangle=-45, yaxis_title="Performance Score (0–100)")
    st.plotly_chart(fig, use_container_width=True)

    # Resource comparison
    st.subheader("📊 Hospital Resource Comparison")
    col1, col2 = st.columns(2)

    fig = px.bar(
        hospital_summary.sort_values("Bed_Utilization_%", ascending=False),
        x=hospital_col,
        y="Bed_Utilization_%",
        color="Bed_Utilization_%",
        title="Estimated Bed Utilization by Hospital",
        labels={"Bed_Utilization_%": "Bed Utilization (%)"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    col1.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        hospital_summary.sort_values("Patients", ascending=False),
        x=hospital_col,
        y="Patients",
        color="Patients",
        title="Patient Volume by Hospital"
    )
    fig.update_layout(xaxis_tickangle=-45)
    col2.plotly_chart(fig, use_container_width=True)

    # Workforce comparison
    col1, col2 = st.columns(2)

    fig = px.bar(
        hospital_summary.sort_values("Patients_per_Doctor", ascending=False),
        x=hospital_col,
        y="Patients_per_Doctor",
        color="Patients_per_Doctor",
        title="Patients per Doctor by Hospital"
    )
    fig.add_hline(y=15, line_dash="dash", annotation_text="15:1 reference")
    fig.update_layout(xaxis_tickangle=-45)
    col1.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        hospital_summary.sort_values("Patients_per_Nurse", ascending=False),
        x=hospital_col,
        y="Patients_per_Nurse",
        color="Patients_per_Nurse",
        title="Patients per Nurse by Hospital"
    )
    fig.add_hline(y=10, line_dash="dash", annotation_text="10:1 reference")
    fig.update_layout(xaxis_tickangle=-45)
    col2.plotly_chart(fig, use_container_width=True)

    # Multi-indicator heatmap
    st.subheader("🔥 Hospital Resource Performance Heatmap")
    heatmap = hospital_summary.set_index(hospital_col)[
        ["Bed_Utilization_%", "Patients_per_Doctor", "Patients_per_Nurse", "Performance_Score"]
    ].copy()
    heatmap["Patients_per_Doctor"] = minmax(heatmap["Patients_per_Doctor"], False)
    heatmap["Patients_per_Nurse"] = minmax(heatmap["Patients_per_Nurse"], False)
    heatmap = heatmap.rename(columns={
        "Bed_Utilization_%": "Bed Utilization",
        "Patients_per_Doctor": "Doctor Efficiency",
        "Patients_per_Nurse": "Nurse Efficiency",
        "Performance_Score": "Overall Performance"
    })

    fig = px.imshow(
        heatmap,
        text_auto=".1f",
        aspect="auto",
        title="Normalized Hospital Resource Indicators"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top and attention hospitals
    st.subheader("🚨 Hospitals Requiring Attention")
    attention = hospital_summary.sort_values("Performance_Score").head(5).copy()
    attention_display = attention[[
        hospital_col, "Patients", "Total_Beds", "Bed_Utilization_%",
        "Doctors", "Nurses", "Patients_per_Doctor", "Patients_per_Nurse",
        "Performance_Score", "Performance"
    ]]
    st.dataframe(
        attention_display.style.format({
            "Bed_Utilization_%": "{:.2f}%",
            "Patients_per_Doctor": "{:.1f}",
            "Patients_per_Nurse": "{:.1f}",
            "Performance_Score": "{:.1f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Full downloadable hospital-level table
    st.subheader("📋 Hospital Resource Performance Table")
    display_cols = [
        hospital_col,
        "Patients", "Total_Beds", "Doctors", "Nurses",
        "Bed_Utilization_%", "Patients_per_Doctor", "Patients_per_Nurse",
        "Avg_Wait", "Avg_LOS", "Performance_Score", "Performance"
    ]
    display_cols = [c for c in display_cols if c in hospital_summary.columns]
    st.dataframe(
        hospital_summary[display_cols].sort_values("Performance_Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv_data = hospital_summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Hospital Performance Analysis",
        csv_data,
        "hospital_resource_performance_analysis.csv",
        "text/csv"
    )

    st.info(
        "Interpretation: Bed utilization is estimated from patient-days divided by available bed-days. "
        "Because this dataset is encounter-level rather than a daily census, this should be treated as an "
        "estimated utilization measure rather than simultaneous occupied-bed occupancy."
    )

# ---------------------------------------------------------
# CAPACITY TREND & RISK ANALYSIS
# ---------------------------------------------------------
elif page == "📊 Capacity Trends & Risk":

    st.subheader("📊 Capacity Trends & Risk Analysis")
    st.caption("Track weekly/monthly demand, bed utilization and workforce pressure to identify emerging capacity risks.")

    if not date_col:
        st.warning("An admission date column is required for trend analysis.")
    else:
        temp = filtered.dropna(subset=[date_col]).copy()
        temp["Month"] = temp[date_col].dt.to_period("M").astype(str)
        temp["Week"] = temp[date_col].dt.to_period("W").astype(str)

        # Monthly patient demand
        monthly = temp.groupby("Month").size().reset_index(name="Patients")
        monthly["Patients_Growth_%"] = monthly["Patients"].pct_change() * 100

        # Weekly patient demand
        weekly = temp.groupby("Week").size().reset_index(name="Patients")
        weekly["Patients_Growth_%"] = weekly["Patients"].pct_change() * 100

        # Resource counts over time. Counts are based on unique resources observed in each period.
        if doctor_id_col:
            monthly_doctors = temp.groupby("Month")[doctor_id_col].nunique().reset_index(name="Doctors")
            monthly = monthly.merge(monthly_doctors, on="Month", how="left")
        elif doctor_col:
            monthly_doctors = temp.groupby("Month")[doctor_col].nunique().reset_index(name="Doctors")
            monthly = monthly.merge(monthly_doctors, on="Month", how="left")
        else:
            monthly["Doctors"] = np.nan

        if nurse_id_col:
            monthly_nurses = temp.groupby("Month")[nurse_id_col].nunique().reset_index(name="Nurses")
            monthly = monthly.merge(monthly_nurses, on="Month", how="left")
        elif nurse_col:
            monthly_nurses = temp.groupby("Month")[nurse_col].nunique().reset_index(name="Nurses")
            monthly = monthly.merge(monthly_nurses, on="Month", how="left")
        else:
            monthly["Nurses"] = np.nan

        monthly["Patients_per_Doctor"] = np.where(
            monthly["Doctors"] > 0, monthly["Patients"] / monthly["Doctors"], np.nan
        )
        monthly["Patients_per_Nurse"] = np.where(
            monthly["Nurses"] > 0, monthly["Patients"] / monthly["Nurses"], np.nan
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Peak Monthly Patients", f"{int(monthly['Patients'].max()):,}")
        c2.metric("Peak Weekly Patients", f"{int(weekly['Patients'].max()):,}")
        c3.metric(
            "Peak Patient/Doctor",
            f"{monthly['Patients_per_Doctor'].max():.1f}" if monthly["Patients_per_Doctor"].notna().any() else "N/A"
        )
        c4.metric(
            "Peak Patient/Nurse",
            f"{monthly['Patients_per_Nurse'].max():.1f}" if monthly["Patients_per_Nurse"].notna().any() else "N/A"
        )

        st.divider()

        # Monthly demand trend
        fig = px.line(
            monthly, x="Month", y="Patients", markers=True,
            title="Monthly Patient Demand Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Weekly demand trend
        fig = px.line(
            weekly, x="Week", y="Patients", markers=True,
            title="Weekly Patient Demand Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Workforce pressure trends
        col1, col2 = st.columns(2)
        fig = px.line(
            monthly, x="Month", y="Patients_per_Doctor", markers=True,
            title="Monthly Patient-to-Doctor Pressure"
        )
        fig.add_hline(y=15, line_dash="dash", annotation_text="15:1 benchmark")
        col1.plotly_chart(fig, use_container_width=True)

        fig = px.line(
            monthly, x="Month", y="Patients_per_Nurse", markers=True,
            title="Monthly Patient-to-Nurse Pressure"
        )
        fig.add_hline(y=10, line_dash="dash", annotation_text="10:1 benchmark")
        col2.plotly_chart(fig, use_container_width=True)

        # Bed utilization trend from patient-days when possible.
        if los_col and beds_col:
            temp[los_col] = pd.to_numeric(temp[los_col], errors="coerce")
            monthly_days = temp.groupby("Month")[los_col].sum().reset_index(name="Patient_Days")
            monthly_beds = temp.groupby("Month")[beds_col].first().reset_index(name="Beds")
            bed_trend = monthly_days.merge(monthly_beds, on="Month", how="left")
            bed_trend["Days_In_Month"] = pd.to_datetime(bed_trend["Month"]).dt.days_in_month
            bed_trend["Bed_Utilization_%"] = np.where(
                bed_trend["Beds"] > 0,
                bed_trend["Patient_Days"] / (bed_trend["Beds"] * bed_trend["Days_In_Month"]) * 100,
                np.nan
            )

            st.subheader("🛏️ Monthly Bed Capacity Utilization Trend")
            fig = px.line(
                bed_trend, x="Month", y="Bed_Utilization_%", markers=True,
                title="Monthly Estimated Bed Utilization",
                labels={"Bed_Utilization_%": "Bed Utilization (%)"}
            )
            fig.add_hline(y=80, line_dash="dash", annotation_text="80% target")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Bed utilization trend requires Admission Date, Length of Stay and Total Beds/Beds columns.")

        # Explicit risk flags based on trend and benchmarks.
        risk_rows = []
        for _, row in monthly.iterrows():
            risks = []
            if row["Patients_per_Doctor"] > 15:
                risks.append("Doctor workload above benchmark")
            if row["Patients_per_Nurse"] > 10:
                risks.append("Nurse workload above benchmark")
            if row["Patients_Growth_%"] >= 10:
                risks.append("Demand increased ≥10% month-over-month")
            if risks:
                risk_rows.append({
                    "Month": row["Month"],
                    "Patients": int(row["Patients"]),
                    "Demand Growth %": row["Patients_Growth_%"],
                    "Patient/Doctor": row["Patients_per_Doctor"],
                    "Patient/Nurse": row["Patients_per_Nurse"],
                    "Risk Indicators": "; ".join(risks),
                    "Risk Level": "High" if len(risks) >= 2 else "Medium"
                })

        st.subheader("🚨 Emerging Capacity Risks")
        if risk_rows:
            risk_df = pd.DataFrame(risk_rows)
            st.dataframe(
                risk_df.style.format({
                    "Demand Growth %": "{:+.1f}%",
                    "Patient/Doctor": "{:.1f}",
                    "Patient/Nurse": "{:.1f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No emerging monthly capacity risks were detected using the configured thresholds.")

        st.info(
            "Trend interpretation: monthly/weekly workforce counts represent unique resources observed in each period. "
            "Bed utilization is estimated from patient-days when daily occupied-bed census data is unavailable."
        )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.caption(
    "Healthcare Operations Dashboard | Streamlit + Plotly | "
    "Interactive filters update all available charts."
)






