import scenarios
from typing import NamedTuple
import matplotlib.pyplot as plt


class CaseStudySystemSetupOutput(NamedTuple):
    pto_mode_scenarios: scenarios.MachinerySystemOperatingMode
    mec_mode_scenarios: scenarios.MachinerySystemOperatingMode
    pti_mode_scenarios: scenarios.MachinerySystemOperatingMode


class CaseStudySystemParameters(NamedTuple):
    main_engine_failure_rate: float
    main_engine_mean_start_time: float
    main_engine_start_time_std: float
    main_engine_start_time_shift: float
    main_engine_nominal_start_prob: float
    main_engine_mean_restart_time: float
    main_engine_restart_time_std: float
    main_engine_restart_time_shift: float
    main_engine_nominal_restart_prob: float
    genset_one_failure_rate: float
    genset_one_mean_start_time: float
    genset_one_start_time_std: float
    genset_one_start_time_shift: float
    genset_one_nominal_start_prob: float
    genset_one_mean_restart_time: float
    genset_one_restart_time_std: float
    genset_one_restart_time_shift: float
    genset_one_nominal_restart_prob: float
    genset_two_failure_rate: float
    genset_two_mean_start_time: float
    genset_two_start_time_std: float
    genset_two_start_time_shift: float
    genset_two_nominal_start_prob: float
    genset_two_mean_restart_time: float
    genset_two_restart_time_std: float
    genset_two_restart_time_shift: float
    genset_two_nominal_restart_prob: float
    hsg_failure_rate: float
    hsg_mean_start_time: float
    hsg_start_time_std: float
    hsg_start_time_shift: float
    hsg_nominal_start_prob: float
    hsg_mean_restart_time: float
    hsg_restart_time_std: float
    hsg_restart_time_shift: float
    hsg_nominal_restart_prob: float


def case_study_system_setup(system_params: CaseStudySystemParameters,
                            time_interval=60,
                            available_time=60):
    main_engine_stops = scenarios.TriggeringEvent(rate_of_occurrence=system_params.main_engine_failure_rate,
                                                  time_interval=time_interval)
    genset_one_stops = scenarios.TriggeringEvent(rate_of_occurrence=system_params.genset_one_failure_rate,
                                                 time_interval=time_interval)
    genset_two_stops = scenarios.TriggeringEvent(rate_of_occurrence=system_params.genset_two_failure_rate,
                                                 time_interval=time_interval)
    shaft_gen_stops = scenarios.TriggeringEvent(rate_of_occurrence=system_params.hsg_failure_rate,
                                                time_interval=time_interval)

    loss_of_main_engine = scenarios.LossOfPropulsionScenario([main_engine_stops])
    loss_of_both_gensets = scenarios.LossOfPropulsionScenario([genset_one_stops, genset_two_stops])
    loss_of_shaft_gen = scenarios.LossOfPropulsionScenario([shaft_gen_stops])

    start_main_engine_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.main_engine_mean_start_time,
        standard_deviation_time_to_restart=system_params.main_engine_start_time_std,
        time_shift_time_to_restart=system_params.main_engine_start_time_shift,
        nominal_success_probability=system_params.main_engine_nominal_start_prob
    )
    start_main_engine = scenarios.StartUpEvent(parameters=start_main_engine_params,
                                               time_available=available_time)
    restart_main_engine_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.main_engine_mean_restart_time,
        standard_deviation_time_to_restart=system_params.main_engine_restart_time_std,
        time_shift_time_to_restart=system_params.main_engine_restart_time_shift,
        nominal_success_probability=system_params.main_engine_nominal_restart_prob
    )
    restart_main_engine = scenarios.StartUpEvent(parameters=restart_main_engine_params,
                                                 time_available=available_time)
    start_genset_one_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.genset_one_mean_start_time,
        standard_deviation_time_to_restart=system_params.genset_one_start_time_std,
        time_shift_time_to_restart=system_params.genset_one_start_time_shift,
        nominal_success_probability=system_params.genset_one_nominal_start_prob
    )
    start_genset_one = scenarios.StartUpEvent(parameters=start_genset_one_params,
                                              time_available=available_time)
    start_genset_two_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.genset_two_mean_start_time,
        standard_deviation_time_to_restart=system_params.genset_two_start_time_std,
        time_shift_time_to_restart=system_params.genset_two_start_time_shift,
        nominal_success_probability=system_params.genset_two_nominal_start_prob
    )
    start_genset_two = scenarios.StartUpEvent(parameters=start_genset_two_params,
                                              time_available=available_time)

    restart_genset_one_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.genset_one_mean_restart_time,
        standard_deviation_time_to_restart=system_params.genset_one_restart_time_std,
        time_shift_time_to_restart=system_params.genset_one_restart_time_shift,
        nominal_success_probability=system_params.genset_one_nominal_restart_prob
    )
    restart_genset_one = scenarios.StartUpEvent(parameters=restart_genset_one_params,
                                                time_available=available_time)
    restart_genset_two_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.genset_two_mean_restart_time,
        standard_deviation_time_to_restart=system_params.genset_two_restart_time_std,
        time_shift_time_to_restart=system_params.genset_two_restart_time_shift,
        nominal_success_probability=system_params.genset_two_nominal_restart_prob
    )
    restart_genset_two = scenarios.StartUpEvent(parameters=restart_genset_two_params,
                                                time_available=available_time)

    start_hsg_as_motor_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.hsg_mean_start_time,
        standard_deviation_time_to_restart=system_params.hsg_start_time_std,
        time_shift_time_to_restart=system_params.hsg_start_time_shift,
        nominal_success_probability=system_params.hsg_nominal_start_prob
    )
    start_hsg_as_motor = scenarios.StartUpEvent(parameters=start_hsg_as_motor_params,
                                                time_available=available_time)

    restart_hsg_as_motor_params = scenarios.StartUpEventParameters(
        mean_time_to_restart_s=system_params.hsg_mean_restart_time,
        standard_deviation_time_to_restart=system_params.hsg_restart_time_std,
        time_shift_time_to_restart=system_params.hsg_restart_time_shift,
        nominal_success_probability=system_params.hsg_nominal_restart_prob
    )
    restart_hsg_as_motor = scenarios.StartUpEvent(parameters=restart_hsg_as_motor_params,
                                                  time_available=available_time)

    propulsion_power_by_starting_main_engine = scenarios.StartupEventSequence(
        list_of_startup_events=[start_main_engine]
    )
    propulsion_power_by_restarting_main_engine = scenarios.StartupEventSequence(
        list_of_startup_events=[restart_main_engine]
    )
    propulsion_power_by_starting_genset_one_and_hsg = scenarios.StartupEventSequence(
        list_of_startup_events=[start_genset_one, start_hsg_as_motor]
    )
    propulsion_power_by_starting_genset_two_and_hsg = scenarios.StartupEventSequence(
        list_of_startup_events=[start_genset_two, start_hsg_as_motor]
    )
    propulsion_power_by_restarting_genset_one = scenarios.StartupEventSequence(
        list_of_startup_events=[restart_genset_one]
    )
    propulsion_power_by_restarting_genset_two = scenarios.StartupEventSequence(
        list_of_startup_events=[restart_genset_two]
    )
    propulsion_power_by_starting_hsg_as_motor = scenarios.StartupEventSequence(
        list_of_startup_events=[start_hsg_as_motor]
    )
    propulsion_power_by_restarting_hsg_as_motor = scenarios.StartupEventSequence(
        list_of_startup_events=[restart_hsg_as_motor]
    )

    restore_from_loss_of_main_engine_in_pto = scenarios.PowerRestorationEventTree(
        startup_event_sequences=[
            propulsion_power_by_restarting_main_engine,
            propulsion_power_by_starting_genset_one_and_hsg,
            propulsion_power_by_starting_genset_two_and_hsg
        ]
    )
    restore_from_loss_of_main_engine_in_mec = scenarios.PowerRestorationEventTree(
        startup_event_sequences=[
            propulsion_power_by_restarting_main_engine,
            propulsion_power_by_starting_hsg_as_motor,
            propulsion_power_by_starting_genset_two_and_hsg
        ]
    )
    restore_from_loss_of_both_gensets_in_pti = scenarios.PowerRestorationEventTree(
        startup_event_sequences=[
            propulsion_power_by_starting_main_engine,
            propulsion_power_by_restarting_genset_one,
            propulsion_power_by_restarting_genset_two
        ]
    )
    restore_from_loss_of_hsg_in_pti = scenarios.PowerRestorationEventTree(
        startup_event_sequences=[
            propulsion_power_by_restarting_hsg_as_motor
        ]
    )

    loss_of_main_engine_in_pto = scenarios.Scenario(
        loss_scenario=loss_of_main_engine,
        restoration_scenario=restore_from_loss_of_main_engine_in_pto
    )
    loss_of_main_engine_in_mec = scenarios.Scenario(
        loss_scenario=loss_of_main_engine,
        restoration_scenario=restore_from_loss_of_main_engine_in_mec
    )
    loss_of_both_gensets_in_pti = scenarios.Scenario(
        loss_scenario=loss_of_both_gensets,
        restoration_scenario=restore_from_loss_of_both_gensets_in_pti
    )
    loss_of_hsg_in_pti = scenarios.Scenario(
        loss_scenario=loss_of_shaft_gen,
        restoration_scenario=restore_from_loss_of_hsg_in_pti
    )

    pto_mode = scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_pto])
    mec_mode = scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_mec])
    pti_mode = scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_both_gensets_in_pti,
                                                                          loss_of_hsg_in_pti])
    return CaseStudySystemSetupOutput(
        pto_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_pto]),
        mec_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_mec]),
        pti_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_both_gensets_in_pti,
                                                                                      loss_of_hsg_in_pti])
    )