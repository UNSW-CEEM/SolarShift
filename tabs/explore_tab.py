import streamlit as st
import plotly.express as px
import pandas as pd

from graphics.charts import apply_chart_formatting
from data_processing.data_processing import metrics, groups, load_and_preprocess_data
from helpers.data_selectors import get_rep_postcode_from_postcode


def render(data):
    """Renders the Advanced explorer tab with flexible data filtering and visualization."""

    # Load data and postcode mapping
    data, postcode_df = load_and_preprocess_data()

    # Highlight this section is for advanced users
    st.markdown(
        """
        <div style='background-color:#FFF3CD; padding:15px; border-left:6px solid #FFA000;'>
            <strong>Note:</strong> This section is designed for advanced users, researchers, or energy analysts. 
            It allows you to explore various hot water technologies and scenarios in greater detail.
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = data.rename(columns={"Location": "Postcode"})
    
    # Remove rows with missing household occupants then cast to int
    data = data.dropna(subset=["Household occupants"])
    data["Household occupants"] = data["Household occupants"].astype(int)

    # Remove NaNs in other selection columns to avoid showing 'nan' in dropdowns
    data = data.dropna(subset=["Hot water usage pattern", "Hot water billing type", "Solar", "Heater", "Heater control", "Postcode"])

  
    f_data = data.copy()

    if "Entered Postcode" in data.columns:
        groups_fixed = [g if g != "Location" else "Entered Postcode" for g in groups]
    else:
        groups_fixed = [g if g != "Location" else "Postcode" for g in groups]

    # Write heading at the top of tab.
    with st.container():
        st.markdown(
            "<h3 style='text-align: center; color: #FFA000;'>Explore hot water system configurations</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='text-align: center;'>Each point in this scatter plot represents a single simulated scenario based on your selections – use the options on the left to explore the results.</div>",
            unsafe_allow_html=True,
        )

    # Create container which holds data selectors and plot.
    with st.container():
        left, gap, right = st.columns([1.75, 0.25, 5])

        with left:
            # Create some space to push the selectors down the page a litte.
            st.markdown("<br>", unsafe_allow_html=True)

            # Reset button to clear all selections
            if st.button("🔄 Reset all selections"):
                for key in list(st.session_state.keys()):
                    if key.startswith("multiselect") or key.startswith("selectbox") or key.startswith("radio") or key.startswith("textinput_postcode"):
                        del st.session_state[key]
                st.session_state["textinput_postcode"] = ""  # force clear
                st.rerun()

            # Create household characteristic filters
            with st.expander("Describe your house", expanded=False):
                st.markdown(
                    "",
                    help="The options below are sequential filtered. "
                         "The options in lower selected box are limited by "
                         "the choices made in select boxes above them.",
                )

                # Enter multiple postcodes manually, comma separated
                postcode_input = st.text_input(
                    "Enter one or more postcodes (comma-separated)",
                    key="textinput_postcode",
                    help="For example: 2000, 2010, 2200"
                )

                if postcode_input:
                    try:
                        # Split input on commas, strip spaces, convert to int
                        entered_postcodes = [int(pc.strip()) for pc in postcode_input.split(",")]

                        # Map each to representative postcode
                        rep_postcodes = []
                        for pc in entered_postcodes:
                            rep_pc = get_rep_postcode_from_postcode(pc, postcode_df)
                            if rep_pc:
                                rep_postcodes.append(rep_pc)
                            else:
                                st.warning(f"Postcode {pc} not found in climate zone database.")
                        # Filter data to include all representative postcodes found
                        if rep_postcodes:
                            data = data[data["Postcode"].isin(rep_postcodes)]

                            # Create rows for each entered postcode, duplicating where reps overlap
                            frames = []
                            for pc in entered_postcodes:
                                rep_pc = get_rep_postcode_from_postcode(pc, postcode_df)
                                if rep_pc:
                                    subset = data[data["Postcode"] == rep_pc].copy()
                                    subset["Entered Postcode"] = pc  # assign the entered value manually
                                    frames.append(subset)

                            # Combine all rows — now duplicates will appear if reps overlap
                            if frames:
                                data = pd.concat(frames, ignore_index=True)
                                f_data = data.copy()
                                groups_fixed = [g if g != "Location" else "Entered Postcode" for g in groups]
                            else:
                                st.warning("No valid postcodes entered.")

                    except ValueError:
                        st.warning("Please enter valid numeric postcodes separated by commas.")

                # Always make a copy of filtered data for further selections
                f_data = data.copy()

                hs = st.multiselect(
                    "Household size",
                    data["Household occupants"].unique(),
                    default=st.session_state.get("multiselect_household", []),
                    key="multiselect_household",
                    help="The number of people living in the house.",
                )
                if len(hs) > 0:
                    f_data = f_data[f_data["Household occupants"].isin(hs)]

                patterns = st.multiselect(
                    "Hot water usage pattern",
                    f_data["Hot water usage pattern"].unique(),
                    default=st.session_state.get("multiselect_pattern", []),
                    key="multiselect_pattern",
                    help="When hot water is typically used in the house.",
                )
                if len(patterns) > 0:
                    f_data = f_data[f_data["Hot water usage pattern"].isin(patterns)]

                tariffs = st.multiselect(
                    "Hot water billing type",
                    data["Hot water billing type"].unique(),
                    default=st.session_state.get("multiselect_tariff", []),
                    key="multiselect_tariff",
                    help="""
                    How energy used for heating hot water is paid for.

                    This needs to match with the Heater type options
                    selected and the Control type options. E.g. to view
                    gas heater options, gas also needs to be selected 
                    as the billing type. Similarly, to use Control type options that
                    restrict when the heater is run the
                    'Control load discount electricity' needs to be selected 
                    as the billing type.
                    """,
                )
                if len(tariffs) > 0:
                    f_data = f_data[f_data["Hot water billing type"].isin(tariffs)]

                solar = st.multiselect(
                    "Solar",
                    f_data["Solar"].unique(),
                    default=st.session_state.get("multiselect_solar", []),
                    key="multiselect_solar",
                    help="If the house has a solar electricity system.",
                )
                if len(solar) > 0:
                    f_data = f_data[f_data["Solar"].isin(solar)]

            # Create heater configuration filters
            with st.expander("Choose a heater"):
                st.markdown(
                    "",
                    help="The options below are sequential filtered. "
                         "The options in lower selected box are limited by "
                         "the choices made in select boxes above them,"
                         "including in the 'Describe your house' box.",
                )
                heater = st.multiselect(
                    "Heater type",
                    f_data["Heater"].unique(),
                    default=st.session_state.get("multiselect_heater", []),
                    key="multiselect_heater",
                )
                if len(heater) > 0:
                    f_data = f_data[f_data["Heater"].isin(heater)]
                control = st.multiselect(
                    "Control type",
                    f_data["Heater control"].unique(),
                    default=st.session_state.get("multiselect_control", []),
                    key="multiselect_control",
                )
                if len(control) > 0:
                    f_data = f_data[f_data["Heater control"].isin(control)]

            # Chart visualization options
            with st.expander("Chart options"):
                index = groups.index("Heater")
                x = st.selectbox(
                    "Side-by-side",
                    groups_fixed,
                    index=groups_fixed.index(st.session_state.get("selectbox_x", "Heater"))
                        if "selectbox_x" in st.session_state else index,
                    key="selectbox_x"
                )
                
                color = st.selectbox(
                    "Color",
                    groups_fixed,
                    index=groups_fixed.index(st.session_state.get("selectbox_color", "Heater"))
                        if "selectbox_color" in st.session_state else index,
                    key="selectbox_color"
                )
                
                index = metrics.index("Annual cost ($/yr)")
                metric = st.selectbox(
                    "Comparison metric",
                    metrics,
                    index=metrics.index(st.session_state.get("selectbox_metric", "Annual cost ($/yr)"))
                        if "selectbox_metric" in st.session_state else index,
                    key="selectbox_metric"
                )

            # Create copy of the data for displaying in a table
            show_data = f_data.loc[:, groups_fixed + metrics]

        # Create the data plot.
        with right:
            chart = px.strip(f_data, y=metric, x=x, color=color)
            chart.update_traces(width=2.0)
            apply_chart_formatting(chart)
            st.plotly_chart(chart, use_container_width=True)
   
    # Write Subheading for the bottom table.
    with st.container():
        st.markdown(
            "<h3 style='text-align: center; color: #FFA000;'>Tabular Summary</h3>",
            unsafe_allow_html=True,
        )
    # Create a container for displaying the chart data in a table.
    with st.container():
        summarise = st.radio(
            "Data display option", ["Average", "Show all"], label_visibility="collapsed"
        )
        table_groups = list(set((x, color)))
        if len(table_groups) > 0 and summarise == "Average":
            agg_dict = {col: "mean" for col in metrics}
            show_data = show_data.groupby(table_groups, as_index=False).agg(agg_dict)
        show_data = show_data.sort_values("Net present cost ($)")
        
         # Rename long columns to shorter versions
        show_data = show_data.rename(columns={
             "Net present cost ($)": "NPC ($)",
            "Annual cost ($/yr)": "Annual ($/yr)",
            "Up front cost ($)": "CapEx ($)",
              "Decrease in solar export revenue ($/yr)": "Δ FIT ($/yr)",
             "Rebates ($)": "Rebates",
             "CO2 emissions (tons/yr)": "CO₂ (t/yr)",
             "Annual energy consumption (kWh)" : "Annual (KWh)"
            # Add more as needed
         })

        st.dataframe(show_data.style.format(precision=2), hide_index=True)
