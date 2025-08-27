import streamlit as st
import plotly.express as px
import pandas as pd

from graphics.charts import apply_chart_formatting
from data_processing.data_processing import metrics, groups, load_and_preprocess_data
from helpers.data_selectors import (
    export_settings_to_compare_tab,
    build_interactive_data_filter,
    get_rep_postcode_from_postcode
)
from data.system_configs import (
    create_basic_heat_pump_config,
    create_solar_electric,
    create_electric,
    create_solar_thermal,
    create_gas_instant,
)

def render(data, postcode_df):
    data, postcode_df = load_and_preprocess_data()

    contents_column, right_gap = st.columns([4, 2])
    with contents_column:

        st.markdown("""
            <style>
            div[data-testid="column"] label, 
            div[data-testid="column"] p, 
            div[data-testid="column"] input {
                font-size: 18px !important;
                font-family: "Source Sans Pro", sans-serif !important;
            }
            div[data-testid="stTextInput"] label p {
                font-size: 24px !important;
                font-weight: 600 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: #FFA000;'>Tell us about your house:</h3>", unsafe_allow_html=True)
        st.markdown("Complete the questions below and we will estimate your new hot water heating costs.")
        st.markdown("Privacy", help="Your data is not stored by SolarShift Customer Hot Water Road Map tool. The tool may use data only for research purposes without any personal or confidential information.")

        # Remember postcode using session state
        if "postcode" not in st.session_state:
            st.session_state["postcode"] = ""

        postcode = st.text_input("Enter your postcode", value=st.session_state["postcode"], max_chars=4)

        # Update session state only when input changes
        if postcode != st.session_state["postcode"]:
            st.session_state["postcode"] = postcode

        rep_postcode = None
        if postcode and postcode.isdigit():
            rep_postcode = get_rep_postcode_from_postcode(int(postcode), postcode_df)
        if not rep_postcode and postcode and postcode.isdigit():
            rep_postcode = int(postcode)
        if rep_postcode:
            data = data[data["Location"] == rep_postcode]
        else:
            return
        
        all_systems_data = data.copy()
        if data.empty:
            st.warning("No data found for this postcode, please check your entry.")
            return

        big_labels = {
            "Location": "What is your postcode?",
            "Household occupants": "How many people live there?",
            "Hot water usage pattern": {"label": ["When do you typically use most of your hot water?", "(see **Assumptions & details** tab: 5. Hot water usage patterns)"]},
            "Solar": "Do you have a solar electricity system (PV)?",
            "Hot water billing type": ["Choose the type of tariff/energy bill you receive for water heating?", "(If unsure, choose flat rate)"],
            "Heater": "What type of hot water heater do you have?",
            "Heater control": "Is your hot water heater being controlled?",
        }
        
        if "begin_tab_values" not in st.session_state:
            st.session_state["begin_tab_values"] = {}

        data, values = build_interactive_data_filter(
            all_systems_data, key_version="one", big_labels=big_labels, prefill_values=st.session_state["begin_tab_values"]
        )

        #  Save current values for persistence
        st.session_state["begin_tab_values"] = values.copy()

        for k in values:
            if isinstance(values[k], str):
                values[k] = values[k].strip()

        values["location"] = rep_postcode

        if data.empty:
            return

        data.insert(0, "System", "Your current hot water system")

        st.markdown("<h3 style='color: #FFA000;'>Your estimated hot water costs:</h3>", unsafe_allow_html=True)

        with st.expander("Spending summary", expanded=True):
            cols = ["Up front cost ($)", "Rebates ($)", "Annual cost ($/yr)", "Decrease in solar export revenue ($/yr)"]
            chart = px.bar(data, x="System", y=cols, text_auto=True, barmode="group", height=200)
            apply_chart_formatting(chart, yaxes_title="Costs")
            st.plotly_chart(chart, use_container_width=True)

        with st.expander("Simple financial summary: Net present cost over 10yrs", expanded=True):
            # Step 1: Create two new metrics
            data["Net present cost (excl. Up front)"] = (
                data["Net present cost ($)"] - data["Up front cost ($)"]
            )
            data["Net present cost (incl. Up front)"] = data["Net present cost ($)"]

            # Step 2: Reshape data for grouped bar chart
            bar_data = data[[
                "System", 
                "Net present cost (excl. Up front)", 
                "Net present cost (incl. Up front)"
            ]]
            bar_data = bar_data.melt(
                id_vars="System", 
                var_name="Metric", 
                value_name="Cost ($)"
            )

            # Step 3: Create grouped bar chart
            bar_chart = px.bar(
                bar_data,
                x="System",
                y="Cost ($)",
                color="Metric",
                barmode="group",
                text_auto=True,
            )

            # Step 4: Apply formatting
            bar_chart.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                bargap=0.3
            )

            apply_chart_formatting(
                bar_chart,
                yaxes_title="Net present cost ($)",
                show_legend=True,
                height=300,
            )

            # Step 5: Display chart
            st.plotly_chart(
                bar_chart, 
                use_container_width=True, 
                key="Net present cost ($) simple"
            )


        
        # Payback period calculation and logic from Gas and Electric to HPs Systems

        """If user select "Electric", "Gas Instant", "Gas Storage" as current system, Payback period question comes up and then there are options to select for End-of-life or standard payback period or not looking for changing system"""

        # Define rep_postcode to state mapping (based on postcode_to_climatezone.csv)
        rep_postcode_to_state = {
            2600: "ACT", 2010: "NSW", 2400: "NSW", 2647: "NSW", 2880: "NSW",
            800: "NT", 860: "NT", 870: "NT",
            4000: "QLD", 4220: "QLD", 4720: "QLD", 4480: "QLD", 4822: "QLD",
            5000: "SA", 5330: "SA", 5270: "SA",
            7000: "TAS", 7330: "TAS",
            3000: "VIC", 3570: "VIC", 3500: "VIC",
            6000: "WA", 6430: "WA", 6640: "WA", 6720: "WA"
        }

        if values["heater"] in ["Electric", "Gas Instant", "Gas Storage"]:
            if values["heater"] == "Electric" and values.get("heater_control") == "Diverter":
                st.info("Payback period calculation is not available for Electric systems with 'Diverter' control.")
            else:
                st.markdown("<h3 style='color: #FFA000;'>Would you like to find out the finances and emissions after switching to a heat-pump?</h3>", unsafe_allow_html=True)
                option = st.radio("Do you want to change to a heat pump?", ["Yes, my current system comes to the end of life and needs a replacement", "Yes, I just want a more efficient system", "No"], index=2)
                if option != "No":
                    st.markdown("**Select discount rate:**")
                    discount_rate = st.selectbox("", [0.02, 0.04, 0.06], index=0)
                    payback_data = []
                    for hp_type in ["Premium Heat Pump", "Standard Heat Pump"]:
                        if values["heater"] in ["Gas Instant", "Gas Storage"]:
                            hp_row = all_systems_data.loc[
                                (all_systems_data["Location"] == rep_postcode) &
                                (all_systems_data["Household occupants"] == values["household_occupants"]) &
                                (all_systems_data["Hot water usage pattern"] == values["hot_water_usage_pattern"]) &
                                (all_systems_data["Heater control"] == values["heater_control"]) &
                                (all_systems_data["Heater"] == hp_type) &
                                (all_systems_data["Solar"] == "No") &
                                (all_systems_data["Hot water billing type"] == "Flat rate electricity")
                            ]
                        elif values["heater"] == "Electric":
                            hp_row = all_systems_data.loc[
                                (all_systems_data["Location"] == rep_postcode) &
                                (all_systems_data["Household occupants"] == values["household_occupants"]) &
                                (all_systems_data["Hot water usage pattern"] == values["hot_water_usage_pattern"]) &
                                (all_systems_data["Heater control"] == values["heater_control"]) &
                                (all_systems_data["Hot water billing type"] == values["hot_water_billing_type"]) &
                                (all_systems_data["Solar"] == values["solar"]) &
                                (all_systems_data["Heater"] == hp_type)
                            ]
                        if hp_row.empty:
                            print(f"No hp_row match for {hp_type} with filters.")
                            continue
                        hp_row = hp_row.iloc[0]

                        try:
                            old_row = all_systems_data.loc[
                                (all_systems_data["Location"] == rep_postcode) &
                                (all_systems_data["Household occupants"] == values["household_occupants"]) &
                                (all_systems_data["Hot water usage pattern"] == values["hot_water_usage_pattern"]) &
                                (all_systems_data["Heater control"] == values["heater_control"]) &
                                (all_systems_data["Hot water billing type"] == values["hot_water_billing_type"]) &
                                (all_systems_data["Solar"] == values["solar"]) &
                                (all_systems_data["Heater"] == values["heater"])
                            ]
                        except Exception as e:
                            print(f"Old row fallback triggered: {e}")
                            old_row = all_systems_data.loc[
                                (all_systems_data["Location"] == rep_postcode) &
                                (all_systems_data["Household occupants"] == values["household_occupants"]) &
                                (all_systems_data["Heater"] == values["heater"])
                            ]
                        if old_row.empty:
                            print(f"No old_row match for heater: {values['heater']}")
                            continue
                        old_row = old_row.iloc[0]

                        print(f"old row: {old_row}")
                        print(f"hp row: {hp_row}")

                        annual_savings = old_row["Annual cost ($/yr)"] + old_row["Annual supply cost ($/yr)"] - hp_row["Annual cost ($/yr)"]
                        if annual_savings <= 0:
                            continue

                        upfront_cost = hp_row["Up front cost ($)"]

                        # Rebate Logic ↓↓↓↓↓↓
                        rebate_value = 0
                        try:
                            state = rep_postcode_to_state.get(rep_postcode)
                            old_heater = values["heater"]
                            is_heat_pump = hp_type.endswith("Heat Pump")
                            if is_heat_pump:
                                if state == "NSW":
                                    rebate_value = 800 if old_heater == "Electric" else 0
                                elif state == "VIC":
                                    rebate_value = 840 if old_heater == "Electric" else 490
                                elif state == "ACT":
                                    if (upfront_cost / 2) < 500:
                                        rebate_value = 500
                                    elif (upfront_cost / 2) <= 2500:
                                        rebate_value = upfront_cost / 2
                                    else:
                                        rebate_value = 2500
                        except Exception as e:
                            print(f"Rebate error for {state}: {e}")
                        # Rebate Logic ↑↑↑↑↑↑

                        upfront_cost -= rebate_value

                        simple_payback = (upfront_cost - old_row["Up front cost ($)"]) / annual_savings if option.startswith("Yes, my current") else upfront_cost / annual_savings

                        cumulative, year = 0, 0
                        while cumulative < upfront_cost and year < 50:
                            year += 1
                            cumulative += annual_savings / (1 + discount_rate) ** year

                        print(f"--- Payback Debug ---")
                        print(f"Heat Pump Type: {hp_type}")
                        print(f"Old Heater: {old_heater}")
                        print(f"State: {state}")
                        print(f"Upfront Cost (before rebate): {hp_row['Up front cost ($)']}")
                        print(f"Rebate Applied: {rebate_value}")
                        print(f"Upfront Cost (after rebate): {upfront_cost}")
                        print(f"Annual Savings: {annual_savings}")
                        print(f"Simple Payback: {simple_payback}")
                        print(f"Discounted Payback (yrs): {year}")
                        print("---------------------")

                        payback_data.append({
                            "Heat Pump Type": hp_type,
                            "Simple Payback (yrs)": round(simple_payback, 1),
                            "Discounted Payback (yrs)": year
                        })

                    with st.expander("Estimated Payback Period", expanded=True):
                        if payback_data:
                            df = pd.DataFrame(payback_data)
                            chart = px.bar(df, x="Heat Pump Type", y=["Simple Payback (yrs)", "Discounted Payback (yrs)"],
                                           barmode="group", text_auto=True, height=200,
                                           color_discrete_sequence=["#1AFF00", "#0FB7E6"])
                            apply_chart_formatting(chart, yaxes_title="Years")
                            st.plotly_chart(chart, use_container_width=True)
                        else:
                            st.info("Could not find matching heat pump scenarios for payback calculation.")

        #  Environmental summary 
        """It slways comes up for current system, howver, ifPayback period question triggered it shows the emission comparison between current and HPs systems """

        with st.expander("Environmental summary: Annual CO2 emissions (tons/year)", expanded=True):
            env_rows = data[["System", "CO2 emissions (tons/yr)"]].copy()

            if 'payback_data' in locals() and payback_data:
                for hp in ["Premium Heat Pump", "Standard Heat Pump"]:
                    hp_match = all_systems_data.loc[
                        (all_systems_data["Location"] == rep_postcode) &
                        (all_systems_data["Household occupants"] == values["household_occupants"]) &
                        (all_systems_data["Heater"] == hp)
                    ]
                    if not hp_match.empty:
                        hp_row = hp_match.iloc[0]
                        env_rows = pd.concat([
                            env_rows,
                            pd.DataFrame({
                                "System": [hp.replace(" Heat Pump", "").title() + " Heat Pump"],
                                "CO2 emissions (tons/yr)": [hp_row["CO2 emissions (tons/yr)"]]
                            })
                        ], ignore_index=True)
            chart = px.bar(env_rows, x="System", y="CO2 emissions (tons/yr)", color ="System",
                           text_auto=True, barmode="group", height=220, color_discrete_sequence=["#EA0C0C", "#1AFF00", "#0FB7E6"])
            apply_chart_formatting(chart, yaxes_title="CO2 emissions (tons/yr)", show_legend=False)
            chart.update_traces(texttemplate="%{y:.2f}")  # force two decimals on top
            st.plotly_chart(chart, use_container_width=True)

        # Compare buttons
        st.markdown("<h3 style='color: #FFA000;'>Compare your hot water system with other options:</h3>", unsafe_allow_html=True)
        st.markdown("Please go to **Compare** tab if you would like to further explore saving opportunities with heat-pumps (i.e. solar-soak control).</h3>", unsafe_allow_html=True)
        compare_options = [
            ("Compare to a Heat Pump", "If using 'Diverter' switches to 'On sunny hours'.", create_basic_heat_pump_config),
            ("Compare with adding solar electric system (PV)", "Converts to electric if starting with gas.", create_solar_electric),
            ("Compare with Electric", None, create_electric),
            ("Compare with Solar Thermal", None, create_solar_thermal),
            ("Compare with Gas Instant", None, create_gas_instant)
        ]

        for text, help, func in compare_options:
            def compare_callback(config=func(values.copy())):
                # Adding postcode for filtering
                config["location"] = rep_postcode
                values["location"] = rep_postcode

                export_settings_to_compare_tab(values.copy(), "two")
                export_settings_to_compare_tab(config, "three")
                st.session_state['tab'] = "Compare"
                st.session_state['scroll_to_top'] = True
            st.button(text, key=text.lower().replace(" ", "_"), help=help, on_click=compare_callback, use_container_width=True)
