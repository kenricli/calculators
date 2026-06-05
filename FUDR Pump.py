import streamlit as st
import pandas as pd

# Set up page configuration
st.set_page_config(
    page_title="HAI Pump Calculator", 
    page_icon="🩺", 
    layout="centered"
)

# --- 1. Session State Initialization for Disclaimer ---
if "disclaimer_agreed" not in st.session_state:
    st.session_state.disclaimer_agreed = None

# --- 2. Disclaimer View Logic ---
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
    
    # Bottom alignment buttons
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

# --- 3. Main Calculator Application View (Only renders if agreed) ---
else:
    # App Title and Description
    st.title("🩺 HAI Pump Calculator")
    st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
    st.write("Calculate the required FUDR dose and compounding components for **Days 1–14** based on pump type.")

    st.divider()

    # 1. Pump Type Selection Dropdown
    pump_type = st.selectbox(
        "Select Pump Type",
        options=["Intera (Codman)", "Medtronic"],
        index=0,
    )

    # Mapping pump specifications cleanly via dictionary lookup
    PUMP_SPECS = {
        "Intera (Codman)": {"volume": 30.0, "dex": "25 mg", "heparin": "30,000 units"},
        "Medtronic": {"volume": 20.0, "dex": "20 mg", "heparin": "25,000 units"}
    }

    specs = PUMP_SPECS[pump_type]
    pump_volume = specs["volume"]

    # Create three columns for neat input alignment
    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox(
            "Patient Gender",
            options=["Male", "Female"],
            index=None,
            placeholder="Select gender..."
        )
        
        # Dropdown offering default values or a custom trigger
        dose_selection = st.selectbox(
            "Starting Dose (mg/kg)", 
            options=[0.12, 0.08, 0.06, "Custom..."],
            index=0,
            format_func=lambda x: f"{x} mg/kg" if isinstance(x, (int, float)) else str(x)
        )
        
        # If "Custom..." is selected, provide a numeric input box right beneath it
        if dose_selection == "Custom...":
            dose_rate = st.number_input(
                "Enter Custom Dose (mg/kg)",
                min_value=0.00,
                max_value=2.00,
                value=None,
                format="%.2f"
                placeholder="Enter dose..."
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
        
        # Indicator using st.metric instead of an entry field
        st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

    st.divider()

    # --- Cached Calculation Logic ---
    @st.cache_data
    def calculate_fudr_dose(gender, height_cm, real_weight, dose_rate, pump_volume, flow_rate):
        # Convert height from cm to inches (1 inch = 2.54 cm)
        height_inches = height_cm / 2.54
        inches_above_5ft = max(0.0, height_inches - 60.0)
        
        # Calculate Ideal Body Weight (IBW)
        if gender == "Male":
            ibw = 50.0 + (2.3 * inches_above_5ft)
        else:
            ibw = 45.5 + (2.3 * inches_above_5ft)
            
        # Check if patient is > 35% over ideal body weight
        is_overweight = real_weight > (1.35 * ibw)
        dosing_weight = (ibw + real_weight) / 2.0 if is_overweight else real_weight
        
        # Formula: [Multiplier mg/kg * Dosing Weight kg * Pump Volume] / [Flow Rate mL/day]
        raw_fudr_dose = (dose_rate * dosing_weight * pump_volume) / flow_rate
        final_fudr_dose = round(raw_fudr_dose / 5) * 5
        
        return ibw, dosing_weight, is_overweight, raw_fudr_dose, final_fudr_dose

    # --- Conditional Layout Execution ---
    if real_weight and height_cm and gender:
        
        ibw, dosing_weight, is_overweight, raw_fudr_dose, final_fudr_dose = calculate_fudr_dose(
            gender, height_cm, real_weight, dose_rate, pump_volume, flow_rate
        )
        
        # Display dynamic context alert
        if is_overweight:
            st.warning(f"⚠️ Patient is >35% over IBW. Using **Average Body Weight**: {dosing_weight:.1f} kg (IBW: {ibw:.1f} kg).")
        else:
            st.info(f"✅ Patient weight is within standard dosing limits. Using **Actual Body Weight**: {real_weight} kg (IBW: {ibw:.1f} kg).")
            
        # --- Summary Section ---
        st.subheader("📋 Order & Compounding Summary")

        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label=f"Calculated FUDR Dose (Raw - {pump_type})", value=f"{raw_fudr_dose:.2f} mg")
        m_col2.metric(label="Final FUDR Dose (Rounded to nearest 5 mg)", value=f"{final_fudr_dose} mg")

        st.markdown("#### Total Mixture Components")

        # Render tidy interactive dataframe view
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

        # Protocol Safety Note
        st.info(
            f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a {pump_type} pump. "
            "Verify the pump's unique serial number, patient ID card, or sticker to confirm the accurate flow rate before preparation."
        )

    else:
        st.warning("⚠️ Please enter patient weight, height, and select a gender to generate the dosage calculations and compounding summary.")
