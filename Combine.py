import streamlit as st
import pandas as pd
import math

# --- Page Configuration ---
st.set_page_config(
    page_title="Oncology Calculator Suite", 
    page_icon="🧮", 
    layout="centered"
)

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
    "🧪 Systemic Infusion (5-FU)", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "5-FU" else "secondary"
):
    st.session_state.active_calculator = "5-FU"
    st.rerun()

if st.sidebar.button(
    "🩺 Hepatic Arterial Infusion (FUDR)", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "FUDR" else "secondary"
):
    st.session_state.active_calculator = "FUDR"
    st.rerun()

if st.sidebar.button(
    "🩻 Anthropometrics & BSA Suite", 
    use_container_width=True, 
    type="primary" if st.session_state.active_calculator == "BSA" else "secondary"
):
    st.session_state.active_calculator = "BSA"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("v2.2.0 | Clinical Decision Support Tool")


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
    if "disclaimer_agreed" not in st.session_state:
        st.session_state.disclaimer_agreed = None

    if st.session_state.disclaimer_agreed is None:
        st.title("🩺 HAI Pump Calculator")
        st.subheader("⚠️ Medical Disclaimer & Terms of Use")
        st.warning("**CRITICAL NOTICE:** This calculator is intended for reference and educational purposes only...")
        st.markdown("""
            By proceeding, you acknowledge and agree that:
            * You will **manually verify all dosage calculations** against official protocols.
            """)
        d_col1, d_col2 = st.columns(2)
        if d_col1.button("🤝 I Agree", use_container_width=True, type="primary"):
            st.session_state.disclaimer_agreed = True
            st.rerun()
        if d_col2.button("❌ Disagree / Exit", use_container_width=True):
            st.session_state.disclaimer_agreed = False
            st.rerun()
    elif st.session_state.disclaimer_agreed is False:
        st.title("🩺 HAI Pump Calculator")
        st.error("🔒 Access Denied. You must agree to the medical disclaimer terms.")
        if st.button("Return to Disclaimer screen"):
            st.session_state.disclaimer_agreed = None
            st.rerun()
    else:
        st.title("🩺 HAI Pump Calculator")
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
            dose_selection = st.selectbox("Starting Dose (mg/kg)", options=[0.12, 0.08, 0.06, "Custom..."], index=0)
            dose_rate = st.number_input("Enter Custom Dose (mg/kg)", min_value=0.00, max_value=2.00, value=None) if dose_selection == "Custom..." else dose_selection
        with col2:
            real_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=250.0, value=None, placeholder="Enter weight...")
            flow_rate = st.selectbox("Pump Flow Rate (mL/day)", options=[1.4, 1.3, 1.2, 1.1], index=1, format_func=lambda x: f"{x} mL/day")
        with col3:
            height_cm = st.number_input("Patient Height (cm)", min_value=0.0, max_value=250.0, value=None, placeholder="Enter height...")
            st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

        st.divider()

        if real_weight and height_cm and gender:
            height_inches = height_cm / 2.54
            inches_above_5ft = max(0.0, height_inches - 60.0)
            ibw = (50.0 if gender == "Male" else 45.5) + (2.3 * inches_above_5ft)
            is_overweight = real_weight > (1.35 * ibw)
            dosing_weight = (ibw + real_weight) / 2.0 if is_overweight else real_weight
            
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


# ==============================================================================
# 🩻 CALCULATOR 3: ANTHROPOMETRICS & BSA SUITE
# ==============================================================================
elif st.session_state.active_calculator == "BSA":
    st.title("🩻 Anthropometrics & BSA Suite")
    st.markdown("### Patient Weight & BSA Indexing")
    st.write("Simultaneously evaluate Body Surface Area (BSA) across multiple foundational oncological equations.")

    st.divider()

    # --- Input Fields ---
    col1, col2, col3 = st.columns(3)
    with col1:
        bsa_gender = st.selectbox("Patient Gender", options=["Male", "Female"], index=None, placeholder="Select gender...")
    with col2:
        bsa_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, value=None, format="%g", placeholder="Enter weight...")
    with col3:
        bsa_height = st.number_input("Patient Height (cm)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter height...")

    st.divider()

    if bsa_gender and bsa_weight and bsa_height:
        # --- Mathematical Calculations ---
        # 1. BSA Formulas
        bsa_mosteller = math.sqrt((bsa_height * bsa_weight) / 3600)
        bsa_dubois = 0.007184 * (bsa_height ** 0.725) * (bsa_weight ** 0.425)
        bsa_haycock = 0.024265 * (bsa_height ** 0.3964) * (bsa_weight ** 0.5378)
        bsa_gehan = 0.0235 * (bsa_height ** 0.42246) * (bsa_weight ** 0.51456)
        
        # 2. Weight Calculations (Devine Formula for IBW)
        height_in = bsa_height / 2.54
        inches_over_5ft = max(0.0, height_in - 60.0)
        
        if bsa_gender == "Male":
            ibw_val = 50.0 + (2.3 * inches_over_5ft)
        else:
            ibw_val = 45.5 + (2.3 * inches_over_5ft)
            
        # Adjusted Body Weight (AdjBW)
        adj_weight_val = ibw_val + 0.4 * (bsa_weight - ibw_val)
        percent_ibw = (bsa_weight / ibw_val) * 100

        # --- Context Alerts ---
        if bsa_weight > (1.2 * ibw_val):
            st.warning(f"⚠️ Patient is obese or overweight (>120% of IBW at **{percent_ibw:.1f}%**). Consider utilizing **Adjusted Body Weight** for chemotherapy regimens requiring weight-based adjustments.")
        else:
            st.info(f"✅ Patient weight profile is within standard limits (**{percent_ibw:.1f}%** of Ideal Body Weight).")

        # --- UI Metrics Display ---
        st.subheader("📋 Clinician Weight Workspace")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(label="Ideal Body Weight (IBW)", value=f"{ibw_val:.2f} kg")
        m_col2.metric(label="Adjusted Body Weight (AdjBW)", value=f"{adj_weight_val:.2f} kg")
        m_col3.metric(label="Percent of IBW", value=f"{percent_ibw:.1f} %")

        # --- Comparison Frame View ---
        st.markdown("#### BSA Multi-Equation Matrix")
        
        df_bsa = pd.DataFrame({
            "BSA Mathematical Formula": [
                "Mosteller (Oncology Standard)", 
                "DuBois & DuBois", 
                "Haycock (Validated for Pediatrics/Extreme Heights)", 
                "Gehan & George"
            ],
            "Calculated Index Value": [
                f"{bsa_mosteller:.3f} m²",
                f"{bsa_dubois:.3f} m²",
                f"{bsa_haycock:.3f} m²",
                f"{bsa_gehan:.3f} m²"
            ]
        })
        st.dataframe(df_bsa, hide_index=True, use_container_width=True)
        
        st.info("💡 **Clinical Note:** Mosteller remains the default calculation model used across modern Electronic Health Records (EHR) networks for standard surface-area-based chemotherapeutic indexing.")
    else:
        st.warning("⚠️ Please provide Patient Gender, Weight, and Height inputs to verify biometric index values.")
