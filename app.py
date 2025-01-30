import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go  # Importing Plotly Graph Objects for more control

# User input for base monthly benefit
base_benefit = st.number_input("Enter your estimated monthly Social Security benefit:", min_value=500, max_value=5000, value=1000, step=100)

# User input for interest rate (default 6%)
interest_rate = st.slider("Enter expected annual interest rate (%):", min_value=0.0, max_value=10.0, value=6.0, step=0.1)

# Set the Full Retirement Age (FRA)
FRA = 67  

# Function to calculate monthly benefits considering FRA
def calculate_monthly_benefit(start_age, base_benefit):
    if start_age < FRA:
        reduction_per_year = 0.06  # Approximate reduction per year before FRA
        years_early = FRA - start_age
        return base_benefit * (1 - (reduction_per_year * years_early))
    elif start_age > FRA:
        increase_per_year = 0.08  # Delayed retirement credits per year after FRA
        years_delayed = start_age - FRA
        return base_benefit * (1 + (increase_per_year * years_delayed))
    else:
        return base_benefit  # Full benefit at FRA

# Generate cumulative benefits with compounding interest
def compute_cumulative_benefits(base_benefit, interest_rate, selected_ages):
    ages = list(range(62, 101))  # Age range from 62 to 100
    benefits = {}

    for start_age in selected_ages:  # Only selected ages (default [62, 67])
        if start_age < 62:
            st.error("Error: Claiming age cannot be less than 62.")
            return None, None  # Return None if invalid age is selected
        
        monthly_benefit = calculate_monthly_benefit(start_age, base_benefit)
        total_benefit = 0
        cumulative_benefits = []

        for age in ages:
            if age >= start_age:
                total_benefit += monthly_benefit * 12  # Add yearly benefits
                # Apply compounding interest yearly
                total_benefit *= (1 + interest_rate / 100)

            cumulative_benefits.append(total_benefit)

        benefits[f"Age {start_age}"] = cumulative_benefits  # Label with "Age"

    return ages, benefits

# Streamlit App
st.title("Social Security Benefits Calculator with Investment Growth")
st.write("This app visualizes the **total Social Security benefits collected**, factoring in investment growth, from selected claiming ages until age 100.")

# Select starting age 1 (Numeric Input with + and - buttons)
selected_age_1 = st.number_input(
    "Select First Claiming Age (Between 62 and 70):", 
    min_value=62, 
    max_value=70, 
    value=62, 
    step=1
)

# Select starting age 2 (Numeric Input with + and - buttons)
selected_age_2 = st.number_input(
    "Select Second Claiming Age (Between 62 and 70):", 
    min_value=62, 
    max_value=70, 
    value=67, 
    step=1
)

# Compute data based on user input
ages, benefits_data = compute_cumulative_benefits(base_benefit, interest_rate, [selected_age_1, selected_age_2])

if benefits_data:  # Only proceed if the data is valid
    # Convert to DataFrame for plotting and displaying raw data
    df = pd.DataFrame(benefits_data, index=ages)

    # Convert data to display with dollar signs for the table
    df_display = df.applymap(lambda x: f"${x:,.0f}")  # Format numbers as currency

    # Create the Plotly figure with traces for each claiming age
    fig = go.Figure()

    # Add traces for both starting ages (selected_age_1 and selected_age_2)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[f"Age {selected_age_1}"], 
        mode='lines', 
        name=f"Age {selected_age_1}",
        visible=True  # Set the lines to be visible by default
    ))

    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[f"Age {selected_age_2}"], 
        mode='lines', 
        name=f"Age {selected_age_2}",
        visible=True  # Set the lines to be visible by default
    ))

    # Update layout for better visualization and interaction
    fig.update_layout(
        title="Total Social Security Benefits Collected Over Time (With Compounding Interest)",
        xaxis_title="Age",
        yaxis_title="Total Benefits ($)",
        legend_title="Claiming Age",
        hovermode="x unified"
    )

    # Display interactive Plotly chart with lines visible by default
    st.plotly_chart(fig, use_container_width=True)

    # Display raw data as a table with formatted values
    st.write("### Raw Data Table (With Investment Growth)")
    st.dataframe(df_display)

    # Explanation
    st.write(f"""
    ### Key Insights:
    - **Claiming at age {selected_age_1}:** The monthly benefits and compounded growth over time.
    - **Claiming at age {selected_age_2}:** The same comparison for a different age.
    - **Compounding Effect:** The longer benefits stay invested, the more exponential the growth.
    - **Consideration:** The impact of the **{interest_rate:.1f}% interest rate** means later claiming may still outperform earlier claiming depending on lifespan.
    """)
