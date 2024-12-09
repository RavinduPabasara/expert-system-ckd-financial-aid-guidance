import streamlit as st
from formtter import CKDFinancialAidKnowledgeManager
from pl_intergration_2 import ApplicationDenialExplainer, ApplicationGenerator

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Create a custom.css file with your styling
local_css("custom.css")

class CKDFinancialAidExpertSystem:
    def __init__(self):
        """
        Initialize the Expert System with key components
        """
        self.knowledge_manager = CKDFinancialAidKnowledgeManager()
        self.denial_explainer = ApplicationDenialExplainer()
        self.application_generator = ApplicationGenerator()

        # Initialize session state for tracking patient workflow
        if 'patient_name' not in st.session_state:
            st.session_state.patient_name = None
        if 'patient_facts' not in st.session_state:
            st.session_state.patient_facts = None
        if 'application_status' not in st.session_state:
            st.session_state.application_status = None
        if 'eligibility_result' not in st.session_state:
            st.session_state.eligibility_result = None

    def run_expert_system(self):
        """
        Main expert system workflow
        """
        st.title("🌟 දිරි - Expert System to Suggest Financial Aid Programs for Chronic Kidney Disease (CKD) Patients")

        # Step 1: Patient Information Input
        st.header("Step 1: Patient Information")
        patient_description = st.text_area(
            "Enter comprehensive patient description:",
            placeholder="Example: 'Nimal Perera is a 45-year-old rural resident with CKD stage 3, working as a farmer with limited monthly income...'"
        )

        if st.button("Process Patient Information"):
            if patient_description.strip():
                try:
                    # Add patient information with interactive mode
                    patient_facts = self.knowledge_manager.add_patient_information(
                        patient_description,
                        interactive=True
                    )

                    # Extract patient name from facts
                    patient_name = next(
                        (fact.split('(')[1].split(')')[0] for fact in patient_facts if fact.startswith('person(')),
                        None
                    )

                    if patient_name:
                        st.session_state.patient_name = patient_name
                        st.session_state.patient_facts = patient_facts
                        st.success(f"Patient {patient_name} information processed successfully!")
                    else:
                        st.error("Could not extract patient name from description.")

                except Exception as e:
                    st.error(f"Error processing patient information: {e}")
            else:
                st.warning("Please enter a patient description.")

        # Step 2: Eligibility Analysis
        if st.session_state.patient_name:
            st.header("Step 2: Eligibility Analysis")
            st.write(f"Patient: {st.session_state.patient_name}")

            if st.button("Check Eligibility"):
                try:
                    # Check patient eligibility
                    eligibility_result = self.denial_explainer.analyze_eligibility(
                        st.session_state.patient_name
                    )

                    # Store eligibility result in session state
                    st.session_state.eligibility_result = eligibility_result
                    st.session_state.application_status = eligibility_result['is_eligible']

                    # Display overall eligibility status
                    if eligibility_result['is_eligible']:
                        st.success("Patient is ELIGIBLE for financial aid.")
                        st.balloons()  # Add a celebratory animation
                    else:
                        st.error("Patient is NOT fully eligible for financial aid.")

                    # Eligible Programs Section
                    st.subheader("Eligible Programs")
                    if eligibility_result['eligible_programs']:
                        for program in eligibility_result['eligible_programs']:
                            st.markdown(f"✅ {program.replace('_', ' ').title()}")
                    else:
                        st.markdown("*No programs currently eligible*")

                    # Non-Eligible Programs Section
                    st.subheader("Non-Eligible Programs")
                    if eligibility_result['non_eligible_programs']:
                        for program in eligibility_result['non_eligible_programs']:
                            st.markdown(f"❌ {program.replace('_', ' ').title()}")
                    else:
                        st.markdown("*All programs are eligible*")

                    # Detailed Explanation Section
                    st.subheader("Detailed Eligibility Explanation")
                    st.info(eligibility_result['explanation'])

                    # Optional: Denial Reasons
                    if eligibility_result['denial_reasons']:
                        st.subheader("Specific Denial Reasons")
                        for reason in eligibility_result['denial_reasons']:
                            st.markdown(f"🚫 {reason}")

                except Exception as e:
                    st.error(f"Error checking eligibility: {e}")

        # Step 3: Application Generation
        if st.session_state.application_status:
            st.header("Step 3: Application Generation")

            if st.button("Generate Financial Aid Application"):
                try:
                    # Generate application
                    result = self.application_generator.generate_application(
                        st.session_state.patient_name
                    )

                    st.success("Application Generated Successfully!")
                    st.subheader("Application Details:")
                    st.text_area(
                        "Application Content:",
                        value=result['application'],
                        height=300,
                        disabled=True
                    )

                except Exception as e:
                    st.error(f"Error generating application: {e}")

        # Optional: View Current Knowledge Base
        st.sidebar.title("System Information")
        if st.sidebar.button("View Knowledge Base"):
            try:
                with open(self.knowledge_manager.knowledge_generator.prolog_file_path, 'r') as f:
                    knowledge_base = f.read()
                    st.sidebar.text_area(
                        "Knowledge Base Contents:",
                        value=knowledge_base,
                        height=400,
                        disabled=True
                    )
            except Exception as e:
                st.sidebar.error(f"Error reading knowledge base: {e}")

        # Reset System State Option
        if st.sidebar.button("Reset Expert System"):
            # Clear session state variables
            for key in ['patient_name', 'patient_facts', 'application_status', 'eligibility_result']:
                if key in st.session_state:
                    del st.session_state[key]

            # Use st.rerun() instead of experimental_rerun()
            st.rerun()

def main():
    expert_system = CKDFinancialAidExpertSystem()
    expert_system.run_expert_system()

if __name__ == "__main__":
    main()
