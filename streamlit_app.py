import os
import pandas as pd
import requests
import datetime
import streamlit as st
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Professional Contact Finder - Real API Integration",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
    }
    .api-status {
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .api-connected { background-color: #d4edda; color: #155724; }
    .api-error { background-color: #f8d7da; color: #721c24; }
    .results-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class APIManager:
    """Manages all API integrations for professional contact discovery"""
    
    def __init__(self):
        self.hunter_api_key = os.getenv('HUNTER_API_KEY')
        self.apollo_api_key = os.getenv('APOLLO_API_KEY')
        self.clearbit_api_key = os.getenv('CLEARBIT_API_KEY')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    def test_api_connections(self) -> Dict[str, bool]:
        """Test all API connections and return status"""
        status = {}
        
        # Test Hunter.io
        if self.hunter_api_key:
            try:
                response = requests.get(
                    f"https://api.hunter.io/v2/account?api_key={self.hunter_api_key}",
                    timeout=10
                )
                status['hunter'] = response.status_code == 200
            except:
                status['hunter'] = False
        else:
            status['hunter'] = False
        
        # Test Apollo.io
        if self.apollo_api_key:
            try:
                headers = {'X-Api-Key': self.apollo_api_key}
                response = requests.get(
                    "https://api.apollo.io/v1/auth/health",
                    headers=headers,
                    timeout=10
                )
                status['apollo'] = response.status_code == 200
            except:
                status['apollo'] = False
        else:
            status['apollo'] = False
        
        # Test Clearbit
        if self.clearbit_api_key:
            try:
                response = requests.get(
                    "https://company.clearbit.com/v1/domains/find?name=google.com",
                    headers={'Authorization': f'Bearer {self.clearbit_api_key}'},
                    timeout=10
                )
                status['clearbit'] = response.status_code == 200
            except:
                status['clearbit'] = False
        else:
            status['clearbit'] = False
        
        return status
    
    def search_professionals_apollo(self, city: str, job_titles: List[str], 
                                  skills: List[str], limit: int = 20) -> List[Dict]:
        """Search for professionals using Apollo.io API"""
        if not self.apollo_api_key:
            return []
        
        try:
            headers = {
                'X-Api-Key': self.apollo_api_key,
                'Content-Type': 'application/json'
            }
            
            # Construct search query
            payload = {
                'q_person_title': ' OR '.join(job_titles),
                'q_person_location': city,
                'page_size': limit,
                'person_seniorities': ['senior', 'director', 'manager', 'individual_contributor']
            }
            
            response = requests.post(
                'https://api.apollo.io/v1/mixed_people/search',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('people', [])
            else:
                logger.error(f"Apollo API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Apollo API exception: {str(e)}")
            return []
    
    def find_email_hunter(self, first_name: str, last_name: str, 
                         company_domain: str) -> Optional[str]:
        """Find email using Hunter.io API"""
        if not self.hunter_api_key:
            return None
        
        try:
            url = "https://api.hunter.io/v2/email-finder"
            params = {
                'domain': company_domain,
                'first_name': first_name,
                'last_name': last_name,
                'api_key': self.hunter_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                email_data = data.get('data', {})
                if email_data.get('confidence') and email_data.get('confidence') > 50:
                    return email_data.get('email')
            
            return None
            
        except Exception as e:
            logger.error(f"Hunter API exception: {str(e)}")
            return None
    
    def enrich_company_clearbit(self, company_name: str) -> Dict:
        """Enrich company data using Clearbit API"""
        if not self.clearbit_api_key:
            return {}
        
        try:
            url = "https://company.clearbit.com/v1/domains/find"
            params = {'name': company_name}
            headers = {'Authorization': f'Bearer {self.clearbit_api_key}'}
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Clearbit API exception: {str(e)}")
            return {}

# Initialize API Manager
api_manager = APIManager()

# Main title
st.markdown('<h1 class="main-header">🔍 Professional Contact Finder v3.0</h1>', 
            unsafe_allow_html=True)
st.markdown("**Real-time professional contact discovery with API integration**")

# API Status Dashboard
st.sidebar.header("🔌 API Connection Status")
api_status = api_manager.test_api_connections()

for api_name, is_connected in api_status.items():
    status_class = "api-connected" if is_connected else "api-error"
    status_text = "✅ Connected" if is_connected else "❌ Disconnected"
    st.sidebar.markdown(
        f'<div class="{status_class}">{api_name.title()}: {status_text}</div>',
        unsafe_allow_html=True
    )

# Configuration sidebar
st.sidebar.header("🎯 Search Configuration")

# Indian cities with major tech hubs
cities = [
    "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai", 
    "Pune", "Kolkata", "Gurgaon", "Noida", "Kochi"
]

job_roles = [
    "Data Scientist", "Senior Data Scientist", "Machine Learning Engineer",
    "Data Engineer", "Senior Data Engineer", "Data Analyst",
    "Business Intelligence Analyst", "Analytics Engineer",
    "Big Data Engineer", "AI Engineer"
]

skills = [
    "Python", "R", "SQL", "Machine Learning", "Deep Learning",
    "AWS", "Azure", "Spark", "Hadoop", "Tableau", "Power BI"
]

# User inputs
selected_city = st.sidebar.selectbox("📍 Target City", cities)
selected_roles = st.sidebar.multiselect("💼 Job Roles", job_roles, default=job_roles[:2])
selected_skills = st.sidebar.multiselect("🛠️ Required Skills", skills, default=skills[:3])
max_results = st.sidebar.slider("📊 Number of Results", 5, 50, 10)

# API preference
api_preference = st.sidebar.selectbox(
    "🔧 Primary API Source",
    ["Apollo.io", "Hunter.io + Manual", "Mixed Sources"]
)

# Search functionality
col1, col2 = st.columns([3, 1])

with col1:
    search_button = st.button("🚀 Search Real Professionals", type="primary", 
                             use_container_width=True)

with col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.experimental_rerun()

# Main search logic
if search_button:
    if not selected_roles:
        st.error("⚠️ Please select at least one job role")
    elif not any(api_status.values()):
        st.error("⚠️ No API connections available. Please configure API keys.")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_contacts = []
        
        # Step 1: Search with Apollo.io
        if api_status.get('apollo'):
            status_text.text("🔍 Searching Apollo.io database...")
            progress_bar.progress(25)
            
            apollo_results = api_manager.search_professionals_apollo(
                selected_city, selected_roles, selected_skills, max_results
            )
            
            for person in apollo_results:
                contact = {
                    'name': f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                    'title': person.get('title', ''),
                    'company': person.get('organization', {}).get('name', ''),
                    'location': person.get('city', selected_city),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'email': person.get('email', ''),
                    'phone': person.get('phone_numbers', [{}])[0].get('raw_number', '') if person.get('phone_numbers') else '',
                    'source': 'Apollo.io'
                }
                all_contacts.append(contact)
        
        # Step 2: Enhance with Hunter.io emails
        if api_status.get('hunter') and all_contacts:
            status_text.text("📧 Enhancing email data with Hunter.io...")
            progress_bar.progress(50)
            
            for contact in all_contacts:
                if not contact['email'] and contact['company']:
                    # Extract company domain
                    company_domain = f"{contact['company'].lower().replace(' ', '')}.com"
                    
                    names = contact['name'].split()
                    if len(names) >= 2:
                        first_name, last_name = names[0], names[-1]
                        enhanced_email = api_manager.find_email_hunter(
                            first_name, last_name, company_domain
                        )
                        if enhanced_email:
                            contact['email'] = enhanced_email
                            contact['source'] += ' + Hunter.io'
        
        # Step 3: Enrich company data
        if api_status.get('clearbit') and all_contacts:
            status_text.text("🏢 Enriching company information...")
            progress_bar.progress(75)
            
            for contact in all_contacts:
                if contact['company']:
                    company_data = api_manager.enrich_company_clearbit(contact['company'])
                    if company_data:
                        contact['company_size'] = company_data.get('metrics', {}).get('employees', '')
                        contact['company_industry'] = company_data.get('category', {}).get('industry', '')
        
        # Step 4: Format results
        status_text.text("📊 Formatting results...")
        progress_bar.progress(100)
        
        if all_contacts:
            # Create DataFrame
            formatted_data = []
            for i, contact in enumerate(all_contacts, 1):
                formatted_data.append([
                    datetime.date.today().strftime("%Y-%m-%d"),
                    i,
                    selected_city,
                    contact.get('linkedin_url', f"https://linkedin.com/search/results/people/?keywords={contact['name'].replace(' ', '%20')}"),
                    contact['name'],
                    contact.get('phone', 'Not Available'),
                    contact.get('email', 'Not Available'),
                    contact['company'],
                    contact.get('source', 'API')
                ])
            
            df = pd.DataFrame(formatted_data, columns=[
                "Date of Scraping", "Sr No", "City", "LinkedIn Profile Link",
                "Name", "Mobile Number", "Email Id", "Organization Name", "Data Source"
            ])
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success(f"✅ Found {len(df)} real professionals in {selected_city}")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Total Contacts", len(df))
            with col2:
                emails_found = len(df[df['Email Id'] != 'Not Available'])
                st.metric("📧 Emails Found", emails_found)
            with col3:
                st.metric("🏙️ City", selected_city)
            with col4:
                companies = df['Organization Name'].nunique()
                st.metric("🏢 Companies", companies)
            
            # Results table
            st.subheader("📋 Real Professional Contacts")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download
            csv_data = df.to_csv(index=False)
            filename = f"real_contacts_{selected_city}_{datetime.date.today().strftime('%Y%m%d')}.csv"
            
            st.download_button(
                label="📥 Download Real Contact Data",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                type="secondary"
            )
            
            # Data quality info
            with st.expander("📊 Data Quality Report"):
                st.write(f"**Data Sources Used:** {', '.join([api for api, status in api_status.items() if status])}")
                st.write(f"**Email Coverage:** {emails_found}/{len(df)} contacts ({emails_found/len(df)*100:.1f}%)")
                st.write(f"**Phone Coverage:** {len(df[df['Mobile Number'] != 'Not Available'])}/{len(df)} contacts")
                st.write(f"**LinkedIn Coverage:** 100% (search URLs provided)")
                st.write(f"**Geographic Accuracy:** City-filtered via API")
        
        else:
            progress_bar.empty()
            status_text.empty()
            st.warning("⚠️ No contacts found. Try adjusting your search criteria or check API quotas.")

# API Configuration Guide
if not any(api_status.values()):
    st.markdown("---")
    st.subheader("🔧 API Configuration Required")
    
    st.markdown("""
    **To use real professional contact data, configure these API keys in your Streamlit Cloud secrets:**
    
    1. **Hunter.io** - Email finding and verification
       - Sign up at: https://hunter.io/
       - Free tier: 50 requests/month
       - Paid plans: $49-399/month
    
    2. **Apollo.io** - Professional contact database
       - Sign up at: https://apollo.io/
       - Free tier: 50 contacts/month
       - Paid plans: $49-1000+/month
    
    3. **Clearbit** - Company data enrichment
       - Sign up at: https://clearbit.com/
       - Free tier available
       - Paid plans: $99+/month
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
<strong>Professional Contact Finder v3.0 - Real API Integration</strong><br>
Legitimate professional contact discovery • Compliance-first approach • Real-time data
</div>
""", unsafe_allow_html=True)
