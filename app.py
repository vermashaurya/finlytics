import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cohere
import datetime as dt
import random

# Initialize Cohere client
cohere_api_key = "piudmDnysbSTR1fzk7Nas0GCt5LSN8VTwTv1GRbL"
co = cohere.Client(cohere_api_key)

# Hardcoded credentials for login
VALID_CREDENTIALS = {
    "admin": "password123",
    "shaurya": "mysecurepassword"
}


# Utility Functions
def login(username, password):
    """Validates login credentials."""
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password


def load_data(file):
    """Loads a dataset and returns it as a DataFrame."""
    return pd.read_csv(file)


def detect_outliers(data, column):
    """Detects outliers using the IQR method."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return outliers


def generate_insights(data, column):
    """Generates AI-driven insights about the selected column."""
    description = data[column].describe().to_string()
    analysis_input = (
        f"The dataset has been analyzed for the column '{column}'. "
        f"The statistical summary is as follows:\n{description}\n"
        "Provide insights on the potential reasons for these outliers and how they may impact analysis."
    )
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=analysis_input,
        max_tokens=200
    )
    return response.generations[0].text.strip()


def calculate_simple_interest(principal, rate, time):
    return (principal * rate * time) / 100


def calculate_compound_interest(principal, rate, time):
    return principal * ((1 + (rate / 100)) ** time) - principal


def calculate_asset_value(initial_value, rate, time, is_appreciating):
    if is_appreciating:
        return initial_value * ((1 + rate / 100) ** time)
    else:
        return initial_value * ((1 - rate / 100) ** time)


def generate_trend_insights(simple_interest, compound_interest):
    difference = abs(simple_interest - compound_interest)
    analysis_input = (
        f"The simple interest amount is {simple_interest:.2f} and the compound interest amount is {compound_interest:.2f}. "
        f"The difference between them is {difference:.2f}. "
        "Please provide a short analysis of this difference, focusing only on how these two amounts compare, and avoid giving definitions."
    )
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=analysis_input,
        max_tokens=200
    )
    return response.generations[0].text.strip()


# Login Page
def login_page():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password):
            st.success("Login successful!")
            st.session_state.page = "homepage"
        else:
            st.error("Invalid username or password.")


# Homepage
def homepage():
    """Homepage with navigation buttons."""
    st.title("Financial Management System")
    st.write("Welcome to the FMS!")

    # Style for buttons
    st.markdown("""
        <style>
            .stButton button {
                width: 300px;
                height: 60px;
                margin: 10px;
                font-size: 20px;
                margin-top: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Centering buttons
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("Outlier Analysis"):
            st.session_state.page = "outlier_analysis"  # Set session state to navigate

    with col2:
        if st.button("Asset Valuation / Interest"):
            st.session_state.page = "interest_and_asset_valuation"  # Use the correct page value

    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.button("Capital Budgeting")  # Placeholder for Module 3
    with col4:
        st.button("Report Generation")  # Placeholder for Module 4


# Outlier Analysis
def outlier_analysis():
    st.title("Outlier Analysis")
    uploaded_file = st.file_uploader("Upload your dataset", type=["csv"])

    if uploaded_file:
        data = load_data(uploaded_file)
        st.write("Dataset Preview:", data.head())

        column = st.selectbox("Select a column for outlier analysis", data.columns)
        if column:
            outliers = detect_outliers(data, column)

            st.subheader("Outlier Analysis Results")
            st.write("Outliers Found:", outliers)

            fig, ax = plt.subplots()
            data[column].plot(kind="box", ax=ax)
            ax.set_title(f"Boxplot for {column}")
            st.pyplot(fig)

            insights = generate_insights(data, column)
            st.subheader("AI Insights")
            st.write(insights)

    if st.button("Back to Homepage"):
        st.session_state.page = "homepage"


# Interest & Asset Valuation
def interest_and_asset_valuation():
    st.title("Asset Valuation")

    # Asset Valuation
    st.subheader("Asset Valuation: Depreciation and Appreciation")

    asset_type = st.selectbox(
        "Select Asset Type",
        ["Land", "Real Estate", "Vehicle", "Jewellery", "Other"]
    )
    initial_price = st.number_input("Enter Initial Price of the Asset", min_value=0.0, value=100000.0)
    purchase_date = st.date_input("Date of Purchase", value=dt.date.today())

    if asset_type in ["Land", "Real Estate"]:
        location = st.text_input("Enter Location of the Asset")

    market_rate = round(random.uniform(2, 10), 2)
    st.write(f"Market Appreciation/Depreciation Rate: {market_rate}%")

    is_appreciating = st.radio(
        "Is this asset appreciating or depreciating?",
        ["Appreciating", "Depreciating"]
    ) == "Appreciating"

    future_date = st.date_input("Select Future Date for Valuation", value=dt.date.today())
    time_years = (future_date - purchase_date).days / 365

    final_value = calculate_asset_value(initial_price, market_rate, time_years, is_appreciating)

    time_values = np.linspace(0, time_years, 100)
    value_over_time = [
        calculate_asset_value(initial_price, market_rate, t, is_appreciating)
        for t in time_values
    ]

    fig, ax = plt.subplots()
    ax.plot(time_values, value_over_time, label='Asset Value Over Time', color='green')
    ax.set_title("Asset Valuation")
    ax.set_xlabel("Time (Years)")
    ax.set_ylabel("Asset Value")
    ax.legend()
    st.pyplot(fig)

    st.write(f"Estimated Value of the Asset on {future_date}: ₹{final_value:.2f}")

    # Interest Calculation
    st.markdown("---")
    st.subheader("Interest Calculator with AI Insights")

    principal = st.number_input("Enter the Principal Amount", min_value=0.0, value=1000.0)
    rate = st.number_input("Enter the Rate of Interest (in %)", min_value=0.0, value=5.0)
    time_period = st.selectbox(
        "Select Time Period",
        ["1 month", "1 quarter", "6 months", "1 year", "2 years", "5 years", "10 years", "20 years"]
    )

    time_mapping = {
        "1 month": 1 / 12,
        "1 quarter": 1 / 4,
        "6 months": 1 / 2,
        "1 year": 1,
        "2 years": 2,
        "5 years": 5,
        "10 years": 10,
        "20 years": 20
    }
    time = time_mapping[time_period]

    final_simple = calculate_simple_interest(principal, rate, time)
    final_compound = calculate_compound_interest(principal, rate, time)

    time_values = np.linspace(0, time, 100)
    simple_interest_values = calculate_simple_interest(principal, rate, time_values)
    compound_interest_values = calculate_compound_interest(principal, rate, time_values)

    fig, ax = plt.subplots()
    ax.plot(time_values, simple_interest_values, label="Simple Interest", color='blue')
    ax.plot(time_values, compound_interest_values, label="Compound Interest", color='orange')
    ax.set_title("Interest Over Time")
    ax.set_xlabel("Time (Years)")
    ax.set_ylabel("Interest Amount")
    ax.legend()
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Simple Interest Amount", value=f"{final_simple:.2f}", disabled=True)
    with col2:
        st.text_input("Compound Interest Amount", value=f"{final_compound:.2f}", disabled=True)

    insight_text = generate_trend_insights(final_simple, final_compound)
    st.write("### AI Analysis on Interest Comparison:")
    st.write(insight_text)

    if st.button("Back to Homepage"):
        st.session_state.page = "homepage"


# Main Function
def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "homepage":
        homepage()
    elif st.session_state.page == "outlier_analysis":
        outlier_analysis()
    elif st.session_state.page == "interest_and_asset_valuation":
        interest_and_asset_valuation()  # Ensure this matches the session state


if __name__ == "__main__":
    main()
