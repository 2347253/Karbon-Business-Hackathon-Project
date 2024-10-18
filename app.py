import streamlit as st
import json
import plotly.express as px
from model import probe_model_5l_profit
from rules import get_flag_color  

def plot_financials(financials, company_name):
    years = [fin["year"] for fin in financials]
    net_revenues = [fin["pnl"]["lineItems"]["net_revenue"] for fin in financials]

    df = {
        'Year': years,
        'Net Revenue (₹)': net_revenues
    }

    fig = px.line(df, x='Year', y='Net Revenue (₹)', markers=True,
                  title= 'Company: '+ company_name,
                  labels={'Net Revenue (₹)': 'Net Revenue (₹)', 'Year': 'Year'})
    
    fig.update_layout(showlegend=True)
    
    return fig

def main():
    st.sidebar.title("Financial Analysis App")
    page = st.sidebar.selectbox("Select Page", ["Upload Data", "Results"])

    if page == "Upload Data":
        st.title("Upload Financial Data")
        uploaded_file = st.file_uploader("Choose a JSON file...", type="json")
        if uploaded_file is not None:
            data = json.load(uploaded_file)
            if st.button("Submit"):
                results = probe_model_5l_profit(data["data"])
                st.session_state.results = results
                st.session_state.financials = data["data"]["financials"]  # Store financials for later use
                st.session_state.company_name = data["data"]["company"]["legal_name"]  # Store company name
                st.success("Data processed successfully!")

    elif page == "Results":
        if 'results' in st.session_state:
            st.markdown("<h1 style='text-align: center;'>Analysis Results</h1>", unsafe_allow_html=True)
            flags = st.session_state.results["flags"]

            col1, col2, col3 = st.columns(3)
            with col1:
                color = get_flag_color(flags.get("TOTAL_REVENUE_5CR_FLAG", "N/A"))
                st.markdown(
                    f"""
                    <div style='border: 2px solid gray; padding: 10px; border-radius: 10px;'>
                        <h3 style='color: {color};'>Total Revenue Flag: {flags.get("TOTAL_REVENUE_5CR_FLAG", "N/A")}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                color = get_flag_color(flags.get("BORROWING_TO_REVENUE_FLAG", "N/A"))
                st.markdown(
                    f"""
                    <div style='border: 2px solid gray; padding: 10px; border-radius: 10px;'>
                        <h3 style='color:{color};'>Borrowing to Revenue Flag: {flags.get("BORROWING_TO_REVENUE_FLAG", "N/A")}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col3:
                color = get_flag_color(flags.get("ISCR_FLAG", "N/A"))
                st.markdown(
                    f"""
                    <div style='border: 2px solid gray; padding: 10px; border-radius: 10px;'>
                        <h3 style='color:{color};'>ISCR Flag for company: {flags.get("ISCR_FLAG", "N/A")}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.subheader("Detailed Insights")
            
            # Insights for TOTAL_REVENUE_5CR_FLAG
            if flags["TOTAL_REVENUE_5CR_FLAG"] == 1:
                st.write("•  Total revenue exceeds ₹5 crore, indicating strong sales performance.")
            else:
                st.write("•  Total revenue is below ₹5 crore, which may indicate growth opportunities.")
            
            # Insights for BORROWING_TO_REVENUE_FLAG
            if flags["BORROWING_TO_REVENUE_FLAG"] == 1:
                st.write("•  The company maintains a healthy borrowing to revenue ratio.")
            else:
                st.write("•  The borrowing to revenue ratio is high, indicating potential over-leverage.")
            
            # Insights for ISCR_FLAG
            if flags["ISCR_FLAG"] == 1:
                st.write("•  The Interest Service Coverage Ratio is robust, suggesting good ability to cover interest payments.")
            else:
                st.write("•  The Company has a low ISCR, therefore indicating potential difficulty in meeting interest obligations.")

            # Plotting Financial Data
            financials = st.session_state.financials  # Retrieve financials from session state
            company_name = st.session_state.company_name  # Retrieve company name from session state
            
            st.subheader("Financial Overview")

            fig = plot_financials(financials, company_name)
            
            with st.container():
                st.markdown(
                    """
                    <div style='border:2px solid gray; padding:10px; border-radius:10px;'>
                        <h3 style='text-align: center;'>Net Revenue Over Years</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                st.plotly_chart(fig)

        else:
            st.warning("Please upload data first.")

if __name__ == "__main__":
    main()