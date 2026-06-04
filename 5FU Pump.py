import streamlit as st

st.set_page_config(page_title="5-FU Infusion Pump Calculator", layout="centered")
st.title("🧪 5-FU Infusion Pump Calculator")

# --- Configuration Mappings ---
OVERFILL_MAP = {
    92: 94,
    96: 98,
    192: 195.5,
    230: 233.5,
    240: 243.5
}

PUMP_TYPE_MAP = {
    (24, None): 'SmartEZ 10 mL/hr 270 mL <span style="color: #2e7d32;">(Green)</span>',
    (96, None): 'SmartEZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
    (120, None): 'SmartEZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
    (None, 92): 'SmartEZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
    (None, 96): 'SmartEZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
    (None, 230): 'SmartEZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>',
    (None, 240): 'SmartEZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>'
}

# --- Input Fields ---
col1, col2 = st.columns(2)
with col1:
    dose = st.number_input("Enter Dose (mg)", min_value=0.0, value=None, format="%g")
with col2:
    duration = st.selectbox("Select Duration (hr)", options=[24, 46, 48, 96, 120], index=2)
    override_pump = st.checkbox("Pump Shortage? Override Pump Volume!")

# --- Core Business Logic ---
pump_vol = None

if override_pump:
    if duration == 46:
        pump_vol = 230
    elif duration == 48:
        pump_vol = 240
    else:
        st.warning("Override is only applicable for 46 hr or 48 hr durations.")
        override_pump = False

# Fall back to standard logic if override isn't active/applicable
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

# Get overfill volume using dict lookup
vol_overfill = OVERFILL_MAP.get(pump_vol)

# Get pump type using dict lookup (checking duration first, then pump volume)
pump_type = PUMP_TYPE_MAP.get((duration, None)) or PUMP_TYPE_MAP.get((None, pump_vol), "")

# --- Mathematical Calculations ---
if dose and dose > 0 and pump_vol and vol_overfill:
    dose_overfill = dose * (vol_overfill / pump_vol)
    dose_overfill_rounded = int(50 * round(dose_overfill / 50))
    concentration = dose_overfill_rounded / vol_overfill
    drug_vol = dose_overfill_rounded / 50
    ns_vol = vol_overfill - drug_vol
else:
    dose_overfill = 0.0
    dose_overfill_rounded = 0
    concentration = 0.0
    drug_vol = 0
    ns_vol = 0

# --- UI Display ---
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

col_c1, col_c2 = st.columns(2)
label_style = "font-size: 0.9rem; color: #ffffff;"
value_style = "font-size: 2rem; line-height: 1.4; word-wrap: break-word; white-space: normal;"

with col_c1:
    st.markdown(
        f'<div style="{label_style}">Pump Volume w/ Overfill</div>'
        f'<div style="{value_style}">{f"{vol_overfill} mL" if vol_overfill else "-"}</div>',
        unsafe_allow_html=True
    )

with col_c2:
    st.markdown(
        f'<div style="{label_style}">Pump Type</div>'
        f'<div style="{value_style}">{pump_type if pump_type else "-"}</div>',
        unsafe_allow_html=True
    )

# Clean spacing replacement for st.space()
st.html("<br>")

h_col3, h_col4 = st.columns(2)
formatted_drug_vol = f"{drug_vol:g}" if drug_vol else "0"
formatted_ns_vol = f"{ns_vol:g}" if ns_vol else "0"

with h_col3:
    st.info(f"**Volume of 5-FU:**\n\n ## `{formatted_drug_vol} mL`")
with h_col4:
    st.success(f"**Volume of NS:**\n\n ## `{formatted_ns_vol} mL`")
