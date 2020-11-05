''' In this case study we use the classes provided in risk_model.py to define a set of LOPP-scenarios
    and power restoration scenarios for a mahinery system that can be operated in three different
    modes.

    The purpose in the case study is to determine the probability of grounding during the next hour
    of sailing in a sailing situation where it would take the ship 60 seconds to ground given loss
    of propulsion power anywhere along the route for the next hour (assume that the ship is sailing
    with constant distance from a straight shore line in constant wind and current conditions).
'''

import risk_model

# Triggering events
main_engine_stops = risk_model.TriggeringEvent(rate_of_occurrence=8e-9, time_interval=3600)
genset_one_stops = risk_model.TriggeringEvent(rate_of_occurrence=14e-9, time_interval=3600)
genset_two_stops = risk_model.TriggeringEvent(rate_of_occurrence=14e-9, time_interval=3600)
shaft_gen_stops = risk_model.TriggeringEvent(rate_of_occurrence=6e-9, time_interval=3600)

# LOPP-scenairos
loss_of_main_engine = risk_model.LossOfPropulsionScenario([main_engine_stops])
loss_of_both_gensets = risk_model.LossOfPropulsionScenario([genset_one_stops, genset_two_stops])
loss_of_shaft_gen = risk_model.LossOfPropulsionScenario([shaft_gen_stops])

# Power restoration startup events
start_main_engine_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=40,
    standard_deviation_time_to_restart=1.2,
    time_shift_time_to_restart=20,
    nominal_success_probability=1
)
start_main_engine = risk_model.StartUpEvent(parameters=start_main_engine_params, time_available=60)

restart_main_engine_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=40,
    standard_deviation_time_to_restart=1.2,
    time_shift_time_to_restart=20,
    nominal_success_probability=0.4
)
restart_main_engine = risk_model.StartUpEvent(parameters=restart_main_engine_params, time_available=60)

start_genset_one_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=30,
    standard_deviation_time_to_restart=1.0,
    time_shift_time_to_restart=13,
    nominal_success_probability=1
)
start_genset_one = risk_model.StartUpEvent(parameters=start_genset_one_params, time_available=60)
start_genset_two = risk_model.StartUpEvent(parameters=start_genset_one_params, time_available=60)

restart_genset_one_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=30,
    standard_deviation_time_to_restart=1.0,
    time_shift_time_to_restart=13,
    nominal_success_probability=0.4
)
restart_genset_one = risk_model.StartUpEvent(parameters=restart_genset_one_params, time_available=60)
restart_genset_two = risk_model.StartUpEvent(parameters=restart_genset_one_params, time_available=60)

start_hsg_as_motor_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=8,
    standard_deviation_time_to_restart=1,
    time_shift_time_to_restart=3,
    nominal_success_probability=1
)
start_hsg_as_motor = risk_model.StartUpEvent(parameters=start_hsg_as_motor_params, time_available=60)

restart_hsg_as_motor_params = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=8,
    standard_deviation_time_to_restart=1,
    time_shift_time_to_restart=3,
    nominal_success_probability=0.8
)
restart_hsg_as_motor = risk_model.StartUpEvent(parameters=restart_hsg_as_motor_params, time_available=60)

# Power restoration sequences
propulsion_power_by_starting_main_engine = risk_model.StartupEventSequence(
    list_of_startup_events=[start_main_engine]
)
propulsion_power_by_restarting_main_engine = risk_model.StartupEventSequence(
    list_of_startup_events=[restart_main_engine]
)
propulsion_power_by_starting_genset_one_and_hsg = risk_model.StartupEventSequence(
    list_of_startup_events=[start_genset_one, start_hsg_as_motor]
)
propulsion_power_by_starting_genset_two_and_hsg = risk_model.StartupEventSequence(
    list_of_startup_events=[start_genset_two, start_hsg_as_motor]
)
propulsion_power_by_restarting_genset_one = risk_model.StartupEventSequence(
    list_of_startup_events=[restart_genset_one]
)
propulsion_power_by_restarting_genset_two = risk_model.StartupEventSequence(
    list_of_startup_events=[restart_genset_two]
)
propulsion_power_by_starting_hsg_as_motor = risk_model.StartupEventSequence(
    list_of_startup_events=[start_hsg_as_motor]
)
propulsion_power_by_restarting_hsg_as_motor = risk_model.StartupEventSequence(
    list_of_startup_events=[restart_hsg_as_motor]
)

# Power restoration event trees
restore_from_loss_of_main_engine_in_pto = risk_model.PowerRestorationEventTree(
    startup_event_sequences=[
        propulsion_power_by_restarting_main_engine,
        propulsion_power_by_starting_genset_one_and_hsg,
        propulsion_power_by_starting_genset_two_and_hsg
    ]
)
restore_from_loss_of_main_engine_in_mec = risk_model.PowerRestorationEventTree(
    startup_event_sequences=[
        propulsion_power_by_restarting_main_engine,
        propulsion_power_by_starting_hsg_as_motor,
        propulsion_power_by_starting_genset_two_and_hsg
    ]
)
restore_from_loss_of_both_gensets_in_pti = risk_model.PowerRestorationEventTree(
    startup_event_sequences=[
        propulsion_power_by_starting_main_engine,
        propulsion_power_by_restarting_genset_one,
        propulsion_power_by_restarting_genset_two
    ]
)
restore_from_loss_of_hsg_in_pti = risk_model.PowerRestorationEventTree(
    startup_event_sequences=[
        propulsion_power_by_restarting_hsg_as_motor
    ]
)

# Construct complete scenarios
loss_of_main_engine_in_pto = risk_model.Scenario(
    loss_scenario=loss_of_main_engine,
    restoration_scenario=restore_from_loss_of_main_engine_in_pto
)
loss_of_main_engine_in_mec = risk_model.Scenario(
    loss_scenario=loss_of_main_engine,
    restoration_scenario=restore_from_loss_of_main_engine_in_mec
)
loss_of_both_gensets_in_pti = risk_model.Scenario(
    loss_scenario=loss_of_both_gensets,
    restoration_scenario=restore_from_loss_of_both_gensets_in_pti
)
loss_of_hsg_in_pti = risk_model.Scenario(
    loss_scenario=loss_of_shaft_gen,
    restoration_scenario=restore_from_loss_of_hsg_in_pti
)

# Construct mode cases
pto_mode = risk_model.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_pto])
mec_mode = risk_model.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_mec])
pti_mode = risk_model.MachinerySystemOperatingMode(possible_scenarios=[loss_of_both_gensets_in_pti,
                                                                       loss_of_hsg_in_pti])

print('Prob of grounding if PTO is selected: ' + str(pto_mode.probability_of_grounding))
print('Prob of grounding if MEC is selected: ' + str(mec_mode.probability_of_grounding))
print('Prob of grounding if PTI is selected: ' + str(pti_mode.probability_of_grounding))