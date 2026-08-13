# Power BI build guide

Load `data/processed/telangana_health_facilities.csv` as `Facilities`. Set latitude and longitude to decimal number and mark their data categories as Latitude and Longitude. Use district, facility type, and source layer as categorical dimensions.

The overview page uses four KPI cards, a facility type bar chart, a district ranking chart, and two data quality bars. A separate map page can use facility name as the tooltip and facility type as the legend. The measures in `measures.dax` provide the core calculations.

The source describes published records. Dashboard labels must not imply current staffing, bed availability, service quality, or emergency readiness.

