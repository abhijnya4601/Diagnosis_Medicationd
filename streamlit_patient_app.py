import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Patient Lookup System",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load patient data"""
    diagnoses_df = pd.read_csv('Sample_Output_encounters_aws/all_encounters_diagnoses.csv')
    medications_df = pd.read_csv('Sample_Output_aws/all_medications.csv')
    return diagnoses_df, medications_df

@st.cache_data
def get_unique_patients(diagnoses_df, medications_df):
    """Get unique patients list"""
    diag_patients = diagnoses_df[['Patient_MRN', 'Patient_Full_Name']].drop_duplicates()
    med_patients = medications_df[['Patient_MRN', 'Patient_Full_Name']].drop_duplicates()
    all_patients = pd.concat([diag_patients, med_patients]).drop_duplicates()
    return all_patients.sort_values('Patient_Full_Name').reset_index(drop=True)

def get_patient_diagnoses(mrn, diagnoses_df):
    """Get all diagnoses for a patient"""
    patient_diag = diagnoses_df[diagnoses_df['Patient_MRN'] == mrn].copy()
    
    if patient_diag.empty:
        return pd.DataFrame()
    
    # Sort by encounter date
    if 'Encounter_Date' in patient_diag.columns:
        patient_diag = patient_diag.sort_values('Encounter_Date', ascending=False)
    
    # Remove duplicates
    if 'Diagnosis_Name' in patient_diag.columns:
        patient_diag = patient_diag.drop_duplicates(subset=['Diagnosis_Name'], keep='first')
    
    # Select diagnosis columns
    diag_cols = ['Diagnosis_Name', 'ICD10_Code', 'ICD10_Description', 
                 'ICD9_Code', 'ICD9_Description', 'Diagnosis_Status',
                 'Diagnosis_Onset_Date', 'Diagnosis_Resolution_Date', 'Encounter_Date']
    
    available_cols = [col for col in diag_cols if col in patient_diag.columns]
    return patient_diag[available_cols].reset_index(drop=True)

def get_patient_medications(mrn, medications_df):
    """Get all medications for a patient"""
    patient_meds = medications_df[medications_df['Patient_MRN'] == mrn].copy()
    
    if patient_meds.empty:
        return pd.DataFrame()
    
    # Sort by start date if available
    if 'Entry_Start_Date' in patient_meds.columns:
        patient_meds['Start_Date_Sort'] = pd.to_datetime(patient_meds['Entry_Start_Date'], errors='coerce')
        patient_meds = patient_meds.sort_values('Start_Date_Sort', ascending=False, na_position='last')
    
    # Select medication columns
    med_cols = ['Med_Original_Text', 'Med_Display_Name', 'Med_Code', 
               'Med_Code_Type', 'Entry_Dose', 'Entry_Start_Date',
               'Entry_End_Date', 'Entry_Instruction_Text']
    
    available_cols = [col for col in med_cols if col in patient_meds.columns]
    return patient_meds[available_cols].reset_index(drop=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Patient Lookup System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        # Load data
        diagnoses_df, medications_df = load_data()
        patients_list = get_unique_patients(diagnoses_df, medications_df)
        
        # Show total patients
        st.info(f"📊 Total Patients in Database: **{len(patients_list)}**")
        
        # Patient selection
        st.markdown("### 🔍 Select a Patient")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            patient_options = [f"{row['Patient_Full_Name']} (MRN: {row['Patient_MRN']})" 
                             for _, row in patients_list.iterrows()]
            
            selected_patient = st.selectbox(
                "Search by name or select from dropdown:",
                options=["-- Select a Patient --"] + patient_options,
                index=0
            )
        
        with col2:
            mrn_search = st.text_input("Or enter MRN directly:", "")
        
        # Determine selected patient
        selected_mrn = None
        
        if mrn_search:
            try:
                selected_mrn = int(mrn_search)
            except:
                st.error("❌ Please enter a valid MRN number")
        elif selected_patient != "-- Select a Patient --":
            selected_mrn = int(selected_patient.split("MRN: ")[1].rstrip(")"))
        
        # Display patient information
        if selected_mrn:
            st.markdown("---")
            
            # Get patient basic info
            patient_info = diagnoses_df[diagnoses_df['Patient_MRN'] == selected_mrn]
            if patient_info.empty:
                patient_info = medications_df[medications_df['Patient_MRN'] == selected_mrn]
            
            if patient_info.empty:
                st.error(f"❌ No patient found with MRN: {selected_mrn}")
            else:
                patient = patient_info.iloc[0]
                
                # Patient basic info
                st.markdown("### 👤 Patient Information")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**Name:**  \n{patient['Patient_Full_Name']}")
                with col2:
                    st.markdown(f"**MRN:**  \n{patient['Patient_MRN']}")
                with col3:
                    st.markdown(f"**DOB:**  \n{patient.get('Patient_DOB', 'N/A')}")
                with col4:
                    st.markdown(f"**Age/Gender:**  \n{patient.get('Patient_Age', 'N/A')} / {patient.get('Patient_Gender', 'N/A')}")
                
                st.markdown("---")
                
                # Get diagnoses and medications
                diagnoses = get_patient_diagnoses(selected_mrn, diagnoses_df)
                medications = get_patient_medications(selected_mrn, medications_df)
                
                # Summary metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h2>{len(diagnoses)}</h2>
                            <p>Total Diagnoses</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h2>{len(medications)}</h2>
                            <p>Total Medications</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Tabs for diagnoses and medications
                tab1, tab2 = st.tabs(["📋 Diagnoses", "💊 Medications"])
                
                with tab1:
                    st.markdown("### Diagnoses")
                    if diagnoses.empty:
                        st.info("No diagnoses found for this patient.")
                    else:
                        st.dataframe(
                            diagnoses,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Download button
                        csv = diagnoses.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Diagnoses as CSV",
                            data=csv,
                            file_name=f"diagnoses_{patient['Patient_Full_Name'].replace(' ', '_')}_{selected_mrn}.csv",
                            mime="text/csv"
                        )
                
                with tab2:
                    st.markdown("### Medications")
                    if medications.empty:
                        st.info("No medications found for this patient.")
                    else:
                        st.dataframe(
                            medications,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Download button
                        csv = medications.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Medications as CSV",
                            data=csv,
                            file_name=f"medications_{patient['Patient_Full_Name'].replace(' ', '_')}_{selected_mrn}.csv",
                            mime="text/csv"
                        )
    
    except FileNotFoundError as e:
        st.error(f"❌ Data files not found: {str(e)}")
        st.info("Please ensure CSV files are in the correct folders")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
    This application allows you to:
    - Search for patients by name or MRN
    - View patient diagnoses with ICD codes
    - View patient medications with details
    - Download patient data as CSV
    """)
    
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Select a patient from dropdown or enter MRN
    2. View diagnoses and medications in tabs
    3. Download data if needed
    """)
    
    st.markdown("---")
    st.markdown("🏥 Patient Lookup System v1.0")

if __name__ == "__main__":
    main()
