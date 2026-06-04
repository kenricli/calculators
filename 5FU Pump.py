import streamlit as st

st.set_page_config(page_title="5-FU Infusion Pump Calculator", layout="centered")
st.title("🧪 5-FU Infusion Pump Calculator")

# Input Fields
col1, col2 = st.columns(2)
with col1:
    # Set value to None for a blank starting input.
    # Using format="%g" strips trailing zeros for whole numbers but preserves decimals.
    dose = st.number_input("Enter Dose (mg)", min_value=0.0, value=None, format="%g")
with col2:
    duration = st.selectbox("Select Duration (hr)", options=[24, 46, 48, 96, 120], index=2)
    
    # Updated Checkbox Label to reflect the dynamic logic
    override_pump = st.checkbox("Pump Shortage? Override Pump Volume!")

# Excel-based Formula Logic
pump_vol = ""

# Updated Logic: Check the override conditions first based on selected duration
if override_pump:
    if duration == 46:
        pump_vol = 230
    elif duration == 48:
        pump_vol = 240
    else:
        # Visual cue in case someone checks the box on an unsupported duration
        st.warning("Override is only applicable for 46 hr or 48 hr durations.")
        override_pump = False  # Deactivate logic fallback

# Standard logic runs if override is not checked or not applicable
if not override_pump and dose is not None:
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
    vol_overfill = 94
elif pump_vol == 96:
    vol_overfill = 98
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

    drug_vol = dose_overfill_rounded / 50

    ns_vol = vol_overfill - drug_vol
else:
    dose_overfill = 0.0
    dose_overfill_rounded = 0
    concentration = 0.0
    drug_vol = 0
    ns_vol = 0

# Display Results
st.markdown("---")
st.subheader("For Verification")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Pump Volume", value=f"{pump_vol} mL" if pump_vol else "-")
with col_m2:
    st.metric(label="Pump Volume w/ Overfill", value=f"{vol_overfill} mL" if vol_overfill else "-")
with col_m3:
    st.metric(label="Dose w/ Overfill", value=f"{dose_overfill:.1f} mg" if dose_overfill else "-")

h_col1, h_col2 = st.columns(2)

with h_col1:
    st.info(f"**Dose w/ Overfill (Rounded):**\n\n ## `{dose_overfill_rounded} mg`")

with h_col2:
    st.success(f"**Final Concentration:**\n\n ## `{concentration:.1f} mg/mL`")

st.markdown("---")
st.subheader("For Compounding")

h_col1, h_col2 = st.columns(2)

# Formatted variables using :g to dynamically remove trailing zeros
formatted_drug_vol = f"{drug_vol:g}" if drug_vol else "0"
formatted_ns_vol = f"{ns_vol:g}" if ns_vol else "0"

with h_col1:
    st.info(f"**Volume of 5-FU:**\n\n ## `{formatted_drug_vol} mL`")

with h_col2:
    st.success(f"**Volume of NS:**\n\n ## `{formatted_ns_vol} mL`")
