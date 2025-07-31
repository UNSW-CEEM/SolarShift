import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np


def filter_data(data: pd.DataFrame, group: str, value: str) -> pd.DataFrame:
    if value is not None:
        data = data[data[group] == value]
    return data


def build_interactive_data_filter(
    data: pd.DataFrame,
    key_version: str,
    big_labels: Optional[Dict[str, Union[str, List[str], Dict[str, Union[str, List[str]]]]]] = None,  prefill_values: Optional[Dict[str, Optional[str]]] = None,
) -> tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    """
    Build an interactive data selector interface with cascading filters.

    This function creates a series of dropdown selectors for filtering the dataset
    based on multiple criteria. The filters are applied sequentially, with each
    subsequent filter showing only options available based on previous selections.
    The function maintains state across Streamlit reruns using session state.

    Args:
        data: DataFrame containing the data to filter
        key_version: String identifier for the session state keys to differentiate
                     between multiple instances of this component
        big_labels: Optional dictionary of labels or instructions for each group.
                    If provided, standard labels are hidden and these are shown instead.
                    Values can be strings, lists (for title + description), or
                    dicts with {"label": ..., "help": ...} for tooltips.

    Returns:
        tuple containing:
            - pd.DataFrame: Filtered DataFrame based on all selections
            - Dict[str, Optional[str]]: Dictionary of selected values for each filter
    """
    # Keeping the slected values
    if prefill_values is None:
        prefill_values = {}
    # Determine label visibility based on big_labels presence
    if big_labels:
        label_visibility = "collapsed"
    else:
        label_visibility = "visible"

    def make_big_label(group: str) -> Optional[str]:
        """
        Create a larger, prominent label for a filter group.
        Returns any help tooltip string if available.
        """
        help_text = None
        if big_labels:
            label_config = big_labels[group]
            if isinstance(label_config, str):
                st.markdown("#### " + label_config)
            elif isinstance(label_config, list):
                st.markdown("#### " + label_config[0])
                st.markdown(label_config[1])
            elif isinstance(label_config, dict):
                label = label_config.get("label")
                help_text = label_config.get("help")
                if isinstance(label, list):
                    st.markdown("#### " + label[0])
                    st.markdown(label[1])
                elif isinstance(label, str):
                    st.markdown("#### " + label)
        return help_text
    
    def create_select(data: pd.DataFrame, group: str, help_text: Optional[str]=None) -> Optional[str]:
        
        """
        Create a select box with state persistence for a filter group.
        """

        # Get unique values for dropdown options
        options = list(data[group].unique())

        # Create consistent key for session state
        group_key = group.lower().replace(" ", "_")
        key = f"select_{group_key}_{key_version}"
        KEY = key.upper()

        # Preload from prefill_values
        default_value = prefill_values.get(group_key)
        if default_value and default_value in options:
            st.session_state[KEY] = default_value

        # Remove invalid value
        if KEY in st.session_state and st.session_state[KEY] not in options:
            st.session_state.pop(KEY)

        if KEY not in st.session_state:
            st.selectbox(group, options, key=key, label_visibility=label_visibility, help=help_text)
        else:
            selected_value = st.session_state[KEY]
            if selected_value in options:
                index = options.index(selected_value)
            else:
                index = 0
            st.selectbox(group, options, index=index, key=key, label_visibility=label_visibility, help=help_text)

        # Final value from session
        selected = st.session_state[key]
        if selected == "---":
            st.session_state[KEY] = None
        else:
            st.session_state[KEY] = selected

        if isinstance(selected, np.generic):
            selected = selected.item()

        return selected

    # Store selected values
    values = {}

    # Create cascading filters
    data = data.copy()
    
    # Drop rows with missing household occupants to avoid conversion errors
    data = data.dropna(subset=["Household occupants"])
    
    # Now safely convert to int
    data["Household occupants"] = data["Household occupants"].astype(int)
    # Household occupants filter
    help_text = make_big_label("Household occupants")
    values["household_occupants"] = create_select(data, "Household occupants", help_text)
    data = filter_data(data, "Household occupants", values["household_occupants"])
    
    # Hot water usage pattern filter
    help_text = make_big_label("Hot water usage pattern")
    values["hot_water_usage_pattern"] = create_select(data, "Hot water usage pattern", help_text)
    data = filter_data(
        data, "Hot water usage pattern", values["hot_water_usage_pattern"]
    )
    
    # Solar PV presence filter
    help_text = make_big_label("Solar")
    values["solar"] = create_select(data, "Solar", help_text)
    data = filter_data(data, "Solar", values["solar"])
    
    # 6 type filter
    help_text = make_big_label("Heater")
    values["heater"] = create_select(data, "Heater", help_text)
    data = filter_data(data, "Heater", values["heater"])
    
    # Hot water billing type filter
    help_text = make_big_label("Hot water billing type")
    values["hot_water_billing_type"] = create_select(data, "Hot water billing type", help_text)
    data = filter_data(data, "Hot water billing type", values["hot_water_billing_type"])
    
    # Heater control filter
    help_text = make_big_label("Heater control")
    values["heater_control"] = create_select(data, "Heater control", help_text)
    data = filter_data(data, "Heater control", values["heater_control"])

    # Return empty dataset if any filter is unset
    if None in values.values():
        data = filter_data(data, "Location", "-")

    # Force-insert location so it is passed to compare
    if "Location" in data.columns and len(data["Location"].unique()) == 1:
        values["location"] = data["Location"].unique()[0]
    else:
        values["location"] = None

    return data, values


def export_settings_to_compare_tab(
    values_to_export: Dict[str, Optional[str]], version: str
) -> None:
    """
    Export filter settings to the comparison tab.

    This function copies the selected filter values from one tab to the
    comparison tab by setting the appropriate session state variables.
    This allows users to compare different configurations side by side.

    Args:
        values_to_export: Dictionary of filter values to export
        version: Identifier string for the target comparison tab (e.g., "two" or "three")
    """
    if "location" in values_to_export:
        st.session_state[f"select_location_{version}"] = values_to_export["location"] 
    st.session_state[f"select_household_occupants_{version}"] = values_to_export["household_occupants"]
    st.session_state[f"select_hot_water_usage_pattern_{version}"] = values_to_export["hot_water_usage_pattern"]
    st.session_state[f"select_solar_{version}"] = values_to_export["solar"]
    st.session_state[f"select_hot_water_billing_type_{version}"] = values_to_export["hot_water_billing_type"]
    st.session_state[f"select_heater_{version}"] = values_to_export["heater"]
    st.session_state[f"select_heater_control_{version}"] = values_to_export["heater_control"]


def get_rep_postcode_from_postcode(user_postcode: int, postcode_df: pd.DataFrame) -> Optional[int]:
    row = postcode_df[postcode_df["postcode"] == user_postcode]
    if not row.empty:
        return row.iloc[0]["rep_postcode"]
    else:
        return None
