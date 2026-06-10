import streamlit as st
import pandas as pd
import math

# --- Page Configuration ---
st.set_page_config(
    page_title="Oncology Calculator Suite", 
    page_icon="🧮", 
    layout="centered"
)


# ==============================================================================
# 🧮 HELPER FUNCTIONS (CARBOPLATIN AUC)
# ==============================================================================
def calculate_bmi(weight_kg, height_cm):
    """Calculates Body Mass Index (BMI)."""
    if height_cm and height_cm > 0:
        return weight_kg / ((height_cm / 100) ** 2)
    return 0


def calculate_ibw(gender, height_cm):
    """Calculates Ideal Body Weight (IBW) using Devine Formula."""
    if not height_cm:
        return 0
    height_in_inches = height_cm / 2.54
    if height_in_inches < 60:
        height_in_inches = 60

    if gender == "Male":
        return 50.0 + 2.3 * (height_in_inches - 60)
    else:  # Female
        return 45.5 + 2.3 * (height_in_inches - 60)


def calculate_adjusted_weight(actual_weight, ibw):
    """Calculates Adjusted Body Weight (AjBW) using a 40% correction factor."""
    return ibw + 0.4 * (actual_weight - ibw)


def calculate_crcl(gender, age, dosing_weight, scr):
    """Calculates Creatinine Clearance (CrCl) using Cockcroft-Gault."""
    if not scr or scr <= 0 or not age or age <= 0:
        return 0

    crcl = ((140 - age) * dosing_weight) / (72 * scr)

    if gender == "Female":
        crcl *= 0.85

    return crcl


def format_trailing(value, precision=1):
    """Formats a float to remove trailing zeros and unnecessary decimal points."""
    rounded = round(value, precision)
    if rounded.is_integer():
        return f"{int(rounded)}"
    return f"{rounded}".rstrip("0").rstrip(".")


# --- 1. Session State Initialization for Navigation ---
if "active_calculator" not in st.session_state:
    st.session_state.active_calculator = "5-FU"  # Default calculator on load

# --- Epic/Beacon-Style Sidebar Navigation ---
st.sidebar.markdown("## 🧮 Oncology Clinical Suite")

# Small font-size line style preserved 
st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 500; margin-bottom: 0px;">Select a calculator below:</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation Button Tabs
if st.sidebar.button(
    "🧪 SMARTeZ Pump Calculator", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "5-FU" else "secondary"
):
    st.session_state.active_calculator = "5-FU"
    st.rerun()

if st.sidebar.button(
    "💉 HAI Pump Calculator", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "FUDR" else "secondary"
):
    st.session_state.active_calculator = "FUDR"
    st.rerun()

if st.sidebar.button(
    "💊 Carboplatin AUC Calculator", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "Carboplatin" else "secondary"
):
    st.session_state.active_calculator = "Carboplatin"
    st.rerun()

if st.sidebar.button(
    "📏 Weight & BSA", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "BSA" else "secondary"
):
    st.session_state.active_calculator = "BSA"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("v2.2.1 | Clinical Decision Support Tool")


# ==============================================================================
# 🧬 CALCULATOR 1: SYSTEMIC INFUSION (5-FU)
# ==============================================================================
if st.session_state.active_calculator == "5-FU":
    st.title("🧪 SMARTeZ Pump Calculator")
    st.markdown("### 5-FU Dose Calculation")
    st.write("Calculate the 5-FU dose with overfill based on pump type.")

    st.divider()

    OVERFILL_MAP = {92: 94, 96: 98, 192: 195.5, 230: 233.5, 240: 243.5}
    PUMP_TYPE_MAP = {
        (24, None): 'SMARTeZ 10 mL/hr 270 mL <span style="color: #2e7d32;">(Green)</span>',
        (96, None): 'SMARTeZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (120, None): 'SMARTeZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 92): 'SMARTeZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 96): 'SMARTeZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 230): 'SMARTeZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>',
        (None, 240): 'SMARTeZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>'
    }

    col1, col2 = st.columns(2)
    with col1:
        dose = st.number_input("Enter Dose (mg)", min_value=0.0, value=None, format="%g", placeholder="Enter dose...")
    with col2:
        duration = st.selectbox("Select Duration (hr)", options=[24, 46, 48, 96, 120], index=None, format_func=lambda x: f"{x} hr")
        override_pump = st.checkbox("Pump shortage? Switch to a larger pump")

    # --- Conditional UI Display based on user input ---
    if not dose or not duration:
        st.warning("⚠️ Please enter dose and select a duration to generate the dosage calculations.")
    else:
        pump_vol = None
        if override_pump:
            if duration == 46: pump_vol = 230
            elif duration == 48: pump_vol = 240
            else:
                st.warning("⚠️ Override is only applicable for 46 hr or 48 hr durations.")
                override_pump = False

        if not override_pump and dose is not None:
            if duration == 24: pump_vol = 240
            elif duration == 96: pump_vol = 192
            elif duration == 120: pump_vol = 240
            elif duration == 48: pump_vol = 240 if dose > 4600 else 96
            elif duration == 46: pump_vol = 230 if dose > 4400 else 92

        vol_overfill = OVERFILL_MAP.get(pump_vol)
        pump_type = PUMP_TYPE_MAP.get((duration, None)) or PUMP_TYPE_MAP.get((None, pump_vol), "")

        if dose and dose > 0 and pump_vol and vol_overfill:
            dose_overfill = dose * (vol_overfill / pump_vol)
            dose_overfill_rounded = int(50 * round(dose_overfill / 50))
            concentration = dose_overfill_rounded / vol_overfill
            drug_vol = dose_overfill_rounded / 50
            ns_vol = vol_overfill - drug_vol
        else:
            dose_overfill, dose_overfill_rounded, concentration, drug_vol, ns_vol = 0.0, 0, 0.0, 0, 0

        st.markdown("---")
        st.subheader("For Verification")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(label="Pump Volume", value=f"{pump_vol} mL" if pump_vol else "-")
        col_m2.metric(label="Pump Volume with Overfill", value=f"{vol_overfill} mL" if vol_overfill else "-")
        col_m3.metric(label="Dose with Overfill", value=f"{dose_overfill:.1f} mg" if dose_overfill else "-")

        h_col1, h_col2 = st.columns(2)
        h_col1.info(f"**Dose with Overfill (Rounded):**\n\n ## `{dose_overfill_rounded} mg`")
        h_col2.success(f"**Final Concentration:**\n\n ## `{concentration:.1f} mg/mL`")

        st.markdown("---")
        st.subheader("For Compounding")
        col_c1, col_c2 = st.columns(2)
        label_style, value_style = "font-size: 0.9rem; color: #ffffff;", "font-size: 2rem; line-height: 1.4; word-wrap: break-word; white-space: normal;"
        col_c1.markdown(f'<div style="{label_style}">Pump Volume with Overfill</div><div style="{value_style}">{f"{vol_overfill} mL" if vol_overfill else "-"}</div>', unsafe_allow_html=True)
        col_c2.markdown(f'<div style="{label_style}">Pump Type</div><div style="{value_style}">{pump_type if pump_type else "-"}</div>', unsafe_allow_html=True)
        
        st.html("<br>")
        h_col3, h_col4 = st.columns(2)
        h_col3.info(f"**Volume of 5-FU:**\n\n ## `{f'{drug_vol:g}' if drug_vol else '0'} mL`")
        h_col4.success(f"**Volume of NS:**\n\n ## `{f'{ns_vol:g}' if ns_vol else '0'} mL`")


# ==============================================================================
# 🫁 CALCULATOR 2: HEPATIC ARTERIAL INFUSION (FUDR)
# ==============================================================================
elif st.session_state.active_calculator == "FUDR":
    st.title("💉 HAI Pump Calculator")
    st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
    st.divider()

    pump_type = st.selectbox("Select Pump Type", options=["Intera (Codman)", "Medtronic"], index=0)
    PUMP_SPECS = {
        "Intera (Codman)": {"volume": 30.0, "dex": "25 mg", "heparin": "30,000 units"},
        "Medtronic": {"volume": 20.0, "dex": "20 mg", "heparin": "25,000 units"}
    }
    specs = PUMP_SPECS[pump_type]
    pump_volume = specs["volume"]

    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Patient Gender", options=["Male", "Female"], index=None, placeholder="Select gender...")
        dose_selection = st.selectbox("Starting Dose (mg/kg)", options=[0.12, 0.08, 0.06, "Custom..."], index=0, format_func=lambda x: f"{x} mg/kg")
        dose_rate = st.number_input("Enter Custom Dose (mg/kg)", min_value=0.00, max_value=2.00, value=None) if dose_selection == "Custom..." else dose_selection
    with col2:
        real_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter weight...")
        flow_rate = st.selectbox("Pump Flow Rate (mL/day)", options=[1.4, 1.3, 1.2, 1.1], index=1, format_func=lambda x: f"{x} mL/day")
    with col3:
        height_cm = st.number_input("Patient Height (cm)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter height...")
        st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

    st.divider()

    if real_weight and height_cm and gender and dose_rate is not None:
        height_inches = height_cm / 2.54
        inches_above_5ft = max(0.0, height_inches - 60.0)
        ibw = (50.0 if gender == "Male" else 45.5) + (2.3 * inches_above_5ft)
        is_overweight = real_weight > (1.35 * ibw)
        dosing_weight = (ibw + real_weight) / 2.0 if is_overweight else real_weight
        
        # --- Calculations for Output Message ---
        daily_dose = dose_rate * dosing_weight
        pump_concentration = daily_dose / flow_rate
        
        raw_fudr_dose = (dose_rate * dosing_weight * pump_volume) / flow_rate
        final_fudr_dose = round(raw_fudr_dose / 5) * 5
        
        if is_overweight:
            st.warning(f"⚠️ Patient is >35% over IBW. Using **Average Body Weight**: {dosing_weight:.1f} kg.")
        else:
            st.info(f"✅ Using **Actual Body Weight**: {real_weight} kg.")
                  
        st.subheader("📋 Order & Compounding Summary")
        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label="Calculated FUDR Dose", value=f"{raw_fudr_dose:.2f} mg")
        m_col2.metric(label="Final FUDR Dose (Nearest 5 mg)", value=f"{final_fudr_dose} mg")

        df_components = pd.DataFrame({
            "Component": ["FUDR", "Dexamethasone", "Heparin", "Normal Saline (NS)"],
            "Target Protocol Dose / Volume": [f"{final_fudr_dose} mg", specs["dex"], specs["heparin"], f"QS to total {int(pump_volume)} mL"]
        })
        st.dataframe(df_components, hide_index=True, use_container_width=True)

        # Build clean string version for clipboard copying
        clean_admin_text = (
            f"1. Floxuridine dose: {dose_rate:g} mg/kg/day × {dosing_weight:g} kg = Daily dose of Floxuridine: {daily_dose:.2f} mg/day\\n"
            f"2. Daily dose of Floxuridine: {daily_dose:.2f} mg/day / flow rate: {flow_rate} mL/day = pump concentration: {pump_concentration:.2f} mg/mL\\n"
            f"3. Pump concentration: {pump_concentration:.2f} mg/mL × pump volume: {int(pump_volume)} mL = total dose of FLOXURIDINE: {final_fudr_dose} mg (rounded to closest 5 mg)\\n"
            f"4. Please insert total dose into Floxuridine dosing field above"
        )

        # --- Layout Header and Copy Button seamlessly ---
        title_col, btn_col = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with title_col:
            st.subheader("✏️ To Fill Out Admin Instructions")
        with btn_col:
            escaped_text = clean_admin_text.replace("'", "\\'").replace("\n", "\\n")
            
            html_button = f"""
            <button onclick="navigator.clipboard.writeText('{escaped_text}'); this.innerText='Copied!';" 
                    style="
                        width: 100%;
                        background-color: #262730;
                        color: #ffffff;
                        border: 1px solid rgba(250, 250, 250, 0.2);
                        padding: 6px 12px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                        height: 38px;
                    ">
                📋 Copy Text
            </button>
            """
            st.components.v1.html(html_button, height=45)

        admin_text = (
            f"1. **Floxuridine dose:** {dose_rate:
