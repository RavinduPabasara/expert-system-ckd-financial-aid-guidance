%% Prolog Knowledge Base
%% Created: ckd_financial_aid.pl

:- discontiguous person/1.
:- discontiguous gender/2.
:- discontiguous health_condition/2.
:- discontiguous age/2.
:- discontiguous age_of/2.
:- discontiguous has_dependents/2.
:- discontiguous monthly_income/2.
:- discontiguous resides_in/2.
:- discontiguous has_health_condition/2.
:- discontiguous income/3.
:- discontiguous has_children/1.
:- discontiguous number_of_children/2.
:- discontiguous is_parent/1.
:- discontiguous profession/2.
:- discontiguous child/3.
:- discontiguous marital_status/2.
:- discontiguous access_to_healthcare/2.
:- discontiguous debt_status/2.
:- discontiguous fixed_income/2.
:- discontiguous chronic_condition/2.
:- discontiguous location/2.
:- discontiguous language_spoken/2.
:- discontiguous communication_preference/2.
:- discontiguous dependent_children/2.
:- discontiguous elderly_dependents/2.
:- discontiguous income_certificate/2.
:- discontiguous medical_report/2.
:- discontiguous children/2.
:- discontiguous income_level/2.
 :-discontiguous family_structure/2.


has_all_required_data(Person) :-
    monthly_income(Person, Income),   % Ensure Income is bound
    Income \= 0,                      % Ensure Income is not zero
    monthly_income(Person, _),
    health_condition(Person, Condition),  % Ensure Condition is bound
    Condition \= unknown,
    access_to_healthcare(Person, Access),  % Ensure Access is bound
    Access \= unknown,
    document_check(Person).

missing_critical_data(Person) :-
    \+ monthly_income(Person, _);   % Missing income
    \+ access_to_healthcare(Person, _).   % Missing healthcare access

% Updated eligibility rule
eligible_for_aid(Person) :-
    \+ missing_critical_data(Person),  % Explicitly check for missing critical data
    has_all_required_data(Person),
    monthly_income(Person, Income),
    Income > 0,  % Explicitly require positive income
    Income =< 30000,
    health_condition(Person, Condition),
    (Condition = stage_4_ckd; Condition = stage_5_ckd),
    access_to_healthcare(Person, no),
    % Optional: Add document verification
    document_check(Person).

% Calculate Health Severity Score
health_severity_score(Person, Score) :-
    health_condition(Person, Condition),
    (Condition = stage_5_ckd -> Score = 40;
     Condition = stage_4_ckd -> Score = 30;
     Condition = stage_3_ckd -> Score = 20;
     Score = 0).

% Calculate Economic Vulnerability Score
economic_vulnerability_score(Person, Score) :-
    monthly_income(Person, Income),
    (Income =< 15000 -> Score = 30;
     Income =< 25000 -> Score = 20;
     Income =< 35000 -> Score = 10;
     Score = 0).

% Calculate Dependency Score
dependency_score(Person, Score) :-
    (dependent_children(Person, NumChildren) ->
        (NumChildren > 0 -> ChildScore = 10; ChildScore = 0)
    ;   ChildScore = 0),
    (elderly_dependents(Person, NumElderly) ->
        (NumElderly > 0 -> ElderScore = 10; ElderScore = 0)
    ;   ElderScore = 0),
    Score is ChildScore + ElderScore.

% Calculate Accessibility Score
accessibility_score(Person, Score) :-
    access_to_healthcare(Person, Access),
    (Access = no -> Score = 10;
     Score = 5).

% Total Matching Score
total_aid_match_score(Person, TotalScore) :-
    health_severity_score(Person, HealthScore),
    economic_vulnerability_score(Person, EconomicScore),
    dependency_score(Person, DependencyScore),
    accessibility_score(Person, AccessibilityScore),
    TotalScore is HealthScore + EconomicScore + DependencyScore + AccessibilityScore.

% Recommend Most Suitable Aid Program
recommend_aid_program(Person, RecommendedProgram) :-
    total_aid_match_score(Person, Score),
    health_condition(Person, Condition),
    monthly_income(Person, Income),

    % Complex Program Matching Logic
    (Condition = stage_5_ckd, Income =< 15000 ->
        RecommendedProgram = 'Comprehensive Chronic Care Program';

     Condition = stage_4_ckd, access_to_healthcare(Person, no) ->
        RecommendedProgram = 'Emergency Medical Support Program';

     resides_in(Person, rural), Condition = stage_3_ckd ->
        RecommendedProgram = 'Rural Healthcare Access Program';

     dependent_children(Person, NumChildren),
     NumChildren > 0, Income =< 30000 ->
        RecommendedProgram = 'Dependent Care Support Program';

     profession(Person, Profession),
     member(Profession, [farmer, fisherman, laborer]),
     Condition = stage_3_ckd ->
        RecommendedProgram = 'Professional Rehabilitation Program';

     RecommendedProgram = 'Emergency Medical Support Program').


%% Dialysis Cost Rule
% The cost for dialysis is LKR 5000 per session. A person with stage 5 CKD requires 3 sessions per week.
dialysis_cost(Person, Cost) :-
    health_condition(Person, stage_5_ckd),
    Cost is 3 * 5000.  % LKR 5000 per session, 3 times per week

%% Indirect Costs Rule
% Transport cost per child and elderly dependent, caregiving cost per dependent.
indirect_cost(Person, TransportationCost, CaregivingCost) :-
    (dependent_children(Person, NumChildren) -> true; NumChildren = 0),  % Default to 0 if not available
    (elderly_dependents(Person, NumElderly) -> true; NumElderly = 0),  % Default to 0 if not available
    TransportationCost is (NumChildren + NumElderly) * 800,  % Transport cost per person
    CaregivingCost is (NumChildren + NumElderly) * 2000.  % Caregiving cost per person

%% Aid Optimization Rule
% Calculate total aid based on dialysis costs, transportation, caregiving, and nutritional support.
recommended_aid(Person, TotalAid) :-
    (dialysis_cost(Person, DialysisCost) -> true; DialysisCost = 0),  % Default to 0 if no dialysis cost
    (indirect_cost(Person, TransportationCost, CaregivingCost) -> true; (TransportationCost = 0, CaregivingCost = 0)),  % Default to 0 if no indirect costs
    NutritionalSupport = 3000,  % Fixed nutritional support
    TotalAid is DialysisCost + TransportationCost + CaregivingCost + NutritionalSupport.

% Advanced Priority Scoring Rule
priority_score(Person, Priority) :-
    % Health Stage Impact
    health_condition(Person, Health),
    (Health = stage_5_ckd ->
        StageFactor = 60  % Higher priority for most critical stage
    ;
        StageFactor = 40  % Lower, but still significant for stage 4
    ),

    % Income Vulnerability
    monthly_income(Person, Income),
    IncomeFactor is max(0, 30 - (Income // 1000)),  % More points for lower income

    % Dependency Burden
    (dependent_children(Person, NumChildren) -> true; NumChildren = 0),
    (elderly_dependents(Person, NumElderly) -> true; NumElderly = 0),
    DependencyFactor is (NumChildren * 10) + (NumElderly * 15),

    % Healthcare Access Penalty
    (access_to_healthcare(Person, no) -> AccessPenalty = 20; AccessPenalty = 0),

    % Final Priority Calculation
    Priority is 100 - StageFactor - IncomeFactor + DependencyFactor - AccessPenalty.

%% Document Validation Rule
% Ensure that the person has required documents such as income certificate and medical report issued within the last 3 months.
document_check(Person) :-
    (income_certificate(Person, yes) -> true; fail),  % Ensure income certificate exists
    (medical_report(Person, recent) -> true; fail).  % Ensure medical report is recent

%% Aid Programs
% Available aid programs and their renewal requirements.
aid_program('Program A', 'LKR 20,000 monthly for dialysis-related expenses', '6 months renewal required').
aid_program('Program B', 'LKR 15,000 monthly for transport and caregiving', '12 months renewal required').


% New Knowledge Block
location(suwanthika_kumari, polonnaruwa).
profession(suwanthika_kumari, part_time_tea_plucker).
monthly_income(suwanthika_kumari, 12000).
marital_status(suwanthika_kumari, single).
chronic_condition(suwanthika_kumari, yes).
children(suwanthika_kumari, 2).
gender(suwanthika_kumari, female).
education(suwanthika_kumari, primary).
dependent_children(suwanthika_kumari, 2).
family_structure(suwanthika_kumari, nuclear).
age(suwanthika_kumari, 42).
health_condition(suwanthika_kumari, stage_4_ckd).
access_to_healthcare(suwanthika_kumari, no).
person(suwanthika_kumari).
communication_preference(suwanthika_kumari, community_support).

% New Knowledge Block
location(ranjith_perera, dambulla).
family_structure(ranjith_perera, nuclear).
fixed_income(ranjith_perera, no).
gender(ranjith_perera, male).
debt_status(ranjith_perera, yes).
health_condition(ranjith_perera, stage_5_ckd).
age(ranjith_perera, 47).
profession(ranjith_perera, farmer).
chronic_condition(ranjith_perera, yes).
monthly_income(ranjith_perera, 18000).
access_to_healthcare(ranjith_perera, no).
language_spoken(ranjith_perera, sinhala).
person(ranjith_perera).
children(ranjith_perera, 3).

% New Knowledge Block
gender(sivapalan_rajendran, male).
location(sivapalan_rajendran, vavuniya).
access_to_healthcare(sivapalan_rajendran, no).
family_structure(sivapalan_rajendran, nuclear).
person(sivapalan_rajendran).
age(sivapalan_rajendran, 50).
education(sivapalan_rajendran, primary).
resides_in(sivapalan_rajendran, rural).
chronic_condition(sivapalan_rajendran, yes).
profession(sivapalan_rajendran, carpenter).
monthly_income(sivapalan_rajendran, 20000).
language_spoken(sivapalan_rajendran, tamil).
health_condition(sivapalan_rajendran, stage_4_ckd).

% New Knowledge Block
person(anoma_karunaratne).
income_level(anoma_karunaratne, high).
profession(anoma_karunaratne, school_principal).
chronic_condition(anoma_karunaratne, yes).
access_to_healthcare(anoma_karunaratne, yes).
health_condition(anoma_karunaratne, stage_2_ckd).
age(anoma_karunaratne, 52).
family_structure(anoma_karunaratne, nuclear).
communication_preference(anoma_karunaratne, email).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
gender(anoma_karunaratne, female).
marital_status(anoma_karunaratne, married).
location(anoma_karunaratne, kandy).
language_spoken(anoma_karunaratne, sinhala).

% New Knowledge Block
person(nimalini_wickremesinghe).
access_to_healthcare(nimalini_wickremesinghe, no).
location(nimalini_wickremesinghe, monaragala).
elderly_dependents(nimalini_wickremesinghe, 1).
profession(nimalini_wickremesinghe, garment_worker).
chronic_condition(nimalini_wickremesinghe, yes).
gender(nimalini_wickremesinghe, female).
language_spoken(nimalini_wickremesinghe, sinhala).
dependent_children(nimalini_wickremesinghe, 1).
education(nimalini_wickremesinghe, primary).
monthly_income(nimalini_wickremesinghe, 14000).
age(nimalini_wickremesinghe, 35).
health_condition(nimalini_wickremesinghe, stage_3_ckd).
family_structure(nimalini_wickremesinghe, nuclear).

% New Knowledge Block
elderly_dependents(nimalini_wickremesinghe, 1).
person(nimalini_wickremesinghe).
chronic_condition(nimalini_wickremesinghe, yes).
access_to_healthcare(nimalini_wickremesinghe, no).
health_condition(nimalini_wickremesinghe, stage_3_ckd).
language_spoken(nimalini_wickremesinghe, sinhala).
family_structure(nimalini_wickremesinghe, nuclear).
monthly_income(nimalini_wickremesinghe, 14000).
children(nimalini_wickremesinghe, 2).
age(nimalini_wickremesinghe, 35).
education(nimalini_wickremesinghe, primary).
location(nimalini_wickremesinghe, monaragala).
gender(nimalini_wickremesinghe, female).
profession(nimalini_wickremesinghe, garment_worker).

% New Knowledge Block
profession(abdul_kareem, fisherman).
gender(abdul_kareem, male).
family_structure(abdul_kareem, nuclear).
monthly_income(abdul_kareem, 16000).
health_condition(abdul_kareem, stage_4_ckd).
chronic_condition(abdul_kareem, yes).
person(abdul_kareem).
education(abdul_kareem, primary).
age(abdul_kareem, 41).
access_to_healthcare(abdul_kareem, no).
location(abdul_kareem, trincomalee).

% New Knowledge Block
chronic_condition(mihin_nimsara, yes).
location(mihin_nimsara, kandy).
family_structure(mihin_nimsara, nuclear).
profession(mihin_nimsara, school_principal).
access_to_healthcare(mihin_nimsara, yes).
language_spoken(mihin_nimsara, sinhala).
gender(mihin_nimsara, male).
health_condition(mihin_nimsara, stage_2_ckd).
age(mihin_nimsara, 52).
person(mihin_nimsara).
education(mihin_nimsara, primary).
marital_status(mihin_nimsara, married).
monthly_income(mihin_nimsara, 120000).
communication_preference(mihin_nimsara, email).

% New Knowledge Block
gender(saman_bandula, male).
marital_status(saman_bandula, married).
profession(saman_bandula, farmer).
person(saman_bandula).
resides_in(saman_bandula, rural).
health_condition(saman_bandula, stage_5_ckd).
language_spoken(saman_bandula, sinhala).
debt_status(saman_bandula, yes).
family_structure(saman_bandula, nuclear).
education(saman_bandula, primary).
monthly_income(saman_bandula, 45000).
communication_preference(saman_bandula, phone).
chronic_condition(saman_bandula, yes).
location(saman_bandula, matale).
age(saman_bandula, 48).
fixed_income(saman_bandula, no).
access_to_healthcare(saman_bandula, no).

% New Knowledge Block
profession(somasundaram_selvakumar, tractor_driver).
language_spoken(somasundaram_selvakumar, tamil).
age(somasundaram_selvakumar, 44).
fixed_income(somasundaram_selvakumar, no).
gender(somasundaram_selvakumar, male).
access_to_healthcare(somasundaram_selvakumar, no).
chronic_condition(somasundaram_selvakumar, yes).
location(somasundaram_selvakumar, kilinochchi).
person(somasundaram_selvakumar).
monthly_income(somasundaram_selvakumar, 98000).
health_condition(somasundaram_selvakumar, stage_4_ckd).
education(somasundaram_selvakumar, primary).
family_structure(somasundaram_selvakumar, nuclear).
income_level(somasundaram_selvakumar, low).

% New Knowledge Block
person(chandana_weerasinghe).
family_structure(chandana_weerasinghe, nuclear).
language_spoken(chandana_weerasinghe, sinhala).
monthly_income(chandana_weerasinghe, 82000).
health_condition(chandana_weerasinghe, stage_5_ckd).
elderly_dependents(chandana_weerasinghe, 0).
location(chandana_weerasinghe, mahiyanganaya).
children(chandana_weerasinghe, 0).
age(chandana_weerasinghe, 53).
access_to_healthcare(chandana_weerasinghe, no).
gender(chandana_weerasinghe, male).
fixed_income(chandana_weerasinghe, yes).
education(chandana_weerasinghe, primary).
communication_preference(chandana_weerasinghe, community_based_assistance_programs).
chronic_condition(chandana_weerasinghe, yes).
dependent_children(chandana_weerasinghe, 0).
profession(chandana_weerasinghe, retired_mason).

% New Knowledge Block
family_structure(somasundaram_selvakumar, nuclear).
health_condition(somasundaram_selvakumar, stage_4_ckd).
gender(somasundaram_selvakumar, male).
chronic_condition(somasundaram_selvakumar, yes).
language_spoken(somasundaram_selvakumar, tamil).
access_to_healthcare(somasundaram_selvakumar, no).
education(somasundaram_selvakumar, primary).
communication_preference(somasundaram_selvakumar, phone).
profession(somasundaram_selvakumar, tractor_driver).
person(somasundaram_selvakumar).
age(somasundaram_selvakumar, 44).
location(somasundaram_selvakumar, kilinochchi).
monthly_income(somasundaram_selvakumar, 18000).
fixed_income(somasundaram_selvakumar, no).

% New Knowledge Block
family_structure(somasundaram_selvakumar, nuclear).
health_condition(somasundaram_selvakumar, stage_4_ckd).
gender(somasundaram_selvakumar, male).
chronic_condition(somasundaram_selvakumar, yes).
language_spoken(somasundaram_selvakumar, tamil).
access_to_healthcare(somasundaram_selvakumar, no).
education(somasundaram_selvakumar, primary).
monthly_income(somasundaram_selvakumar, 98000).
profession(somasundaram_selvakumar, tractor_driver).
location(somasundaram_selvakumar, kilinochchi).
person(somasundaram_selvakumar).
age(somasundaram_selvakumar, 44).
fixed_income(somasundaram_selvakumar, no).

% New Knowledge Block
marital_status(kigali_karunaratne, married).
location(kigali_karunaratne, kandy).
age(kigali_karunaratne, 52).
profession(kigali_karunaratne, school_principal).
family_structure(kigali_karunaratne, nuclear).
chronic_condition(kigali_karunaratne, yes).
income_level(kigali_karunaratne, high).
education(kigali_karunaratne, primary).
communication_preference(kigali_karunaratne, email).
person(kigali_karunaratne).
gender(kigali_karunaratne, female).
monthly_income(kigali_karunaratne, 120000).
language_spoken(kigali_karunaratne, sinhala).

% New Knowledge Block
monthly_income(mini_karunaratne, 120000).
education(mini_karunaratne, primary).
gender(mini_karunaratne, female).
health_condition(mini_karunaratne, stage_2_ckd).
income_level(mini_karunaratne, high).
marital_status(mini_karunaratne, married).
access_to_healthcare(mini_karunaratne, yes).
profession(mini_karunaratne, school_principal).
family_structure(mini_karunaratne, nuclear).
communication_preference(mini_karunaratne, email).
language_spoken(mini_karunaratne, sinhala).
person(mini_karunaratne).
chronic_condition(mini_karunaratne, yes).
location(mini_karunaratne, kandy).
age(mini_karunaratne, 52).

% New Knowledge Block
family_structure(sunil_kumar, extended).
debt_status(sunil_kumar, yes).
gender(sunil_kumar, male).
access_to_healthcare(sunil_kumar, no).
monthly_income(sunil_kumar, 28000).
education(sunil_kumar, primary).
age(sunil_kumar, 42).
marital_status(sunil_kumar, married).
profession(sunil_kumar, farmer).
health_condition(sunil_kumar, stage_5_ckd).
communication_preference(sunil_kumar, phone).
fixed_income(sunil_kumar, no).
person(sunil_kumar).
location(sunil_kumar, batticaloa).
chronic_condition(sunil_kumar, yes).
language_spoken(sunil_kumar, tamil).

% New Knowledge Block
resides_in(sunil_kumar, rural_batticaloa).
family_structure(sunil_kumar, extended).
elderly_dependents(sunil_kumar, 1).
profession(sunil_kumar, farmer).
marital_status(sunil_kumar, married).
gender(sunil_kumar, male).
access_to_healthcare(sunil_kumar, no).
chronic_condition(sunil_kumar, stage_5_ckd).
dependent_children(sunil_kumar, 2).
age(sunil_kumar, 42).
person(sunil_kumar).
education(sunil_kumar, primary).
language_spoken(sunil_kumar, tamil).
debt_status(sunil_kumar, yes).
fixed_income(sunil_kumar, no).
communication_preference(sunil_kumar, phone).
monthly_income(sunil_kumar, 28000).

% New Knowledge Block
location(nimal_perera, colombo).
person(nimal_perera).
profession(nimal_perera, teacher).
family_structure(nimal_perera, nuclear).
education(nimal_perera, primary).
age(nimal_perera, 45).
monthly_income(nimal_perera, 100000).
gender(nimal_perera, male).
health_condition(nimal_perera, stage_4_ckd).
marital_status(nimal_perera, married).
chronic_condition(nimal_perera, yes).
health_condition(nimal_perera, hypertension).

% New Knowledge Block
monthly_income(jamal_perera, 100000).
health_condition(jamal_perera, stage_4_ckd).
access_to_healthcare(jamal_perera, yes).
family_structure(jamal_perera, nuclear).
location(jamal_perera, colombo).
profession(jamal_perera, teacher).
marital_status(jamal_perera, married).
age(jamal_perera, 45).
gender(jamal_perera, male).
person(jamal_perera).
health_condition(jamal_perera, hypertension).
chronic_condition(jamal_perera, yes).
education(jamal_perera, primary).

% New Knowledge Block
family_structure(lahiru_perera, nuclear).
location(lahiru_perera, colombo).
age(lahiru_perera, 45).
profession(lahiru_perera, teacher).
health_condition(lahiru_perera, hypertension).
person(lahiru_perera).
gender(lahiru_perera, male).
chronic_condition(lahiru_perera, yes).
education(lahiru_perera, primary).
marital_status(lahiru_perera, married).
health_condition(lahiru_perera, stage_4_ckd).
monthly_income(lahiru_perera, 100000).

% New Knowledge Block
health_condition(kamal_perera, stage_4_ckd).
chronic_condition(kamal_perera, yes).
monthly_income(kamal_perera, 100000).
education(kamal_perera, primary).
family_structure(kamal_perera, nuclear).
gender(kamal_perera, male).
location(kamal_perera, colombo).
profession(kamal_perera, teacher).
person(kamal_perera).
age(kamal_perera, 45).
marital_status(kamal_perera, married).

% New Knowledge Block
person(janoma_karunaratne).
access_to_healthcare(janoma_karunaratne, yes).
health_condition(janoma_karunaratne, stage_2_ckd).
marital_status(janoma_karunaratne, married).
age(janoma_karunaratne, 52).
gender(janoma_karunaratne, female).
monthly_income(janoma_karunaratne, 120000).
communication_preference(janoma_karunaratne, email).
profession(janoma_karunaratne, school_principal).
chronic_condition(janoma_karunaratne, yes).
income_level(janoma_karunaratne, high).
language_spoken(janoma_karunaratne, sinhala).
education(janoma_karunaratne, primary).
family_structure(janoma_karunaratne, nuclear).
location(janoma_karunaratne, kandy).

% New Knowledge Block
person(janoma_karunaratne).
access_to_healthcare(janoma_karunaratne, yes).
health_condition(janoma_karunaratne, stage_2_ckd).
marital_status(janoma_karunaratne, married).
age(janoma_karunaratne, 52).
gender(janoma_karunaratne, female).
monthly_income(janoma_karunaratne, 120000).
communication_preference(janoma_karunaratne, email).
profession(janoma_karunaratne, school_principal).
chronic_condition(janoma_karunaratne, yes).
income_level(janoma_karunaratne, high).
language_spoken(janoma_karunaratne, sinhala).
education(janoma_karunaratne, primary).
family_structure(janoma_karunaratne, nuclear).
location(janoma_karunaratne, kandy).

% New Knowledge Block
gender(anoma_karunaratne, female).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
age(anoma_karunaratne, 52).
profession(anoma_karunaratne, school_principal).
family_structure(anoma_karunaratne, nuclear).
access_to_healthcare(anoma_karunaratne, yes).
income_level(anoma_karunaratne, high).
person(anoma_karunaratne).
health_condition(anoma_karunaratne, stage_2_ckd).
marital_status(anoma_karunaratne, married).
chronic_condition(anoma_karunaratne, yes).

% New Knowledge Block
marital_status(sunil_perera, married).
person(sunil_perera).
family_structure(sunil_perera, nuclear).
communication_preference(sunil_perera, face_to_face).
chronic_condition(sunil_perera, yes).
monthly_income(sunil_perera, 35000).
gender(sunil_perera, male).
education(sunil_perera, primary).
health_condition(sunil_perera, stage_4_ckd).
location(sunil_perera, anuradhapura).
profession(sunil_perera, farmer).
language_spoken(sunil_perera, sinhala).
age(sunil_perera, 46).

% New Knowledge Block
health_condition(malathi_silva, stage_4_ckd).
fixed_income(malathi_silva, yes).
age(malathi_silva, 58).
communication_preference(malathi_silva, phone).
monthly_income(malathi_silva, 50000).
location(malathi_silva, galle).
education(malathi_silva, primary).
resides_in(malathi_silva, urban).
gender(malathi_silva, female).
profession(malathi_silva, teacher).
chronic_condition(malathi_silva, yes).
family_structure(malathi_silva, nuclear).
language_spoken(malathi_silva, sinhala).
person(malathi_silva).

% New Knowledge Block
location(tharuka_silva, galle).
access_to_healthcare(tharuka_silva, yes).
family_structure(tharuka_silva, nuclear).
fixed_income(tharuka_silva, yes).
health_condition(tharuka_silva, stage_4_ckd).
children(tharuka_silva, 2).
chronic_condition(tharuka_silva, yes).
age(tharuka_silva, 58).
profession(tharuka_silva, teacher).
monthly_income(tharuka_silva, 20000).
education(tharuka_silva, primary).
gender(tharuka_silva, female).
person(tharuka_silva).
communication_preference(tharuka_silva, phone).
dependent_children(tharuka_silva, 0).
language_spoken(tharuka_silva, sinhala).

% New Knowledge Block
marital_status(mohammed_farook, married).
person(mohammed_farook).
family_structure(mohammed_farook, nuclear).
gender(mohammed_farook, male).
education(mohammed_farook, primary).
monthly_income(mohammed_farook, 85000).
access_to_healthcare(mohammed_farook, yes).
age(mohammed_farook, 63).
profession(mohammed_farook, shopkeeper).
chronic_condition(mohammed_farook, yes).

% New Knowledge Block
gender(manodya_fook, male).
health_condition(manodya_fook, hypertension).
marital_status(manodya_fook, married).
location(manodya_fook, colombo).
health_condition(manodya_fook, diabetes).
age(manodya_fook, 23).
communication_preference(manodya_fook, whatsapp).
family_structure(manodya_fook, nuclear).
education(manodya_fook, primary).
profession(manodya_fook, shopkeeper).
communication_preference(manodya_fook, email).
access_to_healthcare(manodya_fook).
resides_in(manodya_fook, urban).
monthly_income(manodya_fook, 15000).
chronic_condition(manodya_fook, yes).
person(manodya_fook).

% New Knowledge Block
gender(manodya_fook, male).
health_condition(manodya_fook, stage_2_ckd).
health_condition(manodya_fook, hypertension).
marital_status(manodya_fook, married).
location(manodya_fook, colombo).
communication_preference(manodya_fook, whatsapp).
access_to_healthcare(manodya_fook, yes).
family_structure(manodya_fook, nuclear).
education(manodya_fook, primary).
profession(manodya_fook, shopkeeper).
language_spoken(manodya_fook, tamil).
communication_preference(manodya_fook, email).
monthly_income(manodya_fook, 15000).
chronic_condition(manodya_fook, yes).
age(manodya_fook, 65).
person(manodya_fook).

% New Knowledge Block
profession(minodya_fook, shopkeeper).
fixed_income(minodya_fook, yes).
chronic_condition(minodya_fook, yes).
access_to_healthcare(minodya_fook, yes).
monthly_income(minodya_fook, 15000).
person(minodya_fook).
family_structure(minodya_fook, nuclear).
age(minodya_fook, 65).
education(minodya_fook, primary).
location(minodya_fook, colombo).
resides_in(minodya_fook, urban).
marital_status(minodya_fook, married).
gender(minodya_fook, male).

% New Knowledge Block
profession(kusum_wijeratne, factory_worker).
language_spoken(kusum_wijeratne, sinhala).
person(kusum_wijeratne).
gender(kusum_wijeratne, female).
communication_preference(kusum_wijeratne, sms).
family_structure(kusum_wijeratne, nuclear).
monthly_income(kusum_wijeratne, 28000).
age(kusum_wijeratne, 40).
location(kusum_wijeratne, kurunegala).
education(kusum_wijeratne, primary).
chronic_condition(kusum_wijeratne, yes).
health_condition(kusum_wijeratne, stage_3_ckd).
access_to_healthcare(kusum_wijeratne, yes).
marital_status(kusum_wijeratne, single).
elderly_dependents(kusum_wijeratne, 2).

% New Knowledge Block
location(tharuka_wijeratne, kurunegala).
education(tharuka_wijeratne, primary).
elderly_dependents(tharuka_wijeratne, 2).
monthly_income(tharuka_wijeratne, 28000).
age(tharuka_wijeratne, 40).
health_condition(tharuka_wijeratne, stage_5_ckd).
gender(tharuka_wijeratne, female).
profession(tharuka_wijeratne, factory_worker).
person(tharuka_wijeratne).
family_structure(tharuka_wijeratne, nuclear).
access_to_healthcare(tharuka_wijeratne, yes).
marital_status(tharuka_wijeratne, unmarried).
language_spoken(tharuka_wijeratne, sinhala).
chronic_condition(tharuka_wijeratne, yes).
communication_preference(tharuka_wijeratne, sms).

% New Knowledge Block
profession(kusum_wijeratne, factory_worker).
language_spoken(kusum_wijeratne, sinhala).
person(kusum_wijeratne).
gender(kusum_wijeratne, female).
age(kusum_wijeratne, 23).
communication_preference(kusum_wijeratne, sms).
marital_status(kusum_wijeratne, unmarried).
monthly_income(kusum_wijeratne, 28000).
location(kusum_wijeratne, kurunegala).
education(kusum_wijeratne, primary).
chronic_condition(kusum_wijeratne, yes).
health_condition(kusum_wijeratne, stage_5_ckd).
access_to_healthcare(kusum_wijeratne, yes).
family_structure(kusum_wijeratne, nuclear).
elderly_dependents(kusum_wijeratne, 2).

% New Knowledge Block
profession(kusum_wijeratne, factory_worker).
language_spoken(kusum_wijeratne, sinhala).
person(kusum_wijeratne).
gender(kusum_wijeratne, female).
age(kusum_wijeratne, 23).
communication_preference(kusum_wijeratne, sms).
marital_status(kusum_wijeratne, unmarried).
monthly_income(kusum_wijeratne, 18000).
location(kusum_wijeratne, kurunegala).
education(kusum_wijeratne, primary).
chronic_condition(kusum_wijeratne, yes).
health_condition(kusum_wijeratne, stage_5_ckd).
family_structure(kusum_wijeratne, nuclear).

% New Knowledge Block
communication_preference(kusum_wijeratne, sms).
age(kusum_wijeratne, 23).
profession(kusum_wijeratne, factory_worker).
monthly_income(kusum_wijeratne, 18000).
access_to_healthcare(kusum_wijeratne, yes).
chronic_condition(kusum_wijeratne, yes).
health_condition(kusum_wijeratne, stage_5_ckd).
language_spoken(kusum_wijeratne, sinhala).
education(kusum_wijeratne, primary).
location(kusum_wijeratne, kurunegala).
family_structure(kusum_wijeratne, nuclear).
gender(kusum_wijeratne, female).
person(kusum_wijeratne).
marital_status(kusum_wijeratne, unmarried).

% New Knowledge Block
chronic_condition(bharuka_wijeratne, yes).
person(bharuka_wijeratne).
communication_preference(bharuka_wijeratne, sms).
gender(bharuka_wijeratne, female).
location(bharuka_wijeratne, kurunegala).
language_spoken(bharuka_wijeratne, sinhala).
health_condition(bharuka_wijeratne, stage_5_ckd).
access_to_healthcare(bharuka_wijeratne, yes).
marital_status(bharuka_wijeratne, single).
monthly_income(bharuka_wijeratne, 18000).
education(bharuka_wijeratne, primary).
family_structure(bharuka_wijeratne, nuclear).
profession(bharuka_wijeratne, factory_worker).
age(bharuka_wijeratne, 23).

% New Knowledge Block
communication_preference(paruka_wijeratne, sms).
access_to_healthcare(paruka_wijeratne, yes).
monthly_income(paruka_wijeratne, 18000).
location(paruka_wijeratne, kurunegala).
health_condition(paruka_wijeratne, stage_5_ckd).
elderly_dependents(paruka_wijeratne, 2).
chronic_condition(paruka_wijeratne, yes).
gender(paruka_wijeratne, female).
marital_status(paruka_wijeratne, single).
education(paruka_wijeratne, primary).
family_structure(paruka_wijeratne, nuclear).
person(paruka_wijeratne).
profession(paruka_wijeratne, factory_worker).
age(paruka_wijeratne, 67).
language_spoken(paruka_wijeratne, sinhala).

% New Knowledge Block
age(hirusha_wijeratne, 67).
health_condition(hirusha_wijeratne, stage_5_ckd).
gender(hirusha_wijeratne, female).
access_to_healthcare(hirusha_wijeratne, yes).
language_spoken(hirusha_wijeratne, sinhala).
family_structure(hirusha_wijeratne, nuclear).
chronic_condition(hirusha_wijeratne, yes).
location(hirusha_wijeratne, kurunegala).
person(hirusha_wijeratne).
marital_status(hirusha_wijeratne, single).
education(hirusha_wijeratne, primary).
communication_preference(hirusha_wijeratne, sms).
monthly_income(hirusha_wijeratne, 18000).
profession(hirusha_wijeratne, factory_worker).
elderly_dependents(hirusha_wijeratne, 2).

% New Knowledge Block
elderly_dependents(bikini_wijeratne, 2).
age(bikini_wijeratne, 40).
person(bikini_wijeratne).
language_spoken(bikini_wijeratne, sinhala).
location(bikini_wijeratne, kurunegala).
health_condition(bikini_wijeratne, stage_5_ckd).
education(bikini_wijeratne, primary).
communication_preference(bikini_wijeratne, sms).
profession(bikini_wijeratne, factory_worker).
gender(bikini_wijeratne, female).
monthly_income(bikini_wijeratne, 18000).
marital_status(bikini_wijeratne, single).
access_to_healthcare(bikini_wijeratne, yes).
family_structure(bikini_wijeratne, nuclear).
chronic_condition(bikini_wijeratne, yes).

% New Knowledge Block
dependent_children(thushara_jayasinghe, 1).
person(thushara_jayasinghe).
gender(thushara_jayasinghe, male).
health_condition(thushara_jayasinghe, hypertension).
location(thushara_jayasinghe, negombo).
profession(thushara_jayasinghe, civil_engineer).
monthly_income(thushara_jayasinghe, 150000).
marital_status(thushara_jayasinghe, married).
health_condition(thushara_jayasinghe, stage_1_ckd).
education(thushara_jayasinghe, primary).
access_to_healthcare(thushara_jayasinghe, yes).
family_structure(thushara_jayasinghe, nuclear).
chronic_condition(thushara_jayasinghe, yes).
communication_preference(thushara_jayasinghe, phone).
language_spoken(thushara_jayasinghe, english).
age(thushara_jayasinghe, 50).
communication_preference(thushara_jayasinghe, email).

% New Knowledge Block
gender(kumari_seneviratne, female).
access_to_healthcare(kumari_seneviratne, no).
profession(kumari_seneviratne, vegetable_seller).
person(kumari_seneviratne).
family_structure(kumari_seneviratne, nuclear).
location(kumari_seneviratne, gampaha).
education(kumari_seneviratne, primary).
language_spoken(kumari_seneviratne, sinhala).
health_condition(kumari_seneviratne, stage_5_ckd).
chronic_condition(kumari_seneviratne, yes).
age(kumari_seneviratne, 55).
monthly_income(kumari_seneviratne, 14000).

% New Knowledge Block
monthly_income(gamini_samarasinghe, 18000).
education(gamini_samarasinghe, primary).
gender(gamini_samarasinghe, male).
chronic_condition(gamini_samarasinghe, yes).
family_structure(gamini_samarasinghe, nuclear).
language_spoken(gamini_samarasinghe, sinhala).
health_condition(gamini_samarasinghe, stage_4_ckd).
profession(gamini_samarasinghe, motor_mechanic).
location(gamini_samarasinghe, kandy).
age(gamini_samarasinghe, 46).
access_to_healthcare(gamini_samarasinghe, no).
person(gamini_samarasinghe).

% New Knowledge Block
language_spoken(suren_perera, sinhala).
profession(suren_perera, security_guard).
chronic_condition(suren_perera, yes).
health_condition(suren_perera, stage_4_ckd).
location(suren_perera, anuradhapura).
monthly_income(suren_perera, 14000).
person(suren_perera).
education(suren_perera, primary).
age(suren_perera, 41).
gender(suren_perera, male).
family_structure(suren_perera, nuclear).
access_to_healthcare(suren_perera, no).

% New Knowledge Block
language_spoken(suren_perera, sinhala).
profession(suren_perera, security_guard).
chronic_condition(suren_perera, yes).
communication_preference(suren_perera, phone).
health_condition(suren_perera, stage_4_ckd).
location(suren_perera, anuradhapura).
monthly_income(suren_perera, 14000).
person(suren_perera).
education(suren_perera, primary).
age(suren_perera, 41).
resides_in(suren_perera, anuradhapura).
gender(suren_perera, male).
family_structure(suren_perera, nuclear).
access_to_healthcare(suren_perera, no).
dependent_children(suren_perera, 2).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
fixed_income(ravindra_wijeratne, no).
commute_time(ravindra_wijeratne, 30).
elderly_dependents(ravindra_wijeratne, 2).
monthly_income(ravindra_wijeratne, 20000).
chronic_condition(ravindra_wijeratne, yes).
access_to_healthcare(ravindra_wijeratne, no).
children(ravindra_wijeratne, 0).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
age(ravindra_wijeratne, 45).
education(ravindra_wijeratne, primary).
gender(ravindra_wijeratne, male).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).

% New Knowledge Block
language_spoken(suren_perera, sinhala).
profession(suren_perera, security_guard).
chronic_condition(suren_perera, yes).
health_condition(suren_perera, stage_4_ckd).
monthly_income(suren_perera, 14000).
location(suren_perera, anuradhapura).
person(suren_perera).
education(suren_perera, primary).
age(suren_perera, 41).
gender(suren_perera, male).
family_structure(suren_perera, nuclear).
access_to_healthcare(suren_perera, no).
dependent_children(suren_perera, 2).

% New Knowledge Block
language_spoken(suren_perera, sinhala).
profession(suren_perera, security_guard).
chronic_condition(suren_perera, yes).
communication_preference(suren_perera, phone).
health_condition(suren_perera, stage_4_ckd).
location(suren_perera, anuradhapura).
monthly_income(suren_perera, 34000).
person(suren_perera).
education(suren_perera, primary).
age(suren_perera, 41).
gender(suren_perera, male).
family_structure(suren_perera, nuclear).
access_to_healthcare(suren_perera, no).
dependent_children(suren_perera, 2).

% New Knowledge Block
profession(suren_perera, security_guard).
language_spoken(suren_perera, sinhala).
chronic_condition(suren_perera, yes).
communication_preference(suren_perera, phone).
health_condition(suren_perera, stage_4_ckd).
location(suren_perera, anuradhapura).
person(suren_perera).
education(suren_perera, primary).
age(suren_perera, 41).
gender(suren_perera, male).
family_structure(suren_perera, nuclear).
access_to_healthcare(suren_perera, no).
monthly_income(suren_perera, 0).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
fixed_income(ravindra_wijeratne, no).
commute_time(ravindra_wijeratne, 30).
gender(ravindra_wijeratne, male).
elderly_dependents(ravindra_wijeratne, 2).
monthly_income(ravindra_wijeratne, 20000).
chronic_condition(ravindra_wijeratne, yes).
access_to_healthcare(ravindra_wijeratne, no).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
age(ravindra_wijeratne, 45).
education(ravindra_wijeratne, primary).
dependent_children(ravindra_wijeratne, 0).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
fixed_income(ravindra_wijeratne, no).
commute_time(ravindra_wijeratne, 30).
gender(ravindra_wijeratne, male).
elderly_dependents(ravindra_wijeratne, 2).
monthly_income(ravindra_wijeratne, 20000).
chronic_condition(ravindra_wijeratne, yes).
access_to_healthcare(ravindra_wijeratne, no).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
age(ravindra_wijeratne, 45).
education(ravindra_wijeratne, primary).
dependent_children(ravindra_wijeratne, 0).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).

% New Knowledge Block
income_level(anoma_karunaratne, high).
language_spoken(anoma_karunaratne, sinhala).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
access_to_healthcare(anoma_karunaratne, yes).
family_structure(anoma_karunaratne, nuclear).
person(anoma_karunaratne).
age(anoma_karunaratne, 52).
profession(anoma_karunaratne, school_principal).
health_condition(anoma_karunaratne, stage_2_ckd).
marital_status(anoma_karunaratne, married).
gender(anoma_karunaratne, female).
resides_in(anoma_karunaratne, urban).
communication_preference(anoma_karunaratne, email).
chronic_condition(anoma_karunaratne, yes).
location(anoma_karunaratne, kandy).

% New Knowledge Block
language_spoken(anoma_karunaratne, sinhala).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
access_to_healthcare(anoma_karunaratne, yes).
family_structure(anoma_karunaratne, nuclear).
person(anoma_karunaratne).
age(anoma_karunaratne, 52).
profession(anoma_karunaratne, school_principal).
marital_status(anoma_karunaratne, married).
health_condition(anoma_karunaratne, stage_2_ckd).
gender(anoma_karunaratne, female).
resides_in(anoma_karunaratne, urban).
communication_preference(anoma_karunaratne, email).
chronic_condition(anoma_karunaratne, yes).
location(anoma_karunaratne, kandy).

% New Knowledge Block
disability(anoma_karunaratne, no).
language_spoken(anoma_karunaratne, sinhala).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
access_to_healthcare(anoma_karunaratne, yes).
family_structure(anoma_karunaratne, nuclear).
person(anoma_karunaratne).
age(anoma_karunaratne, 52).
profession(anoma_karunaratne, school_principal).
marital_status(anoma_karunaratne, married).
communication_preference(anoma_karunaratne, email).
gender(anoma_karunaratne, female).
health_condition(anoma_karunaratne, stage_2_ckd).
chronic_condition(anoma_karunaratne, yes).
children(anoma_karunaratne, 0).
location(anoma_karunaratne, kandy).

% New Knowledge Block
profession(anoma_karunaratne, businesswoman).
language_spoken(anoma_karunaratne, sinhala).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
access_to_healthcare(anoma_karunaratne, yes).
family_structure(anoma_karunaratne, nuclear).
person(anoma_karunaratne).
age(anoma_karunaratne, 52).
communication_preference(anoma_karunaratne, email).
health_condition(anoma_karunaratne, stage_2_ckd).
marital_status(anoma_karunaratne, married).
gender(anoma_karunaratne, female).
chronic_condition(anoma_karunaratne, yes).
children(anoma_karunaratne, 0).
location(anoma_karunaratne, kandy).

% New Knowledge Block
profession(anoma_karunaratne, businesswoman).
income_level(anoma_karunaratne, high).
language_spoken(anoma_karunaratne, sinhala).
education(anoma_karunaratne, primary).
monthly_income(anoma_karunaratne, 120000).
access_to_healthcare(anoma_karunaratne, yes).
family_structure(anoma_karunaratne, nuclear).
person(anoma_karunaratne).
age(anoma_karunaratne, 52).
communication_preference(anoma_karunaratne, email).
health_condition(anoma_karunaratne, stage_2_ckd).
marital_status(anoma_karunaratne, married).
gender(anoma_karunaratne, female).
chronic_condition(anoma_karunaratne, yes).
location(anoma_karunaratne, kandy).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
commute_time(ravindra_wijeratne, 30).
fixed_income(ravindra_wijeratne, no).
elderly_dependents(ravindra_wijeratne, 2).
chronic_condition(ravindra_wijeratne, yes).
access_to_healthcare(ravindra_wijeratne, no).
children(ravindra_wijeratne, 0).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
education(ravindra_wijeratne, primary).
age(ravindra_wijeratne, 45).
monthly_income(ravindra_wijeratne, 25000).
gender(ravindra_wijeratne, male).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).

% New Knowledge Block
health_condition(saman_bandula, stage_5_ckd).
access_to_healthcare(saman_bandula, no).
gender(saman_bandula, male).
chronic_condition(saman_bandula, yes).
communication_preference(saman_bandula, phone).
profession(saman_bandula, farmer).
age(saman_bandula, 48).
marital_status(saman_bandula, married).
education(saman_bandula, primary).
person(saman_bandula).
debt_status(saman_bandula, yes).
monthly_income(saman_bandula, 14000).
family_structure(saman_bandula, nuclear).
language_spoken(saman_bandula, sinhala).

% New Knowledge Block
fixed_income(saman_bandula, no).
health_condition(saman_bandula, stage_5_ckd).
access_to_healthcare(saman_bandula, no).
gender(saman_bandula, male).
chronic_condition(saman_bandula, yes).
communication_preference(saman_bandula, phone).
profession(saman_bandula, farmer).
age(saman_bandula, 48).
resides_in(saman_bandula, rural).
marital_status(saman_bandula, married).
education(saman_bandula, primary).
person(saman_bandula).
debt_status(saman_bandula, yes).
location(saman_bandula, monaragala).
monthly_income(saman_bandula, 14000).
family_structure(saman_bandula, nuclear).
language_spoken(saman_bandula, sinhala).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
fixed_income(ravindra_wijeratne, no).
gender(ravindra_wijeratne, male).
elderly_dependents(ravindra_wijeratne, 2).
chronic_condition(ravindra_wijeratne, yes).
monthly_income(ravindra_wijeratne, 0).
access_to_healthcare(ravindra_wijeratne, no).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
age(ravindra_wijeratne, 45).
education(ravindra_wijeratne, primary).
dependent_children(ravindra_wijeratne, 0).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).

% New Knowledge Block
language_spoken(ravindra_wijeratne, sinhala).
location(ravindra_wijeratne, ratnapura).
commute_time(ravindra_wijeratne, 30).
fixed_income(ravindra_wijeratne, no).
debt_status(ravindra_wijeratne, yes).
gender(ravindra_wijeratne, male).
elderly_dependents(ravindra_wijeratne, 2).
chronic_condition(ravindra_wijeratne, yes).
monthly_income(ravindra_wijeratne, 0).
access_to_healthcare(ravindra_wijeratne, no).
family_structure(ravindra_wijeratne, nuclear).
person(ravindra_wijeratne).
education(ravindra_wijeratne, primary).
age(ravindra_wijeratne, 45).
monthly_income(ravindra_wijeratne, 25000).
dependent_children(ravindra_wijeratne, 0).
health_condition(ravindra_wijeratne, stage_5_ckd).
profession(ravindra_wijeratne, farmer).
