import pandas as pd
import streamlit as st

group_columns = {
    "location": "Location",
    "household_size": "Household occupants",
    "tariff_type": "Hot water billing type",
    "heater_type": "Heater",
    "control_type": "Heater control",
    "has_solar": "Solar",
    "profile_HWD": "Hot water usage pattern",
}

metric_columns = {
    "net_present_cost": "Net present cost ($)",
    "capital_cost": "Up front cost ($)",
    "rebates": "Rebates ($)",
    "annual_energy_cost": "Annual cost ($/yr)",
    "daily_supply_cost" : "Annual supply cost ($/yr)",
    "annual_fit_opp_cost": "Decrease in solar export revenue ($/yr)",
    "emissions_total": "CO2 emissions (tons/yr)",
    "annual_energy_consumption": "Annual energy consumption (kWh)",
}

groups = list(group_columns.values())
metrics = list(metric_columns.values())

@st.cache_data
def load_and_preprocess_data():
    postcode_df = pd.read_csv("data/postcode_to_climatezone.csv")
    data = pd.read_csv("data/all_climatezones_scenario.csv")
    data = data.rename(columns=group_columns)
    data = data.rename(columns=metric_columns)

    data["Heater"] = data["Heater"].map({
        "resistive": "Electric",
        "premium_heat_pump": "Premium Heat Pump",
        "standard_heat_pump": "Standard Heat Pump",
        "heat_pump": "Heat Pump",
        "solar_thermal": "Solar Thermal",
        "gas_instant": "Gas Instant",
        "gas_storage": "Gas Storage",
    })

    data["Heater control"] = data["Heater control"].map({
        "GS": "Run as needed (no control)",
        "CL1": "On overnight",
        "CL2": "Off during peak billing times",
        "CL3": "On overnight and sunny hours",
        "timer_SS": "On sunny hours",
        "diverter": "Diverter",
        "timer_OP": "On during off-peak billing times",
    })

    data["Hot water usage pattern"] = data["Hot water usage pattern"].map({
        1: "Morning and evening only",
        2: "Morning and evening with day time",
        3: "Evenly distributed",
        4: "Morning dominant",
        5: "Evening dominant",
        6: "Late night",
    })

    data["Hot water billing type"] = data["Hot water billing type"].map({
        "flat": "Flat rate electricity",
        "tou": "Time varying rate electricity",
        "CL": "Controlled load discount electricity",
        "gas": "Flat rate gas",
    })

    data["Solar"] = data["Solar"].map({True: "Yes", False: "No"})

    # Add gas heaters with Solar PV
    gas_data = data[data["Heater"].isin(["Gas Storage", "Gas Instant"])].copy()
    gas_data["Solar"] = "Yes"
    data = pd.concat([data, gas_data])

    # Just strip spaces 
    for col in ["Hot water usage pattern", "Heater control", "Heater", "Hot water billing type", "Solar"]:
        data[col] = data[col].astype(str).str.strip()

    data["Household occupants"] = data["Household occupants"].astype(int)

    return data, postcode_df
