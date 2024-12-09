#pl_converter_3.py
import os
import re
import logging
from typing import List, Dict, Any, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


import openai


class AdvancedPrologKnowledgeBaseGenerator:
    def __init__(self,
                 openai_api_key: str = None,
                 prolog_file_path: str = 'ckd_financial_aid.pl',
                 log_path: str = 'knowledge_base.log'):
        """
        Initialize an advanced Prolog Knowledge Base Generator using LLM-powered knowledge extraction.

        This class provides a sophisticated system for:
        1. Converting natural language text to structured Prolog facts
        2. Refining extracted knowledge
        3. Maintaining a persistent knowledge base
        4. Comprehensive logging of knowledge extraction process

        Key Design Principles:
        - LLM-driven knowledge extraction
        - Modular and extensible architecture
        - Robust error handling
        - Detailed logging for traceability

        Args:
            openai_api_key (str, optional): OpenAI API key for LLM processing
            prolog_file_path (str): Path to store the Prolog knowledge base
            log_path (str): Path to store log files
        """
        # Configure comprehensive logging
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

        # Set up OpenAI and LLM Configuration
        self.setup_openai_configuration(openai_api_key)

        # Prolog file management
        self.prolog_file_path = prolog_file_path
        self._initialize_prolog_file()

        # Create advanced prompt templates
        self.extraction_prompt = self._create_knowledge_extraction_prompt()
        self.refinement_prompt = self._create_knowledge_refinement_prompt()

        # Initialize extraction and refinement chains
        self.extraction_chain = (
                {"user_input": RunnablePassthrough()}
                | self.extraction_prompt
                | self.llm
                | StrOutputParser()
        )

        self.knowledge_refinement_chain = (
                {"prolog_facts": RunnablePassthrough()}
                | self.refinement_prompt
                | self.llm
                | StrOutputParser()
        )

    def setup_openai_configuration(self, openai_api_key: str = None):
        """
        Securely set up OpenAI configuration with multiple fallback methods.

        This method ensures robust API key handling:
        1. Prioritizes passed key
        2. Falls back to environment variable
        3. Provides clear error messages

        Args:
            openai_api_key (str, optional): API key for OpenAI services
        """
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            raise ValueError("No OpenAI API key found. Please provide one.")

        openai.api_key = openai_api_key

        # Initialize LLM with nuanced settings
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Balanced between creativity and precision
            max_tokens=1024,  # Allow complex output generation
            api_key=openai_api_key
        )

    def _initialize_prolog_file(self):
        """
        Ensure Prolog knowledge base file exists and is properly initialized.

        Creates the file if it doesn't exist and adds a header comment.
        """
        if not os.path.exists(self.prolog_file_path):
            with open(self.prolog_file_path, 'w') as f:
                f.write('%% Prolog Knowledge Base\n')
                f.write('%% Created: {}\n'.format(os.path.basename(self.prolog_file_path)))
        logging.info(f"Initialized knowledge base at {self.prolog_file_path}")

    def _create_knowledge_extraction_prompt(self) -> PromptTemplate:
        """
        Create a sophisticated prompt for comprehensive knowledge extraction.

        Design goals:
        - Generate precise, semantically rich Prolog facts
        - Handle complex linguistic structures
        - Ensure consistent output format
        """
        return PromptTemplate(
            input_variables=['user_input'],
            template="""
        Prolog Knowledge Extraction with Controlled Vocabulary:

        Objective: Analyze the input text and generate Prolog facts using the controlled vocabulary defined below. Ensure that all facts are precisely structured to avoid inconsistency and follow the correct formats. Each fact must strictly adhere to the predefined predicates and their allowed values. If it's in a another language, translate it into english before using.

        Controlled Vocabulary:
        1. **Person**:
           - person(Name): Defines a person by their name.
           - age(Person, Age): Age of the person (integer, in years).
           - gender(Person, Gender): Gender of the person (e.g., 'male', 'female', 'other').
           - profession(Person, Job): Job or occupation of the person (e.g., 'teacher', 'engineer').
           - marital_status(Person, Status): Marital status (e.g., 'single', 'married', 'divorced').
           - education(Person, Level): Educational qualification (e.g., 'high school', 'bachelor's', 'PhD').

        2. **Health**:
           - health_condition(Person, Condition): Specific health conditions (e.g., 'stage_4_ckd', 'hypertension').
           - chronic_condition(Person, YesNo): If the person has a chronic condition ('yes' or 'no').
           - disability(Person, YesNo): Whether the person has a disability ('yes' or 'no').

        3. **Location**:
           - resides_in(Person, Area): Area of residence (e.g., 'urban', 'rural').
           - location(Person, Province): Geographical location (e.g., 'Colombo', 'Kandy').
           - commute_time(Person, Time): Commute time to work (in minutes).

        4. **Family**:
           - children(Person, Count): Number of children (integer).
           - dependent_children(Person, Count): Number of children under 18 (integer).
           - elderly_dependents(Person, Count): Number of elderly dependents (integer).
           - family_structure(Person, Structure): Describes the family structure (e.g., 'nuclear', 'extended').

        5. **Economic**:
           - monthly_income(Person, Amount): Monthly income (in local currency).
           - income_level(Person, Level): Income level classification ('low', 'middle', 'high').
           - fixed_income(Person, YesNo): Whether the person has a fixed income ('yes' or 'no').
           - debt_status(Person, YesNo): Whether the person has any debt ('yes' or 'no').

        6. **Additional Attributes**:
           - communication_preference(Person, Medium): Preferred communication medium (e.g., 'phone', 'email').
           - access_to_healthcare(Person, YesNo): Whether the person has access to healthcare services ('yes' or 'no').
           - language_spoken(Person, Language): Primary language spoken by the person (e.g., 'Sinhala', 'Tamil', 'English').

        Instructions:
        1. Each Prolog fact must be formatted as: `predicate(argument1, argument2, ...)`.
        2. Ensure that each fact follows the standardized vocabulary above. Do not deviate from the defined predicates or use synonyms.
        3. Always check that values are within allowed categories (e.g., use 'male' or 'female' for gender, not any other variations).
        4. If the input includes multiple facts about a person, generate a separate Prolog fact for each piece of information.

        Example Input:
        {user_input}

        Example Output:
        """
        )

    def _create_knowledge_refinement_prompt(self) -> PromptTemplate:
        """
        Create a sophisticated knowledge refinement prompt template.

        Refinement objectives:
        - Remove redundant facts
        - Infer implicit relationships
        - Ensure logical consistency
        - Standardize representation
        """
        return PromptTemplate(
            input_variables=['prolog_facts'],
            template="""Knowledge Refinement Process:

        Refine the following Prolog facts with these objectives:
        1. Eliminate redundant or semantically equivalent facts
        2. Infer potential missing relationships
        3. Ensure logical consistency and secure integrity 
        4. Standardize predicate naming and formatting

        Constraints:
        - Maintain original semantic meaning
        - Prefer more specific predicates
        - Remove overly generic facts
        - Add contextual relationships if possible

        Input Prolog Facts:
        {prolog_facts}

        Refined Knowledge Base:"""
        )

    def extract_advanced_knowledge(self, text: str) -> List[str]:
        """
        Advanced knowledge extraction using LLM with multi-stage processing.

        Args:
            text (str): Input natural language text

        Returns:
            List[str]: Structured Prolog facts
        """
        try:
            # Use LLM for comprehensive knowledge extraction
            llm_extraction = self.extraction_chain.invoke(text)
            print("llm_extraction", llm_extraction)

            # Parse and clean extracted facts
            prolog_facts = self._parse_llm_output(llm_extraction)
            # print("prolog_facts", prolog_facts)

            # Refine extracted knowledge
            refined_facts = self.refine_knowledge(prolog_facts)
            print("refined_facts", refined_facts)

            logging.info(f"Successfully extracted {len(refined_facts)} structured facts")
            return list(set(refined_facts))  # Remove duplicates

        except Exception as e:
            logging.error(f"Knowledge extraction failed: {e}")
            return []

    def refine_knowledge(self, prolog_facts: List[str]) -> List[str]:
        """
        Refine extracted knowledge using an advanced LLM-powered refinement process.

        Args:
            prolog_facts (List[str]): Initial set of Prolog facts

        Returns:
            List[str]: Refined and optimized Prolog facts
        """
        # Convert facts to a single string for processing
        facts_string = "\n".join(prolog_facts)

        try:
            # Invoke the refinement chain
            refined_facts_str = self.knowledge_refinement_chain.invoke(facts_string)

            # Parse the refined facts
            refined_facts = self._parse_llm_output(refined_facts_str)

            logging.info(f"Knowledge refinement successful. Refined {len(prolog_facts)} to {len(refined_facts)} facts.")

            return refined_facts

        except Exception as e:
            logging.error(f"Knowledge refinement failed: {e}")
            return prolog_facts  # Fallback to original facts if refinement fails

    def _parse_llm_output(self, llm_extraction: str) -> List[str]:
        """
        Parse and clean LLM-generated Prolog facts with enhanced extraction.

        This method aims to:
        1. Extract a wider range of valid Prolog facts based on the enhanced controlled vocabulary.
        2. Handle multi-word entities and complex predicates (e.g., health conditions, family structure).
        3. Maintain strict Prolog syntax validation.
        4. Provide detailed logging for parsing process.

        Args:
            llm_extraction (str): Raw LLM-generated text.

        Returns:
            List[str]: Cleaned and validated Prolog facts.
        """
        # Enhanced fact extraction pattern
        # Changes:
        # - Allow for single quotes around strings (e.g., 'Nimal Perera', 'hypertension')
        # - Supports multi-word arguments with underscores (e.g., stage_4_ckd, colombo)
        # - Ensures lowercase start for predicates and arguments
        # - Requires period at the end of each fact
        fact_pattern = re.compile(
            r'^[a-z][a-z0-9_]*\((?:[a-z0-9_]+(?:_[a-z0-9_]+)*|\'[^\']+\')(?:,\s*(?:[a-z0-9_]+(?:_[a-z0-9_]+)*|\'[^\']+\'))*\)\.$',
            re.MULTILINE
        )

        print("inside_parse", llm_extraction)

        # Extract potential facts based on the enhanced pattern
        potential_facts = fact_pattern.findall(llm_extraction)
        print("potential_facts:", potential_facts)

        # Additional cleaning and validation based on the expanded controlled vocabulary
        valid_facts = []
        for fact in potential_facts:
            # Ensure each fact strictly adheres to the Prolog fact format
            if re.match(
                    r'^[a-z][a-z0-9_]*\((?:[a-z0-9_]+(?:_[a-z0-9_]+)*|\'[^\']+\')(?:,\s*(?:[a-z0-9_]+(?:_[a-z0-9_]+)*|\'[^\']+\'))*\)\.$',
                    fact):
                # Check if the predicate matches the allowed controlled vocabulary
                predicate = fact.split('(')[0]
                valid_predicates = [
                    'person', 'age', 'gender', 'profession', 'marital_status', 'education',
                    'health_condition', 'chronic_condition', 'disability', 'resides_in',
                    'location', 'children', 'monthly_income', 'income_level', 'fixed_income',
                    'debt_status', 'communication_preference', 'access_to_healthcare', 'language_spoken',
                    'family_structure', 'dependent_children', 'elderly_dependents', 'commute_time'
                ]

                if predicate in valid_predicates:
                    valid_facts.append(fact.strip())

        # Logging for transparency
        logging.info(f"LLM Output Parsing: {len(potential_facts)} potential facts, {len(valid_facts)} validated")

        # Optional: Print debugging information if not all potential facts were validated
        if len(valid_facts) < len(potential_facts):
            logging.warning(f"Parsed only {len(valid_facts)}/{len(potential_facts)} facts due to strict validation")

        return valid_facts

    def convert_to_prolog(self, user_input: str) -> str:
        """
        Convert input to Prolog using the LLM conversion chain.

        Args:
            user_input (str): Natural language input

        Returns:
            str: Prolog-formatted facts
        """
        try:
            prolog_conversion = self.extraction_chain.invoke(user_input)
            logging.info(f"Successfully converted input to Prolog")
            return prolog_conversion
        except Exception as e:
            logging.error(f"Conversion error: {e}")
            raise

    def add_to_knowledge_base(self, prolog_facts: List[str]):
        """
        Add multiple Prolog facts to the knowledge base file.

        Args:
            prolog_facts (List[str]): Facts to add to the knowledge base
        """
        # Clean and validate facts
        valid_facts = [
            fact for fact in prolog_facts
            if self.validate_prolog_syntax(fact)
        ]

        if not valid_facts:
            logging.warning("No valid facts to add to knowledge base")
            return

        with open(self.prolog_file_path, 'a') as f:
            f.write('\n% New Knowledge Block\n')
            for fact in valid_facts:
                f.write(f"{fact}\n")

        logging.info(f"Added {len(valid_facts)} facts to knowledge base")

    def validate_prolog_syntax(self, prolog_fact: str) -> bool:
        """
        Validate individual Prolog fact syntax with enhanced flexibility.

        Improvements:
        - Allow multi-word arguments with underscores
        - Support numeric arguments
        - Maintain strict Prolog predicate naming rules

        Args:
            prolog_fact (str): Prolog fact to validate

        Returns:
            bool: Whether the fact has valid Prolog syntax
        """
        # Enhanced regex pattern with more flexible validation
        fact_pattern = re.compile(
            r'^[a-z][a-z0-9_]*\([a-z0-9_]+(?:_[a-z0-9_]+)*(?:,\s*[a-z0-9_]+(?:_[a-z0-9_]+)*)*\)\.$',
            re.MULTILINE
        )

        # Validate the fact
        is_valid = bool(fact_pattern.match(prolog_fact))

        # Optional: Add logging for validation process
        if not is_valid:
            logging.warning(f"Invalid Prolog fact syntax: {prolog_fact}")

        return is_valid

    def interactive_knowledge_builder(self):
        """
        Interactive knowledge base builder with advanced processing and refinement.

        Provides a CLI for users to interactively build a Prolog knowledge base.
        """
        print("🧠 Advanced Prolog Knowledge Base Builder")
        print("Enter complex text paragraphs. Type 'quit' to exit.\n")

        while True:
            user_input = input("Enter text to extract knowledge: ")

            if user_input.lower() == 'quit':
                break

            try:
                # Extract advanced knowledge with refinement
                prolog_facts = self.extract_advanced_knowledge(user_input)

                # Display extracted and refined facts
                print("\n🔍 Extracted & Refined Knowledge:")
                for fact in prolog_facts:
                    print(fact)

                # Confirm adding to knowledge base
                add_confirm = input("\nAdd these facts to knowledge base? (y/n): ")
                if add_confirm.lower() == 'y':
                    self.add_to_knowledge_base(prolog_facts)
                    print("✅ Facts added successfully!")

            except Exception as e:
                print(f"❌ Error processing input: {e}")
                logging.error(f"Processing error: {e}")

        def add_patient_information_with_validation(self, initial_description):
            """
            Enhanced method to collect patient information with interactive validation and completion.

            This method:
            1. Extracts initial facts from the description
            2. Identifies and prompts for missing critical information
            3. Ensures comprehensive patient profile creation
            """
            # Extract initial knowledge
            initial_facts = self.knowledge_generator.extract_advanced_knowledge(initial_description)

            # Critical attributes to check
            critical_attributes = [
                'person', 'age', 'gender', 'location',
                'profession', 'monthly_income', 'health_condition',
                'chronic_condition', 'education', 'family_structure'
            ]

            # Track which critical attributes are missing
            missing_attributes = []

            # Check for missing critical attributes
            for attr in critical_attributes:
                if not any(attr in fact for fact in initial_facts):
                    missing_attributes.append(attr)

            # Interactive prompts for missing information
            if missing_attributes:
                st.warning("Some critical information seems to be missing. Please provide additional details.")

                # Create a mapping of attributes to user-friendly prompts
                attribute_prompts = {
                    'age': "What is the patient's age?",
                    'gender': "What is the patient's gender?",
                    'location': "In which area or province does the patient reside?",
                    'profession': "What is the patient's current occupation?",
                    'monthly_income': "What is the patient's monthly income (in LKR)?",
                    'health_condition': "What is the specific health condition or CKD stage?",
                    'chronic_condition': "Does the patient have any other chronic conditions? (yes/no)",
                    'education': "What is the patient's highest level of education?",
                    'family_structure': "What is the patient's family structure? (nuclear/extended/single)"
                }

                # Collect missing information
                additional_info = {}
                for attr in missing_attributes:
                    prompt = attribute_prompts.get(attr, f"Please provide more information about {attr}")
                    response = st.text_input(prompt)
                    if response:
                        additional_info[attr] = response

                # Combine initial description with additional info
                enriched_description = initial_description
                for attr, value in additional_info.items():
                    enriched_description += f" {attr.replace('_', ' ').title()}: {value}."

                # Re-extract knowledge with enriched description
                final_facts = self.knowledge_generator.extract_advanced_knowledge(enriched_description)

                # Add to knowledge base
                self.knowledge_generator.add_to_knowledge_base(final_facts)

                return final_facts
            else:
                # If no missing attributes, proceed with initial extraction
                self.knowledge_generator.add_to_knowledge_base(initial_facts)
                return initial_facts


def main():
    """
    Main entry point for the Prolog Knowledge Base Generator.

    Handles initialization and provides user-friendly error messages.
    """
    try:
        # Initialize the knowledge base generator
        # Requires an OpenAI API key, either passed or in environment
        kb_generator = AdvancedPrologKnowledgeBaseGenerator()

        # Start interactive knowledge building
        kb_generator.interactive_knowledge_builder()

    except Exception as e:
        print(f"Initialization Error: {e}")
        print("Ensure you have a valid OpenAI API key set.")


if __name__ == '__main__':
    main()