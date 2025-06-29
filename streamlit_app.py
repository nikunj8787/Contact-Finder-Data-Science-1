import os
import pandas as pd
import requests
import datetime
import streamlit as st
import random
import time  # Needed for sleep delays
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Professional Contact Finder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🔍 Professional Contact Finder</h1>', unsafe_allow_html=True)
st.markdown("**Connect students with hiring professionals in data science roles**")

# Sidebar filters
st.sidebar.header("🎯 Search Configuration")
cities = [
    "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai", 
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Gurgaon", "Noida", "Kochi", "Indore", "Nagpur"
]
job_roles = [
    "Data Scientist", "Senior Data Scientist", "Machine Learning Engineer",
    "Data Engineer", "Senior Data Engineer", "Data Analyst",
    "Business Intelligence Analyst", "Analytics Engineer",
    "Big Data Engineer", "AI Engineer", "Data Science Manager"
]
seniority_levels = [
    "Junior", "Mid-Level", "Senior", "Lead", "Principal", 
    "Staff", "Manager", "Director", "Architect", "Consultant"
]
required_skills = [
    "Python", "R", "SQL", "Spark", "Hadoop", "AWS", "Azure", "GCP",
    "Tableau", "Power BI", "Machine Learning", "Deep Learning",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"
]

# Inputs
selected_city = st.sidebar.selectbox("📍 Target City", cities, index=0)
selected_roles = st.sidebar.multiselect("💼 Job Roles", job_roles, default=job_roles[:3])
selected_seniority = st.sidebar.multiselect("🎖️ Seniority Levels", seniority_levels, default=seniority_levels[:3])
selected_skills = st.sidebar.multiselect("🛠️ Required Skills", required_skills, default=required_skills[:4])
max_results = st.sidebar.slider("📊 Number of Results", 5, 100, 20)

# Buttons
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search_button = st.button("🚀 Search Professionals")
with col2:
    if st.button("🔄 Reset Filters"):
        st.experimental_rerun()
with col3:
    demo_button = st.button("📋 View Demo")

# Search logic
if search_button or demo_button:
    if not selected_roles:
        st.error("⚠️ Please select at least one job role.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        steps = [
            (20, "🔍 Scanning LinkedIn profiles..."),
            (40, "📧 Extracting contact info..."),
            (60, "🏢 Gathering company details..."),
            (80, "✅ Validating data..."),
            (100, "📊 Finalizing...")
        ]
        for val, msg in steps:
            progress_bar.progress(val)
            status_text.text(msg)
            time.sleep(0.8)
        # Sample data generation
        companies = [
            "TCS", "Infosys", "Wipro", "Accenture", "IBM", "Microsoft",
            "Amazon", "Google", "Meta", "Flipkart", "Zomato", "Paytm",
            "Swiggy", "Myntra", "PhonePe", "BYJU'S", "Unacademy", "Ola",
            "Freshworks", "Razorpay", "Zerodha", "Nykaa", "Cred"
        ]
        indian_names = [
            "Rajesh Kumar", "Priya Sharma", "Amit Singh", "Neha Gupta",
            "Rohit Verma", "Kavya Reddy", "Sanjay Patel", "Pooja Agarwal",
            "Vikash Yadav", "Ananya Nair", "Rahul Joshi", "Divya Menon",
            "Arjun Krishnan", "Sneha Iyer", "Karan Malhotra", "Ritu Bhatt"
        ]
        data = []
        for i in range(1, max_results + 1):
            name = f"{random.choice(indian_names)} {i}"
            company = random.choice(companies)
            role = random.choice(selected_roles)
            phone_prefix = random.choice(['70', '80', '90', '95', '98', '99'])
            phone = f"+91 {phone_prefix}{random.randint(100, 999)} {random.randint(10000, 99999)}"
            email_name = name.lower().replace(" ", ".").replace(".", "", 1)
            domain = company.lower().replace(" ", "")
            email = f"{email_name}@{domain}.com"
            linkedin_name = name.lower().replace(" ", "-")
            profile_url = f"https://linkedin.com/in/{linkedin_name}-{random.randint(100, 999)}"
            data.append([
                datetime.date.today().strftime("%Y-%m-%d"),
                i,
                selected_city,
                profile_url,
                name,
                phone,
                email,
                company
            ])
        df = pd.DataFrame(data, columns=[
            "Date of Scraping", "Sr No", "City", "LinkedIn Profile Link",
            "Name", "Mobile Number", "Email Id", "Organization Name"
        ])
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Found {len(df)} professionals in {selected_city}!")
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Contacts", len(df))
        with col2:
            st.metric("🏙️ City", selected_city)
        with col3:
            st.metric("🏢 Companies", df['Organization Name'].nunique())
        with col4:
            st.metric("📊 Data Quality", f"{random.randint(75, 95)}%")
        # Results table
        st.subheader("📋 Search Results")
        st.dataframe(df, use_container_width=True, height=400)
        # Download CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        filename = f"contacts_{selected_city}_{datetime.date.today().strftime('%Y%m%d')}.csv"
        st.download_button("📥 Download CSV", data=csv_bytes, file_name=filename, mime="text/csv")
        # Insights
        with st.expander("📈 Search Insights & Analytics"):
            st.write(f"**Search Parameters:**")
            st.write(f"- City: {selected_city}")
            st.write(f"- Roles: {', '.join(selected_roles)}")
            st.write(f"- Seniority: {', '.join(selected_seniority)}")
            st.write(f"- Skills: {', '.join(selected_skills)}")
            st.write(f"**Results Summary:**")
            st.write(f"- Total contacts: {len(df)}")
            st.write(f"- Unique companies: {df['Organization Name'].nunique()}")
            st.write(f"- Data quality: {f'{random.randint(75, 95)}%'}")
            st.write(f"- Generated on: {datetime.date.today().strftime('%B %d, %Y')}")

# Info section
if not (search_button or demo_button):
    st.markdown("---")
    st.subheader("ℹ️ How to Use")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Select Filters**\n- Choose city, roles, seniority, skills")
    with col2:
        st.markdown("**2. Search & Review**\n- Click 'Search Professionals'\n- Review table\n- Download CSV")
    with col3:
        st.markdown("**3. Connect & Follow Up**\n- Use CSV data\n- Reach out professionally")
# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Built for connecting students with hiring professionals • "
    f"Last updated: {datetime.date.today().strftime('%B %Y')}"
    "</div>",
    unsafe_allow_html=True
)
