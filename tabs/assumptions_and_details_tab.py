import streamlit as st


def render(data):
    """Renders the Details tab contents."""

    # --- Table of contents with working anchor links ---
    st.markdown("""
    ## Contents

    - <a href="#methodology">1. Methodology</a>  
    - <a href="#hot-water-heaters">2. Hot water heaters</a>  
    - <a href="#billing-types">3. Billing types (tariffs)</a>  
    - <a href="#hot-water-control">4. Hot water control</a>  
    - <a href="#hot-water-usage-patterns">5. Hot water usage patterns</a>  
    - <a href="#options-explored">6. Options explored</a>
    """, unsafe_allow_html=True)
    

    st.markdown("""
    <a name="methodology"></a>
    ## 1. Methodology

    Hot water system operation was calculated using a two-stage methodology. In
    the first stage, a thermal simulation of the hot water system is performed, and
    in the second stage the cost of operating the system is determined. For these simulations, a standard 315L tank is used with standard insulation material as provided by manufacturer's data-sheets.

    ### 1.1 Thermal simulation

    The thermal simulation of the hot water systems dynamically simulates the
    temperature in the hot water storage tank and the system's use of
    electricity or gas to heat the water, taking into account:

    - Usage of hot water by the house, according to the selected hot water
        usage pattern
    - The thermal properties of the hot water tank (e.g., insulation)
    - Energy obtained from solar thermal water heating panels (solar
        thermal systems only)
    - The heating of the hot water when the temperature falls below the
        thermostat turn-on set point
    - The efficiency of the heater, which determines how much energy from electricity or gas
        it requires to heat water
    - Note: instantaneous gas systems do not have tanks, so only the energy
        required to directly heat the water as needed is considered

    The key output of these simulations is the time-varying energy (gas or
    electricity) usage across the year.

    ### 1.2 Financial cost

    Once a hot water heater's time-varying energy usage has been
    calculated, the cost of operating the heater is determined. For
    electric, heat pump, and solar thermal systems, the following method
    is used to calculate the operating cost. For each half-hourly period
    in the year:

    1. The cost of heating using electricity from the household's solar system
    is determined. If solar electricity is available, this is used preferentially
    with an assumed cost equal to the solar export payment rate (feed-in tariff).
    The solar export payment rate is applied as a cost because when solar
    electricity is used to heat hot water, the household loses the revenue that
    they would otherwise have obtained from exporting.
    
    2. The cost of heating using grid electricity is determined. Any energy
    required to heat the hot water that cannot be provided from solar
    electricity must be imported from the electricity grid. The cost of this
    electricity is determined by the billing type (tariff) selected. For time-
    varying billing types, this rate can change throughout the day and year. For
    flat rate and controlled load billing types, this rate is constant throughout the
    year.
    
    3. The cost of heating from solar and from the grid for the half-hourly period
    is added together to give the total cost for the period.

    Then the cost of heating for a year is determined by summing the costs
    for all periods in the year. Note: no fixed daily charges are considered
    for electricity as households must pay these regardless of their heater
    type or total usage.

    For gas hot water systems, the cost is simply calculated by multiplying the
    total gas usage by the fixed rate for gas.

    ### 1.3 Environmental cost

    For electric, heat pump, and solar hot water, the environmental cost in tons of
    CO2 per year is also calculated on a time-varying basis.
    For each half-hourly period in the year, the volume of electricity not met by the
    household's solar is multiplied by the carbon intensity of the grid at that time to give the
    CO2 emissions associated with using hot water at that time. Then the emissions for all
    half-hourly periods across the year are summed to give the total emissions per year.

    For gas hot water systems, the yearly emissions are simply calculated by multiplying the
    total gas usage by the emissions intensity of gas.
                
    Note: Emissions projections over a 10-year period are not currently supported, as dynamic grid decarbonisation and gas emissions trajectories are not incorporated into this version of the model.
    """, unsafe_allow_html=True)
    st.markdown("""
    <a name="billing-types"></a>
    ## 2. Billing types

    The billing type, or tariff, determines how the household is charged for electricity
    or gas use. There are three types of billing that are considered in the Solar Shift analysis:

    1. **Flat rate electricity/gas**: a fixed rate for electricity or gas is charged
    regardless of when it is used.
    
    2. **Controlled load discount electricity**: a fixed rate is also used for controlled
    load, but a lower rate is charged because the load is typically shifted to times when the cost
    is lower for the grid to supply energy to the household.
    
    3. **Time-varying rate electricity**: the rate charged for electricity depends on the
    time of use.
    """, unsafe_allow_html=True)
    st.markdown("""
    <a name="hot-water-heaters"></a>
    ## 3. Hot water heaters

    ### 3.1 Electric

    Electric hot water heaters refer to electric tank-based systems. Electric hot water
    systems use a resistive element similar to those found in an oven to heat a tank of
    hot water. The tank allows the hot water to be heated and then stored, which means
    these systems can be operated very flexibly, heating when electricity is cheaper, 
    such as overnight, or when solar electricity is available, with the hot water stored
    for use later. These systems are very simple and cheap to
    install. Electric hot water heaters can also be paired with a solar electricity
    diverter, which measures how much electricity is being exported to the grid and
    adjusts the heater power consumption to match the amount of spare solar electricity.
    Diverters add to the cost and complexity of the system but can lower electricity bills
    and carbon emissions.

    ### 3.2 Heat pump

    Heat pumps use the same technology found in fridges and air conditioners to suck heat
    out of the air and pump it into water. As the heat comes from the air rather than
    directly from electricity, they typically use much less energy than simple electric
    hot water heaters. However, similar to an electric hot water heater, they use a tank
    to store the hot water, so they can be run flexibly when electricity is
    cheaper, such as overnight or during the day when solar electricity is available.
    Heat pumps tend to be more expensive to buy but cheaper to run than simple electric
    hot water systems.

    ### 3.3 Gas instant

    Instantaneous gas hot water systems turn on only when you turn on your hot water tap,
    heating the water on demand as it is needed. They tend to be cheap to install and have a
    moderate running cost. However, there isn't any scope to reduce emissions or lower
    running costs by combining this type of hot water system with solar electricity.

    ### 3.4 Gas storage

    Gas storage systems use gas to heat the hot water, which is then stored in a tank.
    These systems tend to be a bit more expensive to install and run compared to
    instantaneous gas.

    ### 3.5 Solar thermal

    Solar thermal systems use the sun to heat the water directly, which is then stored in
    a tank for later use. In the Solar Shift project, we also assumed that the solar
    thermal systems had an electric booster that heated the hot water tank when its
    temperature dropped below a preset temperature. Solar thermal systems tend to be
    expensive to install and relatively cheap to run. Additionally, because the sun is
    being used to heat the water directly, they use less roof space than is required by solar
    electricity systems. However, the complexity of running water pipes on and off your
    roof, as well as the pumps needed for some systems, is an additional
    consideration.
    """, unsafe_allow_html=True)
    st.markdown("""
    <a name="hot-water-control"></a>
    ## 4. Hot water control

    Some hot water systems can be controlled so they use electricity when it is cheaper
    or when solar electricity is available. The various control strategies
    explored in the Solar Shift simulations are described below.

    ### 4.1 Run as needed (no control)

    Run as needed means the hot water system will just run as per its internal
    control system. For electric, heat pump, and gas storage, this means the heater will
    run when the water in the tank falls below a preset temperature. For gas instant,
    the heater will run when hot water is used. For solar thermal, the heater
    will run when the sun is shining or the temperature drops below a preset
    value.

    ### 4.2 Off during peak usage times

    This control option means the water heater is restricted from running during local
    peak electricity usage times. The control option is only available for electric and
    heat pump hot water heaters and with the 'Controlled load discount electricity' billing
    type.

    ### 4.3 On during off-peak billing times

    This control option means the water heater can only run during off-peak billing
    times (as defined in time-varying electricity billing). The control option is only
    available for electric and heat pump hot water heaters and with the
    'Time-varying rate electricity' billing type.

    ### 4.4 On overnight

    This control option means the water heater can only run overnight. The control
    option is only available for electric and heat pump hot water heaters and with the
    'Controlled load discount electricity' billing type.

    ### 4.5 On overnight and sunny hours

    This control option means the water heater can only run overnight and during periods
    of the day that are typically sunny. The control option is only available for
    electric and heat pump hot water heaters and with the 'Controlled load discount
    electricity' billing type.

    ### 4.6 On sunny hours

    This control option means the water heater can only run during periods
    of the day that are typically sunny. The control option is only available for
    electric and heat pump hot water heaters and with the 'Flat rate electricity' billing
    type.

    ### 4.7 Diverter

    This control option means the water heater runs when there is spare solar
    electricity being exported to the grid. The control option is only available for
    electric heaters with the 'Flat rate electricity' or 'Controlled load discount
    electricity' billing type.
    """, unsafe_allow_html=True)
    st.markdown("""
    <a name="hot-water-usage-patterns"></a>
    ## 5. Hot water usage patterns

    Hot water heating was simulated with a number of different hot water usage patterns.
    The user can choose the one that best matches their own usage pattern or consider
    how a hot water system might perform across several patterns if they are unsure
    which one best matches them. The chart below shows when water is used across the
    day for each of the six usage patterns.""", unsafe_allow_html=True)

    # Add hot water usage patterns graph image using columns for centering
    a, b, c = st.columns([1, 3, 1])
    with b:
        st.image("images/usage_patterns.png", use_container_width=True)


    st.markdown("""
    <a name="options-explored"></a>
    ## 6. Options explored

    Not all system configurations have been modelled. Typically, when system
    configurations have not been modelled, this is because the configuration does not
    make sense from a technical perspective, e.g., it does not make sense to model a gas
    storage heater with a flat rate electricity billing type. The complete set of
    configurations that have been modelled are shown in the table below.
    """, unsafe_allow_html=True)
    cols = ["Heater", "Heater control", "Hot water billing type", "Solar"]
    show_data = data.loc[:, cols]
    show_data = show_data.drop_duplicates(cols)
    show_data = show_data.sort_values(by=cols)
    st.dataframe(show_data, hide_index=True)
