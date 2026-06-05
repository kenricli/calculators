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

# Dynamically set pump volume based on the selected type
if pump_type == "Intera (Codman)":
    pump_volume = 30.0
else:  # Medtronic
    pump_volume = 20.0

# Create two columns for neat input alignment
col1, col2 = st.columns(2)

with col1:
    # Patient Weight Input (Set to None/blank by default)
    weight = st.number_input(
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
    # Pump Flow Rate Dropdown
    flow_rate = st.selectbox(
        "Pump Flow Rate (mL/day)", 
        options=[1.4, 1.3, 1.2, 1.1],
        index=1,
        format_func=lambda x: f"{x} mL/day"
    )
    
    # Dynamic Pump Volume Visual Indicator
    st.text_input("Pump Volume (Fixed for selected pump)", value=f"{int(pump_volume)} mL", disabled=True)

st.divider()

# --- Calculations & Conditional Layout ---
# Ensure calculations only run if a valid weight has been explicitly entered
if weight is not None and weight > 0:
    
    # Formula derived from image_d3ae29.png: 
    # [Multiplier mg/kg * Weight kg * Pump Volume] / [Flow Rate mL/day]
    raw_fudr_dose = (dose_rate * weight * pump_volume) / flow_rate
    
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

    # Display standard mixture table modeled after image_d3ae29.png protocol
    st.markdown(f"#### Total Mixture Components (Qs to {int(pump_volume)} mL)")

    components_data = {
        "Component": ["FUDR", "Dexamethasone", "Heparin", "Normal Saline (NS)"],
        "Target Protocol Dose / Volume": [
            f"{final_fudr_dose} mg",
            "25 mg (Flat dose)",
            "30,000 units",
            f"Quantity sufficient (Qs) to total {int(pump_volume)} mL"
        ]
    }

    st.table(components_data)

    # Protocol Note
    st.info(
        f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a {pump_type} pump. "
        "Verify the pump's unique serial number, patient ID card, or sticker to confirm the accurate flow rate before preparation."
    )

else:
    # Message displayed when the weight field is empty
    st.warning("⚠️ Please enter a patient weight to generate the dosage calculations and compounding summary.")
