import streamlit as st
import pandas as pd
from nav import render_sidebar_nav

st.set_page_config(
    page_title="HAI Pump Calculator",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

render_sidebar_nav("hai")

if "hai_disclaimer_agreed" not in st.session_state:
    st.session_state.hai_disclaimer_agreed = None


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


if st.session_state.hai_disclaimer_agreed is None:
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
        if st.button("🤝 I Agree", use_container_width=True, type="primary", key="hai_agree"):
            st.session_state.hai_disclaimer_agreed = True
            st.rerun()

    with d_col2:
        if st.button("❌ Disagree / Exit", use_container_width=True, key="hai_disagree"):
            st.session_state.hai_disclaimer_agreed = False
            st.rerun()

elif st.session_state.hai_disclaimer_agreed is False:
    st.title("🩺 HAI Pump Calculator")
    st.error("🔒 Access Denied. You must agree to the medical disclaimer terms to utilize this calculator.")
    if st.button("Return to Disclaimer screen", key="hai_return"):
        st.session_state.hai_disclaimer_agreed = None
        st.rerun()

else:
    st.title("🩺 HAI Pump Calculator")
    st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
    st.write(
        "Calculate the required FUDR dose and compounding components for **Days 1–14** based on pump type."
    )

    st.divider()

    pump_type = st.selectbox(
        "Select Pump Type",
        options=["Intera (Codman)", "Medtronic"],
        index=0,
        key="hai_pump_type",
    )

    PUMP_SPECS = {
        "Intera (Codman)": {"volume": 30.0, "dex": "25 mg", "heparin": "30,000 units"},
        "Medtronic": {"volume": 20.0, "dex": "20 mg", "heparin": "25,000 units"},
    }

    specs = PUMP_SPECS[pump_type]
    pump_volume = specs["volume"]

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox(
            "Patient Gender",
            options=["Male", "Female"],
            index=None,
            placeholder="Select gender...",
            key="hai_gender",
        )

        dose_selection = st.selectbox(
            "Starting Dose (mg/kg)",
            options=[0.12, 0.08, 0.06, "Custom..."],
            index=0,
            format_func=lambda x: f"{x} mg/kg" if isinstance(x, (int, float)) else str(x),
            key="hai_dose_selection",
        )

        if dose_selection == "Custom...":
            dose_rate = st.number_input(
                "Enter Custom Dose (mg/kg)",
                min_value=0.00,
                max_value=2.00,
                value=None,
                format="%.2f",
                placeholder="Enter dose...",
                key="hai_custom_dose",
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
            key="hai_weight",
        )

        flow_rate = st.selectbox(
            "Pump Flow Rate (mL/day)",
            options=[1.4, 1.3, 1.2, 1.1],
            index=1,
            format_func=lambda x: f"{x} mL/day",
            key="hai_flow_rate",
        )

    with col3:
        height_cm = st.number_input(
            "Patient Height (cm)",
            min_value=0.0,
            max_value=250.0,
            value=None,
            format="%g",
            placeholder="Enter height...",
            key="hai_height",
        )

        st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

    st.divider()

    if real_weight is not None and height_cm is not None and gender and dose_rate is not None:
        ibw, dosing_weight, is_overweight, raw_fudr_dose, final_fudr_dose = calculate_fudr_dose(
            gender, height_cm, real_weight, dose_rate, pump_volume, flow_rate
        )

        if is_overweight:
            st.warning(
                f"⚠️ Patient is >35% over IBW. Using **Average Body Weight**: {dosing_weight:.1f} kg "
                f"(IBW: {ibw:.1f} kg)."
            )
        else:
            st.info(
                f"✅ Patient weight is within standard dosing limits. Using **Actual Body Weight**: "
                f"{real_weight} kg (IBW: {ibw:.1f} kg)."
            )

        st.subheader("📋 Order & Compounding Summary")

        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label=f"Calculated FUDR Dose (Raw - {pump_type})", value=f"{raw_fudr_dose:.2f} mg")
        m_col2.metric(label="Final FUDR Dose (Rounded to nearest 5 mg)", value=f"{final_fudr_dose} mg")

        st.markdown("#### Total Mixture Components")

        df_components = pd.DataFrame(
            {
                "Component": ["FUDR", "Dexamethasone", "Heparin", "Normal Saline (NS)"],
                "Target Protocol Dose / Volume": [
                    f"{final_fudr_dose} mg",
                    specs["dex"],
                    specs["heparin"],
                    f"Quantity sufficient (QS) to total {int(pump_volume)} mL",
                ],
            }
        )
        st.dataframe(df_components, hide_index=True, use_container_width=True)

        st.info(
            f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a "
            f"{pump_type} pump. Verify the pump's unique serial number, patient ID card, or sticker to confirm "
            "the accurate flow rate before preparation."
        )
    else:
        st.warning(
            "⚠️ Please enter patient weight, height, and select a gender to generate the dosage calculations "
            "and compounding summary."
        )
