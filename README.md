# Development of a Healthcare Operations Intelligence Dashboard with Decision Analytics - Team B, Batch 2

Interactive hospital operations analytics dashboard built with **Streamlit + Plotly**.

**Live App**: https://medicaloperationsdashboard.streamlit.app/

**Dataset**: [Download medical_operations_master.csv from Google Drive](https://drive.google.com/file/d/1vbt6YUnj2LN-rLt-fzErgynIpSKWV4Zd/view?usp=sharing)

---

## Quick Start

1. Open the live app link above
2. In the sidebar, upload `medical_operations_master.csv`
3. Use the sidebar filters and radio buttons to explore all 14 sections

---

## Screenshots

![Dashboard Snapshot 1](Dashboard%20snaphot%201.png)

![Dashboard Snapshot 2](Dashbaord%20snapshot%202.png)

---

## Sidebar Filters

All sections respond to these filters simultaneously:

- **Admission date range** — date range picker
- **Department** — multi-select
- **Hospital Type** — multi-select (Government / Private)
- **Diagnosis** — multi-select
- **Severity** — multi-select

---

## Dashboard Sections

| # | Section | Key Metrics & Charts |
|---|---|---|
| 1 | Dashboard Overview | 5 KPI cards (Patients, Doctors, Avg Wait, Avg LOS, Total Cost); bar + donut charts by department, diagnosis, and outcome |
| 2 | Patient Flow & Outcomes | Department-wise patient count, wait time, LOS; outcome KPIs (Recovered/Improved/Transferred); monthly outcome trend |
| 3 | Hospital & Facility Analysis | Top 15 hospitals by volume; Government vs Private split; avg cost and LOS by department |
| 4 | Admission & Demand Trends | Daily/monthly admission lines; top 10 peak days; day-of-week bar; month-over-month growth |
| 5 | Discharge & Recovery Analysis | Overall discharge rate; monthly outcome trend; discharge rate and LOS by department |
| 6 | Service Demand Analysis | Patients by department; top 10 diagnoses; treatment cost by department; monthly and weekday demand |
| 7 | Workforce & Staff Utilization | Patient/Doctor/Nurse/Staff KPIs and ratios; department-level workload bars with 15:1 and 10:1 reference lines; top 15 doctors table |
| 8 | Bed Occupancy Analysis | 5 KPIs (Total Beds, Peak Occupied, Peak Rate, Avg Rate); daily occupancy trend; hospital occupancy comparison; department breakdown on peak date; CSV download |
| 9 | Department Workload Analysis | Top 10 busiest doctors; workload by department; treatment volume by diagnosis; avg LOS by department |
| 10 | Operational Bottlenecks | % patients waiting >3 hrs; wait-time distribution bands; discharge delay by severity; readmission rate |
| 11 | Resource Capacity & Efficiency | Capacity status (Overloaded / Near Capacity / Balanced / Underutilized); efficiency score 0-100 per department; inefficiency flags table; CSV download |
| 12 | Benchmark & Utilization Gap | Doctor 15:1 and Nurse 10:1 benchmarks; gap charts; bed utilization vs 80% target; gap summary table |
| 13 | Capacity Trends & Risk | Monthly and weekly demand trends; workforce pressure trends; bed utilization trend; auto-flagged risk months table |
| 14 | Hospital Resource Performance | Composite performance score per hospital; heatmap; hospitals needing attention; CSV download |

---

## Dataset Columns Expected

The app auto-detects these column names (no renaming needed):

| Field | Column Names |
|---|---|
| Patient ID | `Patient_ID`, `PatientID` |
| Department | `Department_Patient`, `Department` |
| Admission Date | `Admission_Date`, `Admit_Date` |
| Discharge Date | `Discharge_Date`, `Discharge_Time` |
| Wait Time | `Wait_Time_Minutes`, `Wait_Time` |
| Length of Stay | `Length_of_Stay_Days`, `LOS_Days` |
| Doctor | `Doctor_Name`, `Doctor_ID` |
| Nurse | `Nurse_Name`, `Nurse_ID` |
| Staff | `Staff_Name`, `Staff_ID`, `Total_Staff` |
| Treatment Cost | `Treatment_Cost_INR`, `Treatment_Cost_USD` |
| Hospital | `Hospital_Name`, `Hospital_Type` |
| Beds | `Total_Beds`, `Available_Beds`, `Occupied_Beds` |
| Clinical | `Diagnosis`, `Severity_Level`, `Outcome` |
| Readmission | `Readmission_Flag`, `Readmission_30_Days` |

# 📊 Exploratory Data Analysis (EDA)

## 🔍 Key Findings — Final EDA Summary Insights

The dataset contains **100,000 patient records** and **28 features**, providing insights into hospital operations, patient demographics, treatment costs, healthcare resources, and patient outcomes.

### 📌 Dataset Overview

* **Total Records:** 100,000
* **Total Features:** 28 columns
* **Average Patient Age:** 50.48 years
* **Age Range:** 1–100 years

### 🏥 Patient & Department Insights

* **Most Common Department:** Dermatology — 10,205 patients
* **Most Common Diagnosis:** Heart Disease — 10,218 cases
* **Most Frequent Severity Level:** Low — 40,094 patients
* **Most Common Insurance Type:** Government Insurance — 25,075 patients

### ⏱️ Hospital Operations Insights

* **Average Length of Stay:** 5.36 days
* **Average Wait Time:** 152.04 minutes
* **Average Hospital Capacity:** 1,119.64 beds
* **Unique Doctors:** 500
* **Unique Hospitals:** 25
* **Unique Nurses:** 300

### 💰 Financial & Treatment Insights

* **Average Treatment Cost:** USD 4,893.89
* **Treatment Cost Range:** USD 100–49,999
  
### 🛏️ Bed Utilization Insights

- **Total Beds:** 28,490
- **Occupied Beds:** 805
- **Available Beds:** 27,685
- **Overall Occupancy Rate:** 2.83%
- **Peak Date:** 15-Feb-2026

### 📈 Patient Outcomes & Readmissions

* **Total Readmission Cases:** 7,477
* **Readmission Rate:** 7.48%
* **Most Common Patient Outcome:** Recovered — 68,568 patients

### 🌍 Geographic & Hospital Insights

* **Most Represented State:** Telangana — 16,501 patients
* **Most Represented City:** Hyderabad — 16,501 patients
* **Private Hospital Records:** 62,384
* **Government Hospital Records:** 37,616

---

## 🎯 Overall EDA Insights

The exploratory data analysis provides a comprehensive overview of healthcare operations, highlighting patient distribution across departments, hospital resource availability, treatment costs, waiting times, readmission trends, and patient outcomes.

These findings serve as a foundation for developing interactive dashboards and generating data-driven insights to support healthcare operational decision-making.

---

## Run Locally

```bash
pip install streamlit pandas numpy plotly
streamlit run app.py
```

---

## 🛠️ Tech Stack

- **Programming Language:** Python
- **Data Analysis:** Pandas, NumPy
- **Data Visualization:** Matplotlib, Seaborn, Plotly
- **Dashboard Development:** Streamlit
- **Geographic Analysis:** Folium, GeoPandas
- **Development Environment:** Jupyter Notebook, VS Code

---

## Team

**Team B - Batch 2**
Individual task contributions merged into one unified Streamlit app, deployed on Streamlit Community Cloud.

---

## License

This project is licensed under the [MIT License](LICENSE).
