#pl_intergration.py
from pyswip import Prolog
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize Prolog
prolog = Prolog()

# Load your Prolog file
prolog.consult("the_kb.pl")


# Function to query eligibility and other rules based on the person's name
def test_person(name):
    eligibility_query = f"eligible_for_aid({name})"
    eligibility = list(prolog.query(eligibility_query))

    if eligibility:
        print(f"{name} is eligible for aid.")
    else:
        print(f"{name} is not eligible for aid.")

    # Query for dialysis cost (only for stage 5 CKD)
    dialysis_query = f"dialysis_cost({name}, Cost)"
    dialysis = list(prolog.query(dialysis_query))

    if dialysis:
        print(f"Dialysis cost for {name}: LKR {dialysis[0]['Cost']}")
    else:
        print(f"No dialysis cost information for {name}.")

    # Query for indirect costs
    indirect_cost_query = f"indirect_cost({name}, TransportationCost, CaregivingCost)"
    indirect_cost = list(prolog.query(indirect_cost_query))

    if indirect_cost:
        print(
            f"Indirect costs for {name}: Transportation = LKR {indirect_cost[0]['TransportationCost']}, Caregiving = LKR {indirect_cost[0]['CaregivingCost']}")
    else:
        print(f"No indirect cost information for {name}.")

    # Query for recommended aid
    aid_query = f"recommended_aid({name}, TotalAid)"
    aid = list(prolog.query(aid_query))

    if aid:
        print(f"Recommended aid for {name}: LKR {aid[0]['TotalAid']}")
    else:
        print(f"No recommended aid information for {name}.")

    # Query for priority score
    priority_query = f"priority_score({name}, Priority)"
    priority = list(prolog.query(priority_query))

    if priority:
        print(f"Priority score for {name}: {priority[0]['Priority']}")
    else:
        print(f"No priority score information for {name}.")


class ApplicationDenialExplainer:
    def __init__(self, prolog_file_path="ckd_financial_aid.pl", api_key=None):
        """
        Initialize the Application Denial Explainer with Prolog and LLM capabilities.

        This class analyzes why a CKD patient's financial aid application might be denied
        and generates human-readable explanations.
        """
        if not api_key:
            import os
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass the key directly.")

        # Initialize Prolog
        self.prolog = Prolog()
        self.prolog.consult(prolog_file_path)

        # Initialize Language Model
        # Initialize Language Model with explicit API key
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=500
        )

        # Create denial reason explanation prompt
        self.denial_explanation_prompt = PromptTemplate(
            input_variables=['name', 'reasons', 'eligible_programs', 'non_eligible_programs'],
            template="""You are a compassionate healthcare administrative assistant named DIRI (Digital Interactive Resource Interface) explaining why a CKD patient's financial aid application was not fully approved.

        Patient Name: {name}

        Specific Denial Reasons:
        {reasons}

        Eligible Programs: {eligible_programs}
        Ineligible Programs: {non_eligible_programs}

        Please craft a comprehensive, empathetic explanation that:
        1. Breaks down each denial reason in simple, clear language
        2. Provides practical guidance on how the patient might become eligible
        3. Highlights any programs they are partially or fully eligible for
        4. Offers hope and constructive next steps
        5. Maintains a tone of support and understanding
        6. Suggests specific actions or resources the patient can pursue

        The explanation should feel personal, actionable, and encouraging. Avoid medical jargon and focus on clear, compassionate communication."""
        )

        # Update the denial explanation chain
        self.denial_explanation_chain = (
                self.denial_explanation_prompt
                | self.llm
                | StrOutputParser()
        )

        # Create explanation generation chain
        self.denial_explanation_chain = (
                self.denial_explanation_prompt
                | self.llm
                | StrOutputParser()
        )

    def analyze_application_denial(self, name):
        """
        Comprehensively analyze reasons for application denial.

        Checks multiple eligibility criteria and collects specific denial reasons.
        """
        person_exists_query = list(self.prolog.query(f"person({name})"))
        if not person_exists_query:
            return {
                "is_eligible": False,
                "denial_reasons": ["Person not found in the system"],
                "explanation": "No record exists for this individual in our database."
            }

        denial_reasons = []

        # Check monthly income eligibility
        income_query = list(self.prolog.query(f"monthly_income({name}, Income), Income > 30000"))
        if income_query:
            denial_reasons.append(
                f"Monthly income exceeds LKR 30,000 threshold (Current income: {income_query[0]['Income']} LKR)")

        # Check CKD stage
        stage_query = list(self.prolog.query(
            f"health_condition({name}, Condition), Condition \\= stage_4_ckd, Condition \\= stage_5_ckd"))
        if stage_query:
            denial_reasons.append(
                f"CKD stage does not meet program criteria (Current stage: {stage_query[0]['Condition']})")

        # Check healthcare access
        access_query = list(self.prolog.query(f"access_to_healthcare({name}, yes)"))
        if access_query:
            denial_reasons.append("Patient already has access to healthcare services")

        # Check document validation
        document_query = list(self.prolog.query(f"document_check({name}) -> false"))
        if document_query:
            denial_reasons.append("Missing or outdated required documents (income certificate or medical report)")

        # Generate explanation if reasons exist
        required_predicates = [
            f"monthly_income({name}, _)",
            f"health_condition({name}, _)",
            f"access_to_healthcare({name}, _)"
        ]

        for predicate in required_predicates:
            query_result = list(self.prolog.query(predicate))
            if not query_result:
                denial_reasons.append(f"Missing required data: {predicate}")

        if denial_reasons:
            explanation = self.generate_denial_explanation(denial_reasons)
            return {
                "is_eligible": False,
                "denial_reasons": denial_reasons,
                "explanation": explanation
            }

        return {"is_eligible": True, "denial_reasons": []}

    def generate_denial_explanation(self, name, denial_reasons, eligible_programs, non_eligible_programs):
        """
        Generate a comprehensive, compassionate explanation of eligibility status.

        Args:
            name (str): Patient's name
            denial_reasons (list): Specific reasons for program ineligibility
            eligible_programs (list): Programs the patient is eligible for
            non_eligible_programs (list): Programs the patient is not eligible for

        Returns:
            str: Detailed explanation of eligibility status
        """
        try:
            # Format denial reasons for readability
            formatted_reasons = "\n• " + "\n• ".join(denial_reasons) if denial_reasons else "No specific denial reasons"

            # Format program lists
            formatted_eligible = ", ".join(eligible_programs) if eligible_programs else "None"
            formatted_non_eligible = ", ".join(non_eligible_programs) if non_eligible_programs else "None"

            # Generate explanation using LLM
            explanation = self.denial_explanation_chain.invoke({
                "name": name,
                "reasons": formatted_reasons,
                "eligible_programs": formatted_eligible,
                "non_eligible_programs": formatted_non_eligible
            })

            return explanation

        except Exception as e:
            print(f"Error generating explanation: {e}")
            return (
                f"Dear {name},\n\n"
                "We apologize, but we encountered an issue generating a detailed explanation for your financial aid application. "
                "Our team is working to resolve this and will contact you soon with personalized guidance.\n\n"
                "Best regards,\nDIRI Support Team"
            )

    def analyze_eligibility(self, name):
        person_exists_query = list(self.prolog.query(f"person({name})"))
        if not person_exists_query:
            return {
                "is_eligible": False,
                "eligible_programs": [],
                "non_eligible_programs": [],
                "denial_reasons": ["Person not found in the system"],
                "explanation": "No record exists for this individual in our database."
            }

        # Comprehensive programs list
        all_programs = [
            ("suwa_ckd_aid", f"eligible_for_suwa_ckd_aid({name})"),
            ("diriya_support", f"eligible_for_diriya_support({name})"),
            ("thurunu_piyasa", f"eligible_for_thurunu_piyasa({name})"),
            ("sahana_healthcare", f"eligible_for_sahana_healthcare({name})"),
            ("divisaviya_income_support", f"eligible_for_divisaviya_income_support({name})"),
            ("nirmala_empowerment", f"eligible_for_nirmala_empowerment({name})"),
            ("daruwan_suraksha", f"eligible_for_daruwan_suraksha({name})"),
            ("govi_jana_support", f"eligible_for_govi_jana_support({name})"),
            ("arogya_elderly_care", f"eligible_for_arogya_elderly_care({name})")
        ]

        # Detailed program eligibility and reasons
        program_eligibility = {}
        denial_reasons = []
        eligible_programs = []
        non_eligible_programs = []

        for program, query in all_programs:
            program_query = list(self.prolog.query(query))
            if program_query:
                eligible_programs.append(program)
                program_eligibility[program] = True
            else:
                # Determine specific reasons for ineligibility
                non_eligible_programs.append(program)
                program_eligibility[program] = False

                # Specific ineligibility checks for each program
                if program == "suwa_ckd_aid":
                    age_check = list(self.prolog.query(f"age({name}, Age), Age =< 40"))
                    health_check = list(self.prolog.query(
                        f"health_condition({name}, Condition), (Condition \\= stage_4_ckd, Condition \\= stage_5_ckd)"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 25000"))

                    if age_check:
                        denial_reasons.append(f"Ineligible for {program}: Age is 40 or below")
                    if health_check:
                        denial_reasons.append(f"Ineligible for {program}: CKD stage does not meet criteria")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 25,000")

                elif program == "diriya_support":
                    status_check = list(self.prolog.query(f"marital_status({name}, Status), Status \\= single"))
                    children_check = list(self.prolog.query(f"dependent_children({name}, Children), Children =:= 0"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 20000"))

                    if status_check:
                        denial_reasons.append(f"Ineligible for {program}: Not a single parent")
                    if children_check:
                        denial_reasons.append(f"Ineligible for {program}: No dependent children")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 20,000")

                elif program == "thurunu_piyasa":
                    location_check = list(self.prolog.query(f"location({name}, Location), \\+ rural_area(Location)"))
                    education_check = list(self.prolog.query(f"education({name}, Level), Level \\= primary"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 15000"))

                    if location_check:
                        denial_reasons.append(f"Ineligible for {program}: Not in a rural area")
                    if education_check:
                        denial_reasons.append(f"Ineligible for {program}: Education level does not meet criteria")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 15,000")

                elif program == "sahana_healthcare":
                    chronic_check = list(self.prolog.query(f"chronic_condition({name}, Condition), Condition \\= yes"))
                    access_check = list(self.prolog.query(f"access_to_healthcare({name}, Status), Status = yes"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 20000"))

                    if chronic_check:
                        denial_reasons.append(f"Ineligible for {program}: No chronic condition")
                    if access_check:
                        denial_reasons.append(f"Ineligible for {program}: Already has healthcare access")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 20,000")

                elif program == "divisaviya_income_support":
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 15000"))
                    family_check = list(
                        self.prolog.query(f"family_structure({name}, Structure), Structure \\= nuclear"))

                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 15,000")
                    if family_check:
                        denial_reasons.append(f"Ineligible for {program}: Family structure does not meet criteria")

                elif program == "nirmala_empowerment":
                    gender_check = list(self.prolog.query(f"gender({name}, Gender), Gender \\= female"))
                    status_check = list(self.prolog.query(f"marital_status({name}, Status), Status \\= single"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 18000"))

                    if gender_check:
                        denial_reasons.append(f"Ineligible for {program}: Not female")
                    if status_check:
                        denial_reasons.append(f"Ineligible for {program}: Not single")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 18,000")

                elif program == "daruwan_suraksha":
                    children_check = list(self.prolog.query(f"children({name}, TotalChildren), TotalChildren =:= 0"))
                    dependent_check = list(
                        self.prolog.query(f"dependent_children({name}, DependentChildren), DependentChildren =:= 0"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 20000"))

                    if children_check:
                        denial_reasons.append(f"Ineligible for {program}: No children")
                    if dependent_check:
                        denial_reasons.append(f"Ineligible for {program}: No dependent children")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 20,000")

                elif program == "govi_jana_support":
                    profession_check = list(
                        self.prolog.query(f"profession({name}, Profession), Profession \\= part_time_tea_plucker"))
                    location_check = list(self.prolog.query(f"location({name}, Location), \\+ rural_area(Location)"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 18000"))

                    if profession_check:
                        denial_reasons.append(f"Ineligible for {program}: Not a part-time tea plucker")
                    if location_check:
                        denial_reasons.append(f"Ineligible for {program}: Not in a rural area")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 18,000")

                elif program == "arogya_elderly_care":
                    age_check = list(self.prolog.query(f"age({name}, Age), Age =< 60"))
                    income_check = list(self.prolog.query(f"monthly_income({name}, Income), Income >= 20000"))

                    if age_check:
                        denial_reasons.append(f"Ineligible for {program}: Age is 60 or below")
                    if income_check:
                        denial_reasons.append(f"Ineligible for {program}: Monthly income exceeds LKR 20,000")

        # Prepare final result
        result = {
            "is_eligible": len(eligible_programs) > 0,
            "eligible_programs": eligible_programs,
            "non_eligible_programs": non_eligible_programs,
            "denial_reasons": denial_reasons,
            "explanation": self.generate_denial_explanation(name, denial_reasons, eligible_programs,
                                                            non_eligible_programs)
        }

        return result
class ApplicationGenerator:
    def __init__(self, prolog_file_path="ckd_financial_aid.pl", api_key=None):
        """
        Initialize the Application Generator with Prolog and LLM capabilities.

        This class generates a financial aid application for a CKD patient based on available data.
        """
        # Use environment variable or passed API key
        if not api_key:
            api_key = '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'

        if not api_key:
            raise ValueError(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass the key directly.")

        # Initialize Prolog
        self.prolog = Prolog()
        self.prolog.consult(prolog_file_path)

        # Initialize Language Model
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4",
            temperature=0.3,
            max_tokens=500
        )

        # Create application generation prompt
        self.application_generator_prompt = PromptTemplate(
            input_variables=['details'],
            template="""You are an expert filling out a Chronic Kidney Disease Financial Aid Application Form for a person who is illiterate.

            Here are the details to include in the application:

            {details}

            Draft a Financial Aid Application with the following structure:
            1. Full Name:
            2. Full Name with Initials:
            3. Age:
            4. Location:
            5. Marital Status:
            6. Children Count:
            7. Elderly Dependent Count:
            8. Monthly Income:
            9. CKD Stage:
            10. Gender:
            """
        )

        # Create application generation chain
        self.generate_application_chain = (
                self.application_generator_prompt
                | self.llm
                | StrOutputParser()
        )

    def generate_application(self, name):
        """
        Generate the financial aid application for a given person.
        """
        # Check if person exists in Prolog knowledge base
        person_exists_query = list(self.prolog.query(f"person({name})"))
        if not person_exists_query:
            return {
                "is_eligible": False,
                "denial_reasons": ["Person not found in the system"],
                "explanation": "No record exists for this individual in our database.",
                "application_data": {},
                "application": "No application could be generated."
            }

        # Prepare application data and details
        details = []
        application_data = {"full_name": name}

        # Retrieve details from Prolog knowledge base
        queries = [
            ("age", "Age"),
            ("gender", "Gender"),
            ("location", "Location"),
            ("marital_status", "MaritalStatus"),
            ("dependent_children", "Count"),
            ("elderly_dependents", "Count"),
            ("monthly_income", "Income"),
            ("health_condition", "Condition")
        ]

        # Process each query and populate application data
        for predicate, variable in queries:
            query_result = list(self.prolog.query(f"{predicate}({name}, {variable})"))
            if query_result:
                value = query_result[0][variable]

                # Map Prolog query results to application data keys
                key_map = {
                    "Age": "age",
                    "Gender": "gender",
                    "Location": "location",
                    "MaritalStatus": "marital_status",
                    "Count": "children_count" if predicate == "dependent_children" else "elderly_dependent_count",
                    "Income": "monthly_income",
                    "Condition": "ckd_stage"
                }

                application_data[key_map[variable]] = value
                details.append(f"{predicate.replace('_', ' ').title()}: {value}")

        # Generate details text for LLM
        details_text = "\n".join(details)

        try:
            # Generate application using LLM
            generated_application = self.generate_application_chain.invoke({"details": details_text+" name of the applicant: "+name})
        except Exception as e:
            generated_application = f"Application generation error: {str(e)}"

        # Add full name with initials
        application_data["full_name_with_initials"] = " ".join([name[0] + "." for name in name.split()]) + " " + \
                                                      name.split()[-1]

        # # Determine eligibility (implement your specific criteria)
        # is_eligible = self._determine_eligibility(application_data)
        # denial_reasons = self._get_denial_reasons(application_data) if not is_eligible else []

        return {
            # "is_eligible": is_eligible,
            "application_data": application_data,
            # "denial_reasons": denial_reasons,
            # "explanation": "Application generated successfully." if is_eligible else "Application not eligible.",
            "application": str(generated_application)
        }


# Example Usage
def main():
    """
    Demonstrate the application denial analysis functionality.
    """
    explainer = ApplicationDenialExplainer()

    # Interactive demo
    while True:
        person_name = input("\nEnter the person's name (or 'quit' to exit): ")

        if person_name.lower() == 'quit':
            break

        result = explainer.analyze_application_denial(person_name)

        if result['is_eligible']:
            print(f"✅ {person_name} is eligible for financial aid.")
        else:
            print(f"❌ {person_name}'s application was not approved.")
            print("\n📋 Denial Reasons:")
            for reason in result['denial_reasons']:
                print(f"• {reason}")

            print("\n📝 Detailed Explanation:")
            print(result['explanation'])


if __name__ == "__main__":
    main()

