% Program eligibility rules

% Rule for "Suwa" CKD Aid Program
eligible_for_suwa_ckd_aid(Person) :-
    person(Person),
    age(Person, Age), Age > 40,
    health_condition(Person, HealthCondition),
    (HealthCondition = stage_4_ckd ; HealthCondition = stage_5_ckd),
    monthly_income(Person, Income), Income < 25000.

% Rule for "Diriya" Single Parent Support Program
eligible_for_diriya_support(Person) :-
    person(Person),
    marital_status(Person, single),
    dependent_children(Person, DependentChildren), DependentChildren > 0,
    monthly_income(Person, Income), Income < 20000.

% Rule for "Thurunu Piyasa" Rural Education Aid Program
eligible_for_thurunu_piyasa(Person) :-
    person(Person),
    location(Person, Location), rural_area(Location),
    education(Person, primary),
    monthly_income(Person, Income), Income < 15000.

% Rule for "Sahana" Rural Education Aid Program
eligible_for_sahana_healthcare(Person) :-
    person(Person),
    chronic_condition(Person, yes),
    access_to_healthcare(Person, no),
    monthly_income(Person, Income), Income < 20000.

eligible_for_divisaviya_income_support(Person) :-
    person(Person),
    monthly_income(Person, Income), Income < 15000,
    family_structure(Person, nuclear).

eligible_for_nirmala_empowerment(Person) :-
    person(Person),
    gender(Person, female),
    marital_status(Person, single),
    monthly_income(Person, Income), Income < 18000.

eligible_for_daruwan_suraksha(Person) :-
    person(Person),
    children(Person, Children), Children > 0,
    dependent_children(Person, DependentChildren), DependentChildren > 0,
    monthly_income(Person, Income), Income < 20000.

eligible_for_govi_jana_support(Person) :-
    person(Person),
    profession(Person, part_time_tea_plucker),
    location(Person, Location), rural_area(Location),
    monthly_income(Person, Income), Income < 18000.

eligible_for_arogya_elderly_care(Person) :-
    person(Person),
    age(Person, Age), Age > 60,
    monthly_income(Person, Income), Income < 20000.

eligible_programs(Person, Programs) :-
    findall(Program, eligible_for_program(Person, Program), Programs).

eligible_for_program(Person, suwa_ckd_aid) :-
    eligible_for_suwa_ckd_aid(Person).

eligible_for_program(Person, diriya_support) :-
    eligible_for_diriya_support(Person).

eligible_for_program(Person, thurunu_piyasa) :-
    eligible_for_thurunu_piyasa(Person).

eligible_for_program(Person, sahana_healthcare) :-
    eligible_for_sahana_healthcare(Person).

eligible_for_program(Person, divisaviya_income_support) :-
    eligible_for_divisaviya_income_support(Person).

eligible_for_program(Person, nirmala_empowerment) :-
    eligible_for_nirmala_empowerment(Person).

eligible_for_program(Person, daruwan_suraksha) :-
    eligible_for_daruwan_suraksha(Person).

eligible_for_program(Person, govi_jana_support) :-
    eligible_for_govi_jana_support(Person).

eligible_for_program(Person, arogya_elderly_care) :-
    eligible_for_arogya_elderly_care(Person).


%output Programs = [suwa_ckd_aid, diriya_support].

% Rural areas in Sri Lanka
rural_area(monaragala).
rural_area(badulla).
rural_area(mahiyanganaya).
rural_area(rathnapura).
rural_area(hambantota).
rural_area(amupara).
rural_area(batticaloa).
rural_area(mullaitivu).
rural_area(vavuniya).
rural_area(kilinochchi).
rural_area(polonnaruwa).
rural_area(anuradhapura).
rural_area(nuwara_eliya).
rural_area(medawachchiya).
rural_area(tissamaharama).
rural_area(kataragama).
rural_area(mahavilachchiya).
rural_area(galgamuwa).
rural_area(agalawatta).
rural_area(dehiattakandiya).
rural_area(laggala).
rural_area(haldummulla).
rural_area(haputale).
rural_area(kandaketiya).
rural_area(padiyatalawa).
rural_area(horana).
rural_area(dolakanda).
rural_area(yala).
rural_area(gonagala).
rural_area(minneriya).
rural_area(sigiriya).
rural_area(higurakgoda).
rural_area(dambulla).
rural_area(welimada).
rural_area(maskeliya).
rural_area(labugama).
rural_area(kolonna).
rural_area(balangoda).
rural_area(pelmadulla).
rural_area(suriyawewa).
rural_area(embilipitiya).
rural_area(udawalawa).
rural_area(wanduramba).
rural_area(pitigala).
rural_area(deniyaya).
rural_area(morawaka).
rural_area(mirissa).
rural_area(weligama).
rural_area(kotapola).
rural_area(neluwa).
rural_area(lankagama).
rural_area(udugama).
rural_area(nagoda).
rural_area(galle_hapugala).
rural_area(sooriyakanda).
rural_area(passara).
rural_area(bibile).
rural_area(gomarankadawala).
rural_area(kantale).
rural_area(thambalagamuwa).
rural_area(kaduruwela).
rural_area(aluthwewa).
rural_area(warakapola).
rural_area(mawanella).
rural_area(dedigama).
rural_area(horowupotana).
rural_area(puttalam).
rural_area(madampe).
rural_area(chilaw).
rural_area(kuliyapitiya).
rural_area(balangoda).
rural_area(hatton).
rural_area(dickoya).
rural_area(kotagala).
rural_area(hegoda).
rural_area(lunugamvehera).
rural_area(ambalantota).
rural_area(buttala).
rural_area(wellawaya).
rural_area(ginigathena).
rural_area(mahaweli_ganga).
rural_area(wilpattu).

