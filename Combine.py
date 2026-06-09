import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Calculator Suite", 
    page_icon="🧮", 
    layout="centered"
)

# --- 1. Session State Initialization for Navigation ---
if "active_calculator" not in st.session_state:
    st.session_state.active_calculator = "5-FU"  # Default calculator on load

# --- Epic/Beacon-Style Sidebar Navigation ---
st.sidebar.markdown("## 🧮 Calculator Suite")

# --- Made this text smaller using inline HTML styling ---
st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 500; margin-bottom: 0px;">Select a calculator below:</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Use columns or individual buttons to mimic clinical workflow selection tabs
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

st.sidebar.markdown("---")
st.sidebar.caption("v2.1.0 | Dedicated to the PCMB Team")


# ==============================================================================
# 🧬 CALCULATOR 1: SYSTEMIC INFUSION (5-FU)
# ==============================================================================
if st.session_state.active_calculator == "5-FU":
    st.title("🧪 SMARTeZ Pump Calculator")
    st.markdown("### 5-FU Dose Calculation")
    st.write("Calculate the 5-FU dose with overfill based on pump type.")

    st.divider()

    # --- Configuration Mappings ---
    OVERFILL_MAP = {
        92: 94,
        96: 98,
        192: 195.5,
        230: 233.5,
        240: 243.5
    }

    PUMP_TYPE_MAP = {
        (24, None): 'SMARTeZ 10 mL/hr 270 mL <span style="color: #2e7d32;">(Green)</span>',
        (96, None): 'SMARTeZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (120, None): 'SMARTeZ 2 mL/hr 270 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 92): 'SMARTeZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 96): 'SMARTeZ 2 mL/hr 100 mL <span style="color: #fbc02d;">(Yellow)</span>',
        (None, 230): 'SMARTeZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>',
        (None, 240): 'SMARTeZ 5 mL/hr 270 mL <span style="color: #8d6e63;">(Brown)</span>'
    }

    # --- Input Fields ---
    col1, col2 = st.columns(2)
    with col1:
        dose = st.number_input("Enter Dose (mg)", min_value=0.0, value=None, format="%g", placeholder="Enter dose...")
    with col2:
        duration = st.selectbox("Select Duration (hr)", options=[24, 46, 48, 96, 120], index=None, format_func=lambda x: f"{x} hr")
        override_pump = st.checkbox("Pump shortage? Switch to a larger pump")

    # --- Core Business Logic ---
    pump_vol = None

    if override_pump:
        if duration == 46:
            pump_vol = 230
        elif duration == 48:
            pump_vol = 240
        else:
            st.warning("⚠️ Override is only applicable for 46 hr or 48 hr durations.")
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
        st.metric(label="Pump Volume with Overfill", value=f"{vol_overfill} mL" if vol_overfill else "-")
    with col_m3:
        st.metric(label="Dose with Overfill", value=f"{dose_overfill:.1f} mg" if dose_overfill else "-")

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.info(f"**Dose with Overfill (Rounded):**\n\n ## `{dose_overfill_rounded} mg`")
    with h_col2:
        st.success(f"**Final Concentration:**\n\n ## `{concentration:.1f} mg/mL`")

    st.markdown("---")
    st.subheader("For Compounding")

    col_c1, col_c2 = st.columns(2)
    label_style = "font-size: 0.9rem; color: #ffffff;"
    value_style = "font-size: 2rem; line-height: 1.4; word-wrap: break-word; white-space: normal;"

    with col_c1:
        st.markdown(
            f'<div style="{label_style}">Pump Volume with Overfill</div>'
            f'<div style="{value_style}">{f"{vol_overfill} mL" if vol_overfill else "-"}</div>',
            unsafe_allow_html=True
        )

    with col_c2:
        st.markdown(
            f'<div style="{label_style}">Pump Type</div>'
            f'<div style="{value_style}">{pump_type if pump_type else "-"}</div>',
            unsafe_allow_html=True
        )

    st.html("<br>")

    h_col3, h_col4 = st.columns(2)
    formatted_drug_vol = f"{drug_vol:g}" if drug_vol else "0"
    formatted_ns_vol = f"{ns_vol:g}" if ns_vol else "0"

    with h_col3:
        st.info(f"**Volume of 5-FU:**\n\n ## `{formatted_drug_vol} mL`")
    with h_col4:
        st.success(f"**Volume of NS:**\n\n ## `{formatted_ns_vol} mL`")


# ==============================================================================
# 🫁 CALCULATOR 2: HEPATIC ARTERIAL INFUSION (FUDR)
# ==============================================================================
elif st.session_state.active_calculator == "FUDR":
    
    # --- Session State Initialization for Disclaimer ---
    if "disclaimer_agreed" not in st.session_state:
        st.session_state.disclaimer_agreed = None

    # --- Disclaimer View Logic ---
    if st.session_state.disclaimer_agreed is None:
        st.title("🩺 HAI Pump Calculator")
        st.subheader("⚠️ Medical Disclaimer & Terms of Use")
        
        st.warning(
            "**CRITICAL NOTICE:** This calculator is intended for reference and educational "
            "purposes only. It should not be used as the sole basis for clinical decision-making, "
            "nor should it replace professional medical judgment, hospital protocols, or independent "
            "double-checks by qualified healthcare professionals."
        )
        
        st.markdown(
            """
            By proceeding, you acknowledge and agree that:
            * You will **manually verify all dosage calculations** and drug compounding values against official protocols.
            * The creators of this tool assume no clinical or legal liability for dosing errors or patient outcomes.
            """
        )
        
        st.write("Do you agree to these terms and wish to proceed with the calculator?")
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("🤝 I Agree", use_container_width=True, type="primary"):
                st.session_state.disclaimer_agreed = True
                st.rerun()
                
        with d_col2:
            if st.button("❌ Disagree / Exit", use_container_width=True):
                st.session_state.disclaimer_agreed = False
                st.rerun()

    elif st.session_state.disclaimer_agreed is False:
        st.title("🩺 HAI Pump Calculator")
        st.error("🔒 Access Denied. You must agree to the medical disclaimer terms to utilize this calculator.")
        if st.button("Return to Disclaimer screen"):
            st.session_state.disclaimer_agreed = None
            st.rerun()

    # --- Main Calculator Application View ---
    else:
        st.title("🩺 HAI Pump Calculator")
        st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
        st.write("Calculate the required FUDR dose and compounding components for **Days 1–14** based on pump type.")

        st.divider()

        pump_type = st.selectbox(
            "Select Pump Type",
            options=["Intera (Codman)", "Medtronic"],
            index=0,
        )

        PUMP_SPECS = {
            "Intera (Codman)": {"volume": 30.0, "dex": "25 mg", "heparin": "30,000 units"},
            "Medtronic": {"volume": 20.0, "dex": "20 mg", "heparin": "25,000 units"}
        }

        specs = PUMP_SPECS[pump_type]
        pump_volume = specs["volume"]

        col1, col2, col3 = st.columns(3)

        with col1:
            gender = st.selectbox(
                "Patient Gender",
                options=["Male", "Female"],
                index=None,
                placeholder="Select gender..."
            )
            
            dose_selection = st.selectbox(
                "Starting Dose (mg/kg)", 
                options=[0.12, 0.08, 0.06, "Custom..."],
                index=0,
                format_func=lambda x: f"{x} mg/kg" if isinstance(x, (int, float)) else str(x)
            )
            
            if dose_selection == "Custom...":
                dose_rate = st.number_input(
                    "Enter Custom Dose (mg/kg)",
                    min_value=0.00,
                    max_value=2.00,
                    value=None,
                    format="%.2f",
                    placeholder="Enter dose...",
                )
            else:
                dose_rate = dose_selection

        with col2:
            real_weight = st.number_input(
                "Patient Weight (kg)", 
                min_value=0.0, 
                max_value=250.0, 
                value=None, 
                format="%g",
                placeholder="Enter weight...",
            )

            flow_rate = st.selectbox(
                "Pump Flow Rate (mL/day)", 
                options=[1.4, 1.3, 1.2, 1.1],
                index=1,
                format_func=lambda x: f"{x} mL/day"
            )

        with col3:
            height_cm = st.number_input(
                "Patient Height (cm)",
                min_value=0.0,
                max_value=250.0,
                value=None,
                format="%g",
                placeholder="Enter height..."
            )
            
            st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

        st.divider()

        # --- Cached Calculation Logic ---
        @st.cache_data
        def calculate_fudr_dose(gender, height_cm, real_weight, dose_rate, pump_volume, flow_rate):
            height_inches = height_cm / 2.54
            inches_above_5ft = max(0.0, height_inches - 60.0)
            
            if gender == "Male":
                ibw = 50.0 + (2.3 * inches_above_5ft)
            else:
                ibw = 45.5 + (2.3 * inches_above_5ft)
                
            is_overweight = real_weight > (1.35 * ibw)
            dosing_weight = (ibw + real_weight) / 2.0 if is_overweight else real_weight
            
            raw_fudr_dose = (dose_rate * dosing_weight * pump_volume) / flow_rate
            final_fudr_dose = round(raw_fudr_dose / 5) * 5
            
            return ibw, dosing_weight, is_overweight, raw_fudr_dose, final_fudr_dose

        # --- Conditional Layout Execution ---
        if real_weight and height_cm and gender:
            
            ibw, dosing_weight, is_overweight, raw_fudr_dose, final_fudr_dose = calculate_fudr_dose(
                gender, height_cm, real_weight, dose_rate, pump_volume, flow_rate
            )
            
            if is_overweight:
                st.warning(f"⚠️ Patient is >35% over IBW. Using **Average Body Weight**: {dosing_weight:.1f} kg (IBW: {ibw:.1f} kg).")
            else:
                st.info(f"✅ Patient weight is within standard dosing limits. Using **Actual Body Weight**: {real_weight} kg (IBW: {ibw:.1f} kg).")
                
            st.subheader("📋 Order & Compounding Summary")

            m_col1, m_col2 = st.columns(2)
            m_col1.metric(label=f"Calculated FUDR Dose (Raw - {pump_type})", value=f"{raw_fudr_dose:.2f} mg")
            m_col2.metric(label="Final FUDR Dose (Rounded to nearest 5 mg)", value=f"{final_fudr_dose} mg")

            st.markdown("#### Total Mixture Components")

            df_components = pd.DataFrame({
                "Component": ["FUDR", "Dexamethasone", "Heparin", "Normal Saline (NS)"],
                "Target Protocol Dose / Volume": [
                    f"{final_fudr_dose} mg",
                    specs["dex"],
                    specs["heparin"],
                    f"Quantity sufficient (QS) to total {int(pump_volume)} mL"
                ]
            })
            st.dataframe(df_components, hide_index=True, use_container_width=True)

            st.info(
                f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a {pump_type} pump. "
                "Verify the pump's unique serial number, patient ID card, or sticker to confirm the accurate flow rate before preparation."
            )

        else:
            st.warning("⚠️ Please enter patient weight, height, and select a gender to generate the dosage calculations and compounding summary.")
