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
# 🧮 CLINICAL HELPER FUNCTIONS
# ==============================================================================
def calculate_bmi(weight_kg, height_cm):
    """Calculates Body Mass Index (BMI)."""
    if height_cm and height_cm > 0:
        return weight_kg / ((height_cm / 100) ** 2)
    return 0.0


def calculate_ibw(gender, height_cm):
    """Calculates Ideal Body Weight (IBW) using Devine Formula."""
    if not height_cm:
        return 0.0
    height_in_inches = height_cm / 2.54
    if height_in_inches < 60:
        height_in_inches = 60.0

    base_weight = 50.0 if gender == "Male" else 45.5
    return base_weight + 2.3 * (height_in_inches - 60.0)


def calculate_adjusted_weight(actual_weight, ibw):
    """Calculates Adjusted Body Weight (AjBW) using a 40% correction factor."""
    return ibw + 0.4 * (actual_weight - ibw)


def calculate_crcl(gender, age, dosing_weight, scr):
    """Calculates Creatinine Clearance (CrCl) using Cockcroft-Gault."""
    if not scr or scr <= 0 or not age or age <= 0:
        return 0.0

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


# ==============================================================================
# 🔀 NAVIGATION SETUP
# ==============================================================================
# Setup clean options map for readability
CALC_OPTIONS = {
    "5-FU": "🧪 SMARTeZ Pump Calculator",
    "FUDR": "💉 HAI Pump Calculator",
    "Carboplatin": "💊 Carboplatin AUC Calculator",
    "BSA": "📏 Weight & BSA Matrix"
}

st.sidebar.markdown("## 🧮 Oncology Clinical Suite")
st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 500; margin-bottom: 0px;">Select a calculator:</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Use a native radio input component for automated callback rerun routing
selected_label = st.sidebar.radio(
    label="Navigation Menu",
    options=list(CALC_OPTIONS.values()),
    label_visibility="collapsed"
)
active_calc = [k for k, v in CALC_OPTIONS.items() if v == selected_label][0]

st.sidebar.markdown("---")
st.sidebar.caption("v2.3.0 | Clinical Decision Support Tool")


# ==============================================================================
# 🧬 CALCULATOR 1: SYSTEMIC INFUSION (5-FU)
# ==============================================================================
@st.fragment
def render_5fu_calculator():
    st.title("🧪 SMARTeZ Pump Calculator")
    st.markdown("### 5-FU Dose Calculation")
    st.write("Calculate 5-FU dose with overfill based on pump type.")
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

    if not dose or not duration:
        st.warning("⚠️ Please enter dose and select a duration to generate the dosage calculations.")
        st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")
        return

    pump_vol = None
    if override_pump:
        if duration == 46: pump_vol = 230
        elif duration == 48: pump_vol = 240
        else:
            st.warning("⚠️ Override is only applicable for 46 hr or 48 hr durations.")
            override_pump = False

    if not override_pump:
        if duration == 24: pump_vol = 240
        elif duration == 96: pump_vol = 192
        elif duration == 120: pump_vol = 240
        elif duration == 48: pump_vol = 240 if dose > 4600 else 96
        elif duration == 46: pump_vol = 230 if dose > 4400 else 92

    vol_overfill = OVERFILL_MAP.get(pump_vol)
    pump_type = PUMP_TYPE_MAP.get((duration, None)) or PUMP_TYPE_MAP.get((None, pump_vol), "")

    if pump_vol and vol_overfill:
        dose_overfill = dose * (vol_overfill / pump_vol)
        dose_overfill_rounded = int(50 * round(dose_overfill / 50))
        concentration = dose_overfill_rounded / vol_overfill
        drug_vol = dose_overfill_rounded / 50
        ns_vol = vol_overfill - drug_vol
    else:
        dose_overfill, dose_overfill_rounded, concentration, drug_vol, ns_vol = 0.0, 0, 0.0, 0.0, 0.0

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
    label_style = "font-size: 0.9rem; opacity: 0.8;"
    value_style = "font-size: 2rem; font-weight: 600; line-height: 1.4;"
    col_c1.markdown(f'<div style="{label_style}">Pump Volume with Overfill</div><div style="{value_style}">{vol_overfill} mL</div>', unsafe_allow_html=True)
    col_c2.markdown(f'<div style="{label_style}">Pump Type</div><div style="{value_style}">{pump_type if pump_type else "-"}</div>', unsafe_allow_html=True)
    
    st.html("<br>")
    h_col3, h_col4 = st.columns(2)
    h_col3.info(f"**Volume of 5-FU:**\n\n ## `{f'{drug_vol:g}' if drug_vol else '0'} mL`")
    h_col4.success(f"**Volume of NS:**\n\n ## `{f'{ns_vol:g}' if ns_vol else '0'} mL`")
    st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")


# ==============================================================================
# 🫁 CALCULATOR 2: HEPATIC ARTERIAL INFUSION (FUDR)
# ==============================================================================
@st.fragment
def render_fudr_calculator():
    st.title("💉 HAI Pump Calculator")
    st.markdown("### FUDR Dose Calculation (1 Cycle = 28 Days)")
    st.write("Calculate FUDR dose based on initial starting dose and flow rate.")
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
        dose_selection = st.selectbox("Starting Dose (mg/kg)", options=[0.12, 0.08, 0.06, "Custom..."], index=0, format_func=lambda x: f"{x} mg/kg" if isinstance(x, (int, float)) else x)
        dose_rate = st.number_input("Enter Custom Dose (mg/kg)", min_value=0.00, max_value=2.00, value=None) if dose_selection == "Custom..." else dose_selection
    with col2:
        real_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter weight...")
        flow_rate = st.selectbox("Pump Flow Rate (mL/day)", options=[1.4, 1.3, 1.2, 1.1], index=1, format_func=lambda x: f"{x} mL/day")
    with col3:
        height_cm = st.number_input("Patient Height (cm)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter height...")
        st.metric(label="Pump Volume (Fixed)", value=f"{int(pump_volume)} mL")

    st.divider()

    if not (real_weight and height_cm and gender and dose_rate is not None):
        st.warning("⚠️ Please enter patient weight, height, and select a gender to generate calculations.")
        st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")
        return

    ibw = calculate_ibw(gender, height_cm)
    is_overweight = real_weight > (1.35 * ibw)
    dosing_weight = (ibw + real_weight) / 2.0 if is_overweight else real_weight
    
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

    clean_admin_text = (
        f"1. Floxuridine dose: {dose_rate:g} mg/kg/day × {dosing_weight:g} kg = Daily dose of Floxuridine: {daily_dose:.2f} mg/day\\n"
        f"2. Daily dose of Floxuridine: {daily_dose:.2f} mg/day / flow rate: {flow_rate} mL/day = pump concentration: {pump_concentration:.2f} mg/mL\\n"
        f"3. Pump concentration: {pump_concentration:.2f} mg/mL × pump volume: {int(pump_volume)} mL = total dose of FLOXURIDINE: {final_fudr_dose} mg (rounded to closest 5 mg)\\n"
        f"4. Please insert total dose into Floxuridine dosing field above"
    )

    title_col, btn_col = st.columns([0.75, 0.25], vertical_alignment="bottom")
    with title_col:
        st.subheader("✏️ To Fill Out Admin Instructions")
    with btn_col:
        escaped_text = clean_admin_text.replace("'", "\\'").replace("\n", "\\n")
        html_button = f"""
        <button onclick="navigator.clipboard.writeText('{escaped_text}'); this.innerText='Copied!';" 
                style="
                    width: 100%; background-color: #262730; color: #ffffff;
                    border: 1px solid rgba(250, 250, 250, 0.2); padding: 6px 12px;
                    border-radius: 8px; cursor: pointer; font-size: 14px;
                    font-weight: 500; display: flex; align-items: center;
                    justify-content: center; gap: 8px; height: 38px;
                ">
            📋 Copy Text
        </button>
        """
        st.components.v1.html(html_button, height=45)

    admin_text = (
        f"1. **Floxuridine dose:** {dose_rate:g} mg/kg/day × {dosing_weight:g} kg = **Daily dose of Floxuridine:** {daily_dose:.2f} mg/day  \n"
        f"2. **Daily dose of Floxuridine:** {daily_dose:.2f} mg/day / **flow rate:** {flow_rate} mL/day = **pump concentration:** {pump_concentration:.2f} mg/mL  \n"
        f"3. **Pump concentration:** {pump_concentration:.2f} mg/mL × **pump volume:** {int(pump_volume)} mL = **total dose of FLOXURIDINE:** {final_fudr_dose} mg (rounded to closest 5 mg)  \n"
        f"4. Please insert total dose into Floxuridine dosing field above"
    )
    st.success(admin_text)

    st.info(
        f"💡 **Note:** This calculation is specifically for **Day 1-14** of the 28-day cycle using a {pump_type} pump. "
        "Verify the pump's unique serial number, patient ID card, or sticker to confirm the accurate flow rate before preparation."
    )
    st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")


# ==============================================================================
# 💊 CALCULATOR 3: CARBOPLATIN AUC CALCULATOR (CALVERT FORMULA)
# ==============================================================================
@st.fragment
def render_carboplatin_calculator():
    st.title("💊 Carboplatin AUC Calculator")
    st.write("Calculate Carboplatin dosing based on target AUC and estimated Creatinine Clearance.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Patient Demographics")
        gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=None, step=1, format="%g")
        weight = st.number_input("Actual Weight (kg)", min_value=1.0, max_value=300.0, value=None, step=1.0, format="%g")
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=None, step=1.0, format="%g")

    with col2:
        st.subheader("Clinical Parameters")
        scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, max_value=10.0, value=None, step=0.01, format="%g")
        target_auc = st.number_input("Target AUC", min_value=1.0, max_value=10.0, value=None, step=0.5, format="%g")

        st.markdown("##### Dosing Adjustments")
        use_gog_floor = st.checkbox(
            "Apply GOG Recommendation (SCr floor of 0.7 mg/dL)",
            value=False,
            help="If Serum Creatinine is less than 0.7, rounds up to 0.7 to avoid overestimating CrCl."
        )
        cap_crcl = st.checkbox("Cap GFR/CrCl at 125 mL/min (FDA Recommendation)", value=True)

    st.markdown("---")

    if not (age and weight and height and scr and target_auc):
        st.warning("⚠️ Please complete all patient information and clinical parameter fields above to view dosing outputs.")
        st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")
        return

    bmi = calculate_bmi(weight, height)
    ibw = calculate_ibw(gender, height)
    ajbw = calculate_adjusted_weight(weight, ibw)

    dosing_weight = weight
    weight_strategy_used = "Actual Body Weight"

    if bmi >= 25.0:
        with col2:
            use_adjusted = st.checkbox(
                f"Use Adjusted Body Weight ({format_trailing(ajbw)} kg) instead of Actual Weight",
                value=False,
                help="Often considered for overweight/obese patients to prevent CrCl overestimation."
            )
            if use_adjusted:
                dosing_weight = ajbw
                weight_strategy_used = "Adjusted Body Weight"
    else:
        with col2:
            st.info("Patient BMI is normal (< 25). Actual Body Weight used.")

    final_scr = scr
    scr_adjusted_msg = ""
    if use_gog_floor and scr < 0.7:
        final_scr = 0.7
        scr_adjusted_msg = "*(Rounded up to 0.7 mg/dL per GOG)*"

    raw_crcl = calculate_crcl(gender, age, dosing_weight, final_scr)
    final_crcl = min(raw_crcl, 125.0) if cap_crcl else raw_crcl
    carboplatin_dose = target_auc * (final_crcl + 25)

    st.subheader("Calculation Results")
    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        st.metric(
            label="Estimated CrCl",
            value=f"{format_trailing(final_crcl)} mL/min",
            delta=f"Capped (Raw: {format_trailing(raw_crcl)})" if cap_crcl and raw_crcl > 125 else None,
            delta_color="inverse"
        )
        st.caption(f"Calculated via **{weight_strategy_used}**")
        if scr_adjusted_msg:
            st.caption(scr_adjusted_msg)

    with res_col2:
        st.metric(label="Recommended Carboplatin Dose", value=f"{carboplatin_dose:.0f} mg")

    with res_col3:
        st.metric(label="Patient BMI", value=f"{format_trailing(bmi)} kg/m²")
        st.caption(f"IBW: {format_trailing(ibw)} kg | AjBW: {format_trailing(ajbw)} kg")

    with st.expander("Clinical Notes & Formulas Used"):
        st.markdown(
            """
        * **Calvert Formula:** $\\text{Dose (mg)} = \\text{Target AUC} \\times (\\text{CrCl} + 25)$
        * **Cockcroft-Gault Equation:** $$\\text{CrCl} = \\frac{(140 - \\text{Age}) \\times \\text{Dosing Weight (kg)}}{72 \\times \\text{Serum Creatinine (mg/dL)}}$$
          *(Multiplied by 0.85 for female patients)*
        * **GOG Serum Creatinine Recommendation:** Low serum creatinine artificially drives up calculated CrCl. The Gynecologic Oncology Group (GOG) guidelines suggest rounding up a low baseline creatinine value to a minimum of **0.7 mg/dL** to provide a safety buffer against over-dosing.
        * **Weight Dosing Strategy:** * **Ideal Body Weight (IBW):** Calculated using the Devine formula.
            * **Adjusted Body Weight (AjBW):** Calculated as $\\text{IBW} + 0.4 \\times (\\text{Actual Weight} - \\text{IBW})$.
        * **FDA Warning:** The FDA recommends capping the maximum GFR/CrCl at **125 mL/min** to prevent unintended toxicity.
        """
        )
    st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")


# ==============================================================================
# 🩻 CALCULATOR 4: WEIGHT & BSA SUITE
# ==============================================================================
@st.fragment
def render_bsa_calculator():
    st.title("📏 Weight & BSA Calculator")
    st.markdown("### Patient Weight & BSA Indexing")
    st.write("Simultaneously evaluate Body Surface Area (BSA) across multiple foundational oncological equations.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        bsa_gender = st.selectbox("Patient Gender", options=["Male", "Female"], index=None, placeholder="Select gender...")
    with col2:
        bsa_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, value=None, format="%g", placeholder="Enter weight...")
    with col3:
        bsa_height = st.number_input("Patient Height (cm)", min_value=0.0, max_value=250.0, value=None, format="%g", placeholder="Enter height...")

    st.divider()

    if not (bsa_gender and bsa_weight and bsa_height):
        st.warning("⚠️ Please provide Patient Gender, Weight, and Height inputs to verify biometric index values.")
        st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")
        return

    bsa_mosteller = math.sqrt((bsa_height * bsa_weight) / 3600)
    bsa_dubois = 0.007184 * (bsa_height ** 0.725) * (bsa_weight ** 0.425)
    bsa_haycock = 0.024265 * (bsa_height ** 0.3964) * (bsa_weight ** 0.5378)
    bsa_gehan = 0.0235 * (bsa_height ** 0.42246) * (bsa_weight ** 0.51456)
    
    ibw_val = calculate_ibw(bsa_gender, bsa_height)
    adj_weight_val = calculate_adjusted_weight(bsa_weight, ibw_val)
    percent_ibw = (bsa_weight / ibw_val) * 100

    formatted_ibw = f"{round(ibw_val, 1):g}"
    formatted_adjbw = f"{round(adj_weight_val, 1):g}"
    formatted_pct = f"{round(percent_ibw, 1):g}"

    if bsa_weight > (1.2 * ibw_val):
        st.warning(f"⚠️ Patient is obese or overweight (>120% of IBW at **{formatted_pct}%**). Consider utilizing **Adjusted Body Weight** for chemotherapy regimens requiring weight-based adjustments.")
    else:
        st.info(f"✅ Patient weight profile is within standard limits (**{formatted_pct}%** of Ideal Body Weight).")

    st.subheader("📋 Clinician Weight Workspace")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric(label="Ideal Body Weight (IBW)", value=f"{formatted_ibw} kg")
    m_col2.metric(label="Adjusted Body Weight (AdjBW)", value=f"{formatted_adjbw} kg")
    m_col3.metric(label="Percent of IBW", value=f"{formatted_pct} %")

    st.markdown("#### BSA Multi-Equation Matrix")
    df_bsa = pd.DataFrame({
        "BSA Mathematical Formula": [
            "Mosteller (Oncology Standard)", 
            "DuBois & DuBois", 
            "Haycock (Validated for Pediatrics/Extreme Heights)", 
            "Gehan & George"
        ],
        "Calculated Index Value": [
            "%.3f m²" % bsa_mosteller,
            "%.3f m²" % bsa_dubois,
            "%.3f m²" % bsa_haycock,
            "%.3f m²" % bsa_gehan
        ]
    })
    st.dataframe(df_bsa, hide_index=True, use_container_width=True)
    st.info("💡 **Clinical Note:** Mosteller remains the default calculation model used across modern Electronic Health Records (EHR) networks for standard surface-area-based chemotherapeutic indexing.")
    st.caption("Disclaimer: This tool is for educational purposes only and should not replace professional clinical judgment.")


# --- Dynamic View Routing Engine ---
if active_calc == "5-FU":
    render_5fu_calculator()
elif active_calc == "FUDR":
    render_fudr_calculator()
elif active_calc == "Carboplatin":
    render_carboplatin_calculator()
elif active_calc == "BSA":
    render_bsa_calculator()
