import streamlit as st

st.set_page_config(page_title="5-FU Infusion Pump Calculator", layout="centered")
st.title("🧪 5-FU Infusion Pump Calculator")

# Input Fields
col1, col2 = st.columns(2)
with col1:
    # Set value to None for a blank starting input, and removed the step parameter
    dose = st.number_input("Enter Dose (mg)", min_value=0.0, value=None)
with col2:
    duration = st.selectbox("Select Duration (hr)", options=[24, 46, 48, 96, 120], index=1)

# Excel-based Formula Logic
pump_vol = ""
# Ensure dose is not None before doing comparisons
if dose is not None:
    if duration == 24:
        pump_vol = 240
    elif duration == 96:
        pump_vol = 192
    elif duration == 120:
        pump_vol = 240
    elif duration == 48:
        pump_vol = 240 if dose > 4600 else 96
    elif duration == 46:
        pump_vol = 230 if dose > 4400 else 92

# Overfill volume matching logic
vol_overfill = ""
if pump_vol == 92:
    vol_overfill = 94.0
elif pump_vol == 96:
    vol_overfill = 98.0
elif pump_vol == 192:
    vol_overfill = 195.5
elif pump_vol == 230:
    vol_overfill = 233.5
elif pump_vol == 240:
    vol_overfill = 243.5

# Math Calculations
if dose and dose > 0 and pump_vol:
    dose_overfill = dose * (vol_overfill / pump_vol)
    
    # NEW LOGIC: Round to the nearest 50
    dose_overfill_rounded = int(50 * round(dose_overfill / 50))
    
    # Concentration calculation
    concentration = dose_overfill_rounded / vol_overfill
else:
    dose_overfill = 0.0
    dose_overfill_rounded = 0
    concentration = 0.0

# Display Results
st.markdown("---")
st.subheader("Calculation Outputs")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Pump Volume", value=f"{pump_vol} mL" if pump_vol else "-")
with col_m2:
    st.metric(label="Pump Volume w/ Overfill", value=f"{vol_overfill} mL" if vol_overfill else "-")
with col_m3:
    st.metric(label="Dose w/ Overfill", value=f"{dose_overfill:.1f} mg" if dose_overfill else "-")

h_col1, h_col2 = st.columns(2)

with h_col1:
    st.info(f"**Dose w/ Overfill (Rounded to Nearest 50 mg):**\n\n ## `{dose_overfill_rounded} mg`")

with h_col2:
    st.success(f"**Final Concentration:**\n\n ## `{concentration:.1f} mg/mL`")
