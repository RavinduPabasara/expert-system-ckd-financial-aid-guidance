import re
import logging
from typing import Dict, Any, List


class AdvancedCKDKnowledgeBaseGenerator:
    def __init__(self, log_path='ckd_knowledge_base.log'):
        """
        Initialize a specialized knowledge base generator for CKD financial aid.

        Focuses on:
        - Standardized knowledge representation
        - Robust fact validation
        - Comprehensive logging
        """
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

        # Predicate schemas for validation
        self.predicate_schemas = {
            'patient': ['unique_id', 'full_name', 'age', 'gender', 'nationality'],
            'health_condition': ['patient_id', 'condition', 'stage'],
            'socio_economic_profile': [
                'patient_id', 'monthly_income', 'income_source',
                'residence_type', 'dependent_count', 'employment_status'
            ],
            'medical_details': [
                'patient_id', 'primary_diagnosis',
                'treatment_plan', 'medical_expenses'
            ]
        }

    def validate_fact(self, predicate: str, arguments: List[Any]) -> bool:
        """
        Validate a Prolog fact against predefined schemas.

        Args:
            predicate (str): Name of the predicate
            arguments (List[Any]): Arguments to validate

        Returns:
            bool: Whether the fact is valid
        """
        if predicate not in self.predicate_schemas:
            logging.warning(f"Unknown predicate: {predicate}")
            return False

        schema = self.predicate_schemas[predicate]

        if len(arguments) != len(schema):
            logging.warning(f"Argument count mismatch for {predicate}")
            return False

        # Add type and range validations here
        return True

    def normalize_input(self, input_text: str) -> Dict[str, Any]:
        """
        Convert natural language input to structured knowledge.

        Uses pattern matching and rule-based extraction.

        Args:
            input_text (str): Natural language description

        Returns:
            Dict[str, Any]: Structured patient information
        """
        # Comprehensive extraction patterns
        patterns = [
            (r'(\w+)\s+is\s+a\s+(\d+)\s+years?\s+old\s+(\w+)',
             ['full_name', 'age', 'gender']),
            (r'monthly\s+income\s+is\s+(\d+)', ['monthly_income']),
            (r'stage\s+(\d+)\s+CKD', ['ckd_stage']),
            (r'lives\s+in\s+(\w+)', ['residence_type'])
        ]

        normalized_data = {}
        for pattern, keys in patterns:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                for i, key in enumerate(keys):
                    normalized_data[key] = match.group(i + 1)

        return normalized_data

    def generate_prolog_facts(self, patient_info: Dict[str, Any]) -> List[str]:
        """
        Generate standardized Prolog facts from patient information.

        Args:
            patient_info (Dict[str, Any]): Extracted patient details

        Returns:
            List[str]: Standardized Prolog facts
        """
        # Generate unique ID (could be more sophisticated)
        unique_id = patient_info.get('full_name', 'unknown').lower().replace(' ', '_')

        facts = [
            f"patient({unique_id}, '{patient_info.get('full_name', 'Unknown')}', {patient_info.get('age', 0)}, {patient_info.get('gender', 'unknown')}, sri_lankan).",
            f"health_condition({unique_id}, chronic_kidney_disease, {patient_info.get('ckd_stage', 0)}).",
            f"socio_economic_profile({unique_id}, {patient_info.get('monthly_income', 0)}, unknown, {patient_info.get('residence_type', 'unknown')}, 0, unknown)."
        ]

        return facts

    def process_patient_description(self, description: str) -> List[str]:
        """
        Comprehensive patient information processing pipeline.

        Args:
            description (str): Natural language patient description

        Returns:
            List[str]: Validated and normalized Prolog facts
        """
        try:
            # Normalize input
            normalized_data = self.normalize_input(description)

            # Generate facts
            prolog_facts = self.generate_prolog_facts(normalized_data)

            # Validate facts
            validated_facts = [
                fact for fact in prolog_facts
                if self.validate_fact(
                    fact.split('(')[0],
                    fact.split('(')[1].strip(').').split(',')
                )
            ]

            logging.info(f"Processed patient description: {validated_facts}")
            return validated_facts

        except Exception as e:
            logging.error(f"Error processing description: {e}")
            return []


def main():
    """
    Interactive patient description input for CKD Knowledge Base Generator.
    Allows users to:
    - Add multiple patient descriptions
    - Continue or exit the input process
    """
    generator = AdvancedCKDKnowledgeBaseGenerator()

    while True:
        # Prompt for patient description
        print("\n--- CKD Knowledge Base Patient Information Entry ---")
        print("Enter patient description (or 'done' to finish):")

        # Get user input
        user_input = input("> ").strip()

        # Check if user wants to exit
        if user_input.lower() == 'done':
            break

        # Process the patient description
        try:
            facts = generator.process_patient_description(user_input)

            # Check if any facts were generated
            if facts:
                print("\nGenerated Facts:")
                for fact in facts:
                    print(fact)
            else:
                print("\nNo valid facts could be extracted. Please check your input format.")

        except Exception as e:
            print(f"\nError processing description: {e}")

        # Option to continue or exit
        continue_input = input("\nDo you want to enter another patient description? (yes/no): ").strip().lower()
        if continue_input != 'yes':
            break

    print("\nThank you for using the CKD Knowledge Base Generator!")


if __name__ == "__main__":
    main()