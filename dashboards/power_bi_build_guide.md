# Power BI build guide

Load `data/processed/india_health_facilities.csv` as `Facilities`. Set latitude and longitude to decimal number and assign the Latitude and Longitude data categories. Keep state, district, subdistrict, facility type, location type, and ownership type as text dimensions.

## Page 1: national overview

Use cards for total facilities, state count, district count, mapping percentage, and public facility percentage. Add a state ranking bar, facility type mix, location type split, and a quality callout.

## Page 2: geographic access explorer

Use latitude and longitude on a map with facility name in the tooltip, state and district slicers, and facility type as the legend. Add a detail table for state, district, subdistrict, facility name, ownership type, and completeness.

## Page 3: state comparison

Use a state matrix with total facilities, mapped percentage, public percentage, distinct districts, and average completeness. Add a drill-through destination for district and subdistrict details.

## Page 4: data quality

Show invalid-coordinate exclusions, missing administrative fields, duplicate signatures removed, and completeness distribution. Keep the directory date and interpretation boundary visible on every page.

The source is an historical directory snapshot. Dashboard labels must not imply live availability, current staffing, bed capacity, emergency readiness, or clinical quality.
