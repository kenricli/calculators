import streamlit as st

# Set up page configuration
st.set_page_config(
    page_title="FUDR Pump Dose Calculator", 
    page_icon="🩺", 
    layout="centered"
)

# App Title and Description
st.title("🩺 FUDR Pump Dose Calculator")
st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
st.write("Calculate the required FUDR dose and compounding components for **Days 1–14** based on pump type.")

st.divider()

# 1. Pump Type Selection Dropdown
pump_type = st.selectbox(
    "Select Pump Type",
    options=["Intera (Codman)", "Medtronic"],
    index=0,
)

# Dynamically set pump volume and baseline components based on the selected type
if pump_type == "Intera (Codman)":
    pump_volume = 30.0
    dex_dose = "25 mg"
    heparin_dose = "30,000 units"
else:  # Medtronic
    pump_volume = 20.0
    dex_dose = "20 mg"
    heparin_dose = "25,000 units"

# Create three columns for neat input alignment
col1, col2, col3 = st.columns(3)

with col1:
    # Patient Weight Input (Real Weight)
    real_weight = st.number_input(
        "Patient Weight (kg)", 
        min_value=0.0, 
        max_value=250.0, 
        value=None,  # This leaves the input field empty on load
        format="%g",
        placeholder="Enter weight...",
    )
    
    # Dosing Multiplier Dropdown
    dose_rate = st.selectbox(
        "Dosing Multiplier (mg/kg)", 
        options=[0.12, 0.08, 0.06],
        index=0,
        format_func=lambda x: f"{x} mg/kg"
    )

with col2:
    # Gender selection for IBW calculation
    gender = st.selectbox(
        "Patient Gender",
        options=["Male", "Female"],
        index=0
    )

    # Pump Flow Rate Dropdown
    flow_rate = st.selectbox(
        "Pump Flow Rate (mL/day)", 
        options=[1.4, 1.3, 1.2, 1.1],
        index=1,
        format_func=lambda x: f"{x} mL/day"
    )

with col3:
    # Height input in cm
    height_cm = st.number_input(
        "Patient Height (cm)",
        min_value=0.0,
        max_value=250.0,
        value=None,
        format="%g",
        placeholder="Enter height..."
    )
    
    # Dynamic Pump Volume Visual Indicator
    st.text_input("Pump Volume (Fixed)", value=f"{int(pump_volume)} mL", disabled=True)

st.divider()

# --- Calculations & Conditional Layout ---
# Ensure calculations only run if valid weight and height have been explicitly entered
if real_weight is not None and real_weight > 0 and height_cm is not None and height_cm > 0:
    
    # 1. Convert height from cm to inches (1 inch = 2.54 cm)
    height_inches = height_cm / 2.54
    
    # Calculate inches above 5 feet (5 feet = 60 inches)
    inches_above_5ft = max(0.0, height_inches - 60.0)
    
    # 2. Calculate Ideal Body Weight (IBW) based on gender formulas provided
    if gender == "Male":
        ibw = 50.0 + (2.3 * inches_above_5ft)
    else:  # Female
        ibw = 45.5 + (2.3 * inches_above_5ft)
        
    # 3. Determine Dosing Weight based on Overweight condition (Weight > 35% above IBW)
    is_overweight = real_weight > (1.35 * ibw)
    
    if is_overweight:
        # Calculate Average Body Weight (ABW)
        dosing_weight = (ibw + real_weight) / 2.0
        weight_status_msg = f"⚠️ Patient is >35% over IBW. Using **Average Body Weight (ABW)**: {dosing_weight:.1f} kg (IBW: {ibw:.1f} kg)."
    else:
        dosing_weight = real_weight
        weight_status_msg = f"✅ Patient weight is within standard dosing limits. Using **Actual Weight**: {real_weight} kg (IBW: {ibw:.1f} kg)."
        
    # Show weight adjustment status to user
    st.info(weight_status_msg)
    
    # 4. Formula: [Multiplier mg/kg * Dosing Weight kg * Pump Volume] / [Flow Rate mL/day]
    raw_fudr_dose = (dose_rate * dosing_weight * pump_volume) / flow_rate
    
    # Round to the nearest 5 mg
    final_fudr_dose = round(raw_fudr_dose / 5) * 5

    # --- Summary Section ---
    st.subheader("📋 Order & Compounding Summary")

    # Metrics Display
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(
        label=f"Calculated FUDR Dose (Raw - {pump_type})", 
        value=f"{raw_fudr_dose:.2f} mg"
    )
    m_col2.metric(
        label="Final FUDR Dose (Rounded to nearest 5 mg)", 
        value=f"{final_fudr_dose} mg",
        delta=f"{final_fudr_dose - raw_fudr_dose:+.2f} mg rounding adjustment",
        delta_color="off"
    )

    # Display standard mixture table
    st.markdown(f"#### Total Mixture Components")

    components_data = {
        "Component": ["FUDR", "Dexamethasone", "Heparin", "Normal Saline (NS)"],
        "Target Protocol Dose / Volume": [
            f"{final_fudr_dose} mg",
            dex_dose,
            heparin_dose,
            f"Quantity sufficient (QS) to total {int(pump_volume)} mL"
        ]
    }

    st.table(components_data)

    # Protocol Note
    st.info(
        f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a {pump_type} pump. "
        "Verify the pump's unique serial number, patient ID card, or sticker to confirm the accurate flow rate before preparation."
    )

else:
    # Message displayed when vital input metrics are missing
    st.warning("⚠️ Please enter both patient weight and height to generate the dosage calculations and compounding summary.")
