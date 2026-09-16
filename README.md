# Healthcare System Performance & Sustainability Analytics

## Overview

A province-year analysis of healthcare-system performance across **Canadian provinces**, examining how changing population demand, healthcare resources, expenditure, access, and outcomes interact.

The project applies an **economic and quantitative analysis lens** to assess resource alignment, cross-provincial differences, and system pressures using descriptive evidence.

---

## At a Glance

| Metric                       |                                                                          Scope |
| ---------------------------- | -----------------------------------------------------------------------------: |
| Provinces                    |                                                                   **10** |
| Province-year observations   |                                                                  **730** |
| Overall data coverage        |                                                           **1971–2025** |
| Research questions           |                                                                    **6** |
| Healthcare access indicators |                                                                  **28+** |
| Analytical grain             |                                                        **Province-year** |
| Core dimensions              | **Demand · Capacity · Workforce · Expenditure · Access · Outcomes** |

---

## Selected Findings

* **Aging is accelerating relative to total population.** National average annual growth was **2.87% for 65+**, **3.27% for 80+**, and **3.63% for 85+**.
* **Hospital capacity came under broad relative pressure.** Beds per 100,000 declined in **10 provinces** examined from 2009–2022.
* **Physician growth exceeded population growth in all 10 provinces** with available data.
* **Real healthcare expenditure generally outpaced population and demographic growth**, but higher resource intensity did not consistently correspond with stronger access or outcomes.
* **Access varied substantially:** 2022 median hip-replacement waits ranged from **108 days in Ontario to 367 days in Saskatchewan**.
* **Outcomes diverged substantially:** 2022 avoidable hospitalization rates ranged from **281 per 100,000 in British Columbia to 455 in Saskatchewan**.
* **Resource quantity alone did not explain performance.** Provinces with broadly similar resource levels could exhibit markedly different access and outcome profiles.

### Population & Demographic Pressure

![Population aging relative to total population](<graphs/Agieng Population Canada.png>)

*Older population groups generally grew faster than total population, indicating increasing and uneven demographic pressure.*

### Hospital Capacity

![Hospital beds per 100,000 population](<graphs/Hospital Bed Growth Relative to Population.png>)

*Hospital-bed capacity declined relative to population across most provinces examined.*

### Resource Intensity & Observed Performance

![Healthcare resource intensity and observed outcome variation](<graphs/Real Healthcare Expenditure and Avoidable Hospitalizations.png>)

*Higher resource intensity does not consistently correspond with stronger observed outcomes. The relationship is descriptive and does not imply causality.*

---

## Analytical Framework:

### **Demand → Capacity → Expenditure → Access → Outcomes → Performance**

---

## Research Questions

| RQ            | Focus                                        | Analysis                                                       |
| ------------- | -------------------------------------------- | -------------------------------------------------------------- |
| **RQ1** | Population & Healthcare Demand               | [→ See Analysis](notebooks/01_RQ1_population_demand.ipynb)     |
| **RQ2** | Healthcare Resources & Capacity              | [→ See Analysis](notebooks/02_RQ2_capacity_workforce.ipynb)    |
| **RQ3** | Healthcare Expenditure & Financial Resources | [→ See Analysis](notebooks/03_RQ3_expenditure_resources.ipynb) |
| **RQ4** | Healthcare Access                            | [→ See Analysis](notebooks/04_RQ4_healthcare_access.ipynb)     |
| **RQ5** | Healthcare Outcomes                          | [→ See Analysis](notebooks/05_RQ5_healthcare_outcomes.ipynb)   |
| **RQ6** | Resource Effectiveness & System Performance  | [→ See Evaluation](notebooks/06_RQ6_system_performance.ipynb)  |

---

## Data & Analytical Approach

The project integrates healthcare data from Canadian public sources through a structured:

**Python → SQL → PostgreSQL → Analytical Dataset → Power BI**

## Sources and Workflow (End-to-end)

- **Canadian Institute for Health Information (CIHI):** healthcare expenditure, capacity, workforce, access, and outcome indicators
- **Statistics Canada:** population and demographic data

Analysis includes data acquisition and transformation, exploratory analysis, descriptive statistics, trend analysis, cross-jurisdictional comparison, resource-intensity analysis, and exploratory relationships between resources, access, and outcomes.

The findings are **descriptive and do not establish causal relationships**.

The notebooks follow the analytical sequence from **EDA → RQ1 → RQ6**, with navigation between stages.

---

## Tools

**Python · pandas · NumPy · Matplotlib · Seaborn · SQL · PostgreSQL · Power BI · Excel · Git/GitHub**

---

## Limitations

* Data availability and definitions vary across indicators and provinces.
* Some indicators have incomplete historical or jurisdictional coverage.
* Cross-jurisdictional differences may reflect factors beyond measured resource levels.
* Descriptive relationships should not be interpreted as causal effects.

## Project Status

> - **RQ1–RQ6 Analysis:** Complete

> - **RQ6 Final Synthesis:** Complete

> - **Power BI:** In Progress

| Research Area                                | Status         |
| -------------------------------------------- | -------------- |
| Population & Healthcare Demand               | ✅ Complete    |
| Healthcare Resources & Capacity              | ✅ Complete    |
| Healthcare Expenditure & Financial Resources | ✅ Complete    |
| Healthcare Access                            | ✅ Complete    |
| Healthcare Outcomes                          | ✅ Complete    |
| Resource Effectiveness & System Performance  | ✅ Complete    |
| Power BI Dashboard                           | 🔜 In Progress |

## Author

Christopher Ajayi
