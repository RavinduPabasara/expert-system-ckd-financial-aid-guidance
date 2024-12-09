import streamlit as st
from pl_converter_3 import AdvancedPrologKnowledgeBaseGenerator
import re


class CKDFinancialAidKnowledgeManager:
    def __init__(self, prolog_file_path='ckd_financial_aid.pl'):
        """
        Initialize a specialized knowledge manager for CKD Financial Aid system.
        """
        self.knowledge_generator = AdvancedPrologKnowledgeBaseGenerator(
            prolog_file_path=prolog_file_path
        )

        # Restore ALL critical attributes with comprehensive validation
        self.critical_attributes = {
            'location': {
                'prompt': "Province or District",
                'type': 'text',
                'validator': self._validate_location
            },
            'family_structure': {
                'prompt': "Family Structure",
                'type': 'select',
                'options': ['nuclear', 'extended', 'single'],
                'validator': self._validate_family_structure
            },
            'education': {
                'prompt': "Highest Education Level",
                'type': 'select',
                'options': ['primary', 'secondary', 'high school', 'bachelor', 'master', 'phd'],
                'validator': self._validate_education
            },
            'profession': {
                'prompt': "Current Occupation",
                'type': 'text',
                'validator': self._validate_profession
            },
            'monthly_income': {
                'prompt': "Monthly Income (LKR)",
                'type': 'number',
                'validator': self._validate_income
            },
            'chronic_condition': {
                'prompt': "Other Chronic Conditions",
                'type': 'select',
                'options': ['yes', 'no'],
                'validator': self._validate_yes_no
            }
        }

    def gather_missing_information(self, initial_facts):
        """
        Comprehensive method to gather missing patient information with enhanced state management.
        """
        # Debug: Print initial facts to verify input
        print("Initial Facts Received:", initial_facts)

        # Use Streamlit's session state to maintain persistent information
        if 'patient_missing_info' not in st.session_state:
            st.session_state.patient_missing_info = {}

        # Identify the patient name from initial facts
        person_name = next(
            (fact.split('(')[1].split(')')[0] for fact in initial_facts if fact.startswith('person(')),
            None
        )

        if not person_name:
            st.error("Could not identify patient name from initial facts.")
            return {}

        st.subheader(f"Additional Information for {person_name}")

        # Wrap the entire information gathering in a form to prevent unexpected reloads
        with st.form(key=f"additional_info_form_{person_name}", clear_on_submit=False):
            # Debug: Print current session state
            st.write("Current Session State:", st.session_state.patient_missing_info)

            # Track missing attributes
            missing_attrs = [
                attr for attr, details in self.critical_attributes.items()
                if not any(attr in fact for fact in initial_facts)
            ]

            st.write(f"Missing Attributes: {missing_attrs}")  # Explicit debug print

            # Information gathering for each missing attribute
            for attr in missing_attrs:
                details = self.critical_attributes[attr]

                # Retrieve existing value from session state or use default
                current_value = st.session_state.patient_missing_info.get(attr)

                if details['type'] == 'select':
                    # Selectbox with careful index management
                    index = details['options'].index(current_value) if current_value in details['options'] else 0
                    selected_value = st.selectbox(
                        label=f"Select {details['prompt']}",
                        options=details['options'],
                        index=index,
                        key=f"{person_name}_{attr}_select"
                    )
                    st.session_state.patient_missing_info[attr] = selected_value

                elif details['type'] == 'text':
                    text_value = st.text_input(
                        label=f"Enter {details['prompt']}",
                        value=current_value or '',
                        key=f"{person_name}_{attr}_text"
                    )
                    st.session_state.patient_missing_info[attr] = text_value

                elif details['type'] == 'number':
                    number_value = st.number_input(
                        label=f"Enter {details['prompt']}",
                        value=current_value or 0,
                        min_value=0,
                        key=f"{person_name}_{attr}_number"
                    )
                    st.session_state.patient_missing_info[attr] = number_value

            # Critical: Form submission button
            submitted = st.form_submit_button("Save Additional Information")

            if submitted:
                # Validation logic
                validated_info = {}
                for attr, value in st.session_state.patient_missing_info.items():
                    details = self.critical_attributes[attr]

                    # Skip validation for empty/zero values
                    if value is None or (isinstance(value, (int, float)) and value == 0):
                        continue

                    # Validate each attribute
                    if details['validator'](value):
                        validated_info[attr] = value
                    else:
                        st.warning(f"Invalid input for {details['prompt']}. Please check your entry.")

                # Return validated information or current session state
                return validated_info if validated_info else st.session_state.patient_missing_info

        # Fallback to session state
        return st.session_state.patient_missing_info


    def add_patient_information(self, patient_description, interactive=True):
        try:
            # Extract initial knowledge
            initial_facts = self.knowledge_generator.extract_advanced_knowledge(patient_description)

            # Identify the person's name from initial facts
            person_name = next(
                (fact.split('(')[1].split(')')[0] for fact in initial_facts if fact.startswith('person(')),
                None
            )

            if not person_name:
                st.error("Could not identify patient name from initial facts.")
                return initial_facts

            # If interactive mode is on, gather missing information
            if interactive:
                # Debug: Print initial facts before gathering additional info
                print("Initial Facts Before Additional Info:", initial_facts)

                additional_info = self.gather_missing_information(initial_facts)

                # Debug: Print additional information gathered
                print("Additional Information Gathered:", additional_info)

                # If additional information was gathered, create explicit Prolog facts
                if additional_info:
                    # Convert additional info to Prolog facts
                    additional_facts = [
                        f"{attr}({person_name}, {self._convert_to_prolog_term(value)})."
                        for attr, value in additional_info.items()
                        if value is not None and value != ''
                    ]

                    # Debug: Print additional facts being added
                    print("Additional Facts to Add:", additional_facts)

                    # Combine initial and additional facts, removing duplicates
                    final_facts = list(set(initial_facts + additional_facts))

                    # Add ALL facts to the knowledge base
                    self.knowledge_generator.add_to_knowledge_base(final_facts)

                    # Debug: Print final facts being saved
                    print("Final Facts Saved:", final_facts)

                    return final_facts
                else:
                    # Add initial facts to knowledge base if no additional info
                    self.knowledge_generator.add_to_knowledge_base(initial_facts)
                    return initial_facts
            else:
                # In non-interactive mode, just add initial facts
                self.knowledge_generator.add_to_knowledge_base(initial_facts)
                return initial_facts

        except Exception as e:
            st.error(f"Error adding patient information: {e}")
            # Print full traceback for debugging
            import traceback
            traceback.print_exc()
            return []



    def _convert_to_prolog_term(self, value):
        """
        Convert a value to a Prolog-friendly term.

        Args:
            value: Input value to be converted

        Returns:
            str: Prolog-friendly representation of the value
        """
        # Convert to lowercase and replace spaces with underscores
        if isinstance(value, str):
            # Remove quotes, convert to lowercase, replace spaces with underscores
            return value.lower().replace(' ', '_').strip("'\"")

        # For numeric values, convert to string
        return str(value).lower()
    def _validate_name(self, name):
        """Validate patient name."""
        return bool(re.match(r'^[A-Za-z\s]+$', str(name))) and len(str(name)) >= 2

    def _validate_age(self, age):
        """Validate patient age."""
        try:
            age = int(age)
            return 0 < age < 120
        except ValueError:
            return False

    def _validate_gender(self, gender):
        """Validate gender input."""
        return str(gender).lower() in ['male', 'female', 'other']

    def _validate_location(self, location):
        """Validate location input."""
        return bool(re.match(r'^[A-Za-z\s]+$', str(location))) and len(str(location)) >= 2

    def _validate_profession(self, profession):
        """Validate profession input."""
        return bool(re.match(r'^[A-Za-z\s]+$', str(profession))) and len(str(profession)) >= 2

    def _validate_income(self, income):
        """Validate monthly income."""
        try:
            income = float(income)
            return income >= 0
        except ValueError:
            return False

    def _validate_health_condition(self, condition):
        """Validate health condition input."""
        return bool(re.match(r'^[A-Za-z0-9\s]+$', str(condition))) and len(str(condition)) >= 2

    def _validate_yes_no(self, response):
        """Validate yes/no responses."""
        return str(response).lower() in ['yes', 'no']

    def _validate_education(self, education):
        """Validate education level input."""
        valid_levels = ['primary', 'secondary', 'high school', 'bachelor', 'master', 'phd']
        return str(education).lower() in valid_levels

    def _validate_family_structure(self, structure):
        """Validate family structure input."""
        valid_structures = ['nuclear', 'extended', 'single']
        return str(structure).lower() in valid_structures