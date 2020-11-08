"""
    Provides classes to estimate drifting grounding risk either for a small time interval or a
    prediction horizon (a set of adjoining small time intervals.
"""

from typing import NamedTuple, List

import scenarios
from ship_in_transit_simulator.models import DriftSimulationConfiguration, \
    EnvironmentConfiguration, ShipModelWithoutPropulsion, ShipConfiguration


class ENC:  # Temporary class (placeholder for real ENC-class)
    def __init__(self):
        self.x = 200


class MotionStateInput(NamedTuple):
    north_position: float
    east_position: float
    yaw_angle_rad: float
    surge_speed: float
    sway_speed: float
    yaw_rate: float


class RiskModelConfiguration(NamedTuple):
    max_drift_time_s: float
    risk_time_interval: float


class ScenarioAnalysisParameters(NamedTuple):
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


class ScenarioProbabilitiesOutput(NamedTuple):
    pto_mode_scenarios: scenarios.MachinerySystemOperatingMode
    mec_mode_scenarios: scenarios.MachinerySystemOperatingMode
    pti_mode_scenarios: scenarios.MachinerySystemOperatingMode


class RiskModelOutput(NamedTuple):
    probability_of_grounding_in_pto: float
    probability_of_grounding_in_mec: float
    probability_of_grounding_in_pti: float
    consequence_of_grounding: float


class GroundingRiskModel:
    def __init__(self, risk_model_config: RiskModelConfiguration,
                 ttg_sim_config: ShipConfiguration,
                 sim_config: DriftSimulationConfiguration,
                 env_config: EnvironmentConfiguration,
                 environment: ENC,
                 scenario_params: ScenarioAnalysisParameters):
        self.max_simulation_time = risk_model_config.max_drift_time_s
        self.risk_time_interval = risk_model_config.risk_time_interval
        self.ship_config = ttg_sim_config
        self.sim_config = sim_config
        self.env_config = env_config
        self.environment = environment
        self.scenario_params = scenario_params
        self.initial_states = MotionStateInput(sim_config.initial_north_position_m,
                                               sim_config.initial_east_position_m,
                                               sim_config.initial_yaw_angle_rad,
                                               sim_config.initial_forward_speed_m_per_s,
                                               sim_config.initial_sideways_speed_m_per_s,
                                               sim_config.initial_yaw_rate_rad_per_s)

        self.ttg_simulator = TimeToGroundingSimulator(max_simulation_time=self.max_simulation_time,
                                                      ship_config=self.ship_config,
                                                      simulation_config=self.sim_config,
                                                      environment_config=self.env_config,
                                                      environment=self.environment,
                                                      initial_states=self.initial_states)
        self.risk_model_output = self.calculate_risk_output()

    def calculate_risk_output(self):
        time_to_grounding, consequence_of_grounding = self.ttg_simulator.time_to_grounding()
        scenario_analysis_output = self.scenario_analysis(available_recovery_time=time_to_grounding)
        return RiskModelOutput(
            probability_of_grounding_in_pto=scenario_analysis_output.pto_mode_scenarios.probability_of_grounding,
            probability_of_grounding_in_mec=scenario_analysis_output.mec_mode_scenarios.probability_of_grounding,
            probability_of_grounding_in_pti=scenario_analysis_output.pti_mode_scenarios.probability_of_grounding,
            consequence_of_grounding=consequence_of_grounding
        )

    def scenario_analysis(self, available_recovery_time: float):
        main_engine_stops = scenarios.TriggeringEvent(rate_of_occurrence=self.scenario_params.main_engine_failure_rate,
                                                      time_interval=self.risk_time_interval)
        genset_one_stops = scenarios.TriggeringEvent(rate_of_occurrence=self.scenario_params.genset_one_failure_rate,
                                                     time_interval=self.risk_time_interval)
        genset_two_stops = scenarios.TriggeringEvent(rate_of_occurrence=self.scenario_params.genset_two_failure_rate,
                                                     time_interval=self.risk_time_interval)
        shaft_gen_stops = scenarios.TriggeringEvent(rate_of_occurrence=self.scenario_params.hsg_failure_rate,
                                                    time_interval=self.risk_time_interval)

        loss_of_main_engine = scenarios.LossOfPropulsionScenario([main_engine_stops])
        loss_of_both_gensets = scenarios.LossOfPropulsionScenario([genset_one_stops, genset_two_stops])
        loss_of_shaft_gen = scenarios.LossOfPropulsionScenario([shaft_gen_stops])

        start_main_engine_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.main_engine_mean_start_time,
            standard_deviation_time_to_restart=self.scenario_params.main_engine_start_time_std,
            time_shift_time_to_restart=self.scenario_params.main_engine_start_time_shift,
            nominal_success_probability=self.scenario_params.main_engine_nominal_start_prob
        )
        start_main_engine = scenarios.StartUpEvent(parameters=start_main_engine_params,
                                                   time_available=available_recovery_time)
        restart_main_engine_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.main_engine_mean_restart_time,
            standard_deviation_time_to_restart=self.scenario_params.main_engine_restart_time_std,
            time_shift_time_to_restart=self.scenario_params.main_engine_restart_time_shift,
            nominal_success_probability=self.scenario_params.main_engine_nominal_restart_prob
        )
        restart_main_engine = scenarios.StartUpEvent(parameters=restart_main_engine_params,
                                                     time_available=available_recovery_time)
        start_genset_one_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.genset_one_mean_start_time,
            standard_deviation_time_to_restart=self.scenario_params.genset_one_start_time_std,
            time_shift_time_to_restart=self.scenario_params.genset_one_start_time_shift,
            nominal_success_probability=self.scenario_params.genset_one_nominal_start_prob
        )
        start_genset_one = scenarios.StartUpEvent(parameters=start_genset_one_params,
                                                  time_available=available_recovery_time)
        start_genset_two_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.genset_two_mean_start_time,
            standard_deviation_time_to_restart=self.scenario_params.genset_two_start_time_std,
            time_shift_time_to_restart=self.scenario_params.genset_two_start_time_shift,
            nominal_success_probability=self.scenario_params.genset_two_nominal_start_prob
        )
        start_genset_two = scenarios.StartUpEvent(parameters=start_genset_two_params,
                                                  time_available=available_recovery_time)

        restart_genset_one_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.genset_one_mean_restart_time,
            standard_deviation_time_to_restart=self.scenario_params.genset_one_restart_time_std,
            time_shift_time_to_restart=self.scenario_params.genset_one_restart_time_shift,
            nominal_success_probability=self.scenario_params.genset_one_nominal_restart_prob
        )
        restart_genset_one = scenarios.StartUpEvent(parameters=restart_genset_one_params,
                                                    time_available=available_recovery_time)
        restart_genset_two_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.genset_two_mean_restart_time,
            standard_deviation_time_to_restart=self.scenario_params.genset_two_restart_time_std,
            time_shift_time_to_restart=self.scenario_params.genset_two_restart_time_shift,
            nominal_success_probability=self.scenario_params.genset_two_nominal_restart_prob
        )
        restart_genset_two = scenarios.StartUpEvent(parameters=restart_genset_two_params,
                                                    time_available=available_recovery_time)

        start_hsg_as_motor_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.hsg_mean_start_time,
            standard_deviation_time_to_restart=self.scenario_params.hsg_start_time_std,
            time_shift_time_to_restart=self.scenario_params.hsg_start_time_shift,
            nominal_success_probability=self.scenario_params.hsg_nominal_start_prob
        )
        start_hsg_as_motor = scenarios.StartUpEvent(parameters=start_hsg_as_motor_params,
                                                    time_available=available_recovery_time)

        restart_hsg_as_motor_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.hsg_mean_restart_time,
            standard_deviation_time_to_restart=self.scenario_params.hsg_restart_time_std,
            time_shift_time_to_restart=self.scenario_params.hsg_restart_time_shift,
            nominal_success_probability=self.scenario_params.hsg_nominal_restart_prob
        )
        restart_hsg_as_motor = scenarios.StartUpEvent(parameters=restart_hsg_as_motor_params,
                                                      time_available=available_recovery_time)

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
        return ScenarioProbabilitiesOutput(
            pto_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_pto]),
            mec_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_main_engine_in_mec]),
            pti_mode_scenarios=scenarios.MachinerySystemOperatingMode(possible_scenarios=[loss_of_both_gensets_in_pti,
                                                                                          loss_of_hsg_in_pti])
        )


class TimeToGroundingSimulator:
    ''' Simulate a ship drifting from given initial states until a grounding occurs
        or the maximum simulation time has elapsed.
    '''

    def __init__(self, initial_states: MotionStateInput,
                 environment: ENC,
                 max_simulation_time: float,
                 ship_config: ShipConfiguration,
                 simulation_config: DriftSimulationConfiguration,
                 environment_config: EnvironmentConfiguration):
        ''' Set up simulation.

            args:
            - initial_states (MotionStateInput): See MotionStateInput-class
            - max_simulation_time (float): Number of seconds after which to terminate simulation if
            grounding has not occurred.
        '''
        self.initial_states = initial_states
        self.max_sim_time = max_simulation_time
        self.environment = environment
        self.ship_config = ship_config
        self.simulation_config = simulation_config
        self.environment_config = environment_config
        self.ship_model = ShipModelWithoutPropulsion(ship_config=self.ship_config,
                                                     environment_config=self.environment_config,
                                                     simulation_config=self.simulation_config)

    def time_to_grounding(self):
        ''' Find the time it will take to ground and the magnitude of the consequence
            of grounding based on the speed of impact and the character of the shore
            (whether or not the ship hits infrastructure such as fish-farms. If the
            simulation is terminated before grounding occurs, the consequence of grounding
            is calculated based on the speed of the ship when the simulation is terminated
            and the cheapest shore character.

            returns:
            - time_to_grounding (float): Number of seconds it takes before the ship grounds
            - consequence_of_grounding (float): The cost of the impact.
        '''
        consequence_of_grounding = 2000
        self.ship_model.set_north_pos(self.initial_states.north_position)
        self.ship_model.set_east_pos(self.initial_states.east_position)
        self.ship_model.set_yaw_angle(self.initial_states.yaw_angle_rad)
        self.ship_model.set_surge_speed(self.initial_states.surge_speed)
        self.ship_model.set_sway_speed(self.initial_states.sway_speed)
        self.ship_model.set_yaw_rate(self.initial_states.yaw_rate)
        grounded = False
        while self.ship_model.int.time <= self.ship_model.int.sim_time and not grounded:
            self.ship_model.update_differentials()
            self.ship_model.integrate_differentials()
            self.ship_model.store_simulation_data()
            self.ship_model.int.next_time()
            grounded = self.check_if_grounded(self.ship_model.n, self.ship_model.e)
        time_to_grounding = self.ship_model.int.time
        return time_to_grounding, consequence_of_grounding

    @staticmethod
    def check_if_grounded(x, y):
        if abs(x) >= 200 or abs(y) >= 200:
            return True
        else:
            return False


class AccumulatedRiskInPredictionHorizon:
    ''' Find the probability of an event occurring during a prediction horizon (consisting
        of a set of small adjoining time intervals.

        It is assumed that the event can occur only one time per prediction horizon.
    '''

    def __init__(self, conditional_probabilities_for_each_time_interval: List[float],
                 consequence_of_accident_for_each_time_step: List[float]):
        ''' For each small adjoining time interval, calculate:
            - the unconditional probability of the event occurring for each time interval
            - the unconditional risk ('probability of occurrence' times 'consequence of occurrence'
            - the accumulated (cumulative) probability of the event having occurred in any of the
                preceding time intervals after each time interval
            - the risk accumulated so far in the prediction horizon after each time interval

        '''
        # Find unconditional prob of accident for each time step
        self.unconditional_probability_for_each_time_interval = []
        self.unconditional_risk_at_each_time_interval = []
        self.accumulated_probability_after_each_time_interval = []
        self.accumulated_risk_after_each_time_interval = []
        self.accumulated_probability = 0
        self.accumulated_risk = 0

        for cond_prob, consequence in zip(conditional_probabilities_for_each_time_interval,
                                          consequence_of_accident_for_each_time_step):
            print(self.accumulated_probability)
            self.unconditional_probability_for_each_time_interval.append(
                self.unconditional_probability_at_time_step(
                    conditional_probability_this_time_step=cond_prob,
                    probability_of_event_having_occurred=self.accumulated_probability
                )
            )
            self.update_probability_that_accident_occurred()

            self.unconditional_risk_at_each_time_interval.append(
                self.unconditional_risk_each_time_step(
                    unconditional_probability_this_time_step=self.unconditional_probability_for_each_time_interval[-1],
                    consequence_this_time_step=consequence
                )
            )
            self.update_risk()
            self.accumulated_probability_after_each_time_interval.append(self.accumulated_probability)
            self.accumulated_risk_after_each_time_interval.append(self.accumulated_risk)

    def update_probability_that_accident_occurred(self):
        self.accumulated_probability = sum(self.unconditional_probability_for_each_time_interval)

    def update_risk(self):
        self.accumulated_risk = sum(self.unconditional_risk_at_each_time_interval)

    @staticmethod
    def unconditional_probability_at_time_step(conditional_probability_this_time_step: float,
                                               probability_of_event_having_occurred: float):
        """ The unconditional probability accounts for the possibility that the
            event might have occurred already. Thus, the further out out in the prediction
            horizon, the smaller the unconditional probability will be (i.e. if it is
            almost certain that the event has already occurred, and it can only occur
            once, it is almost certain not to occur now).
        """
        return conditional_probability_this_time_step * (1 - probability_of_event_having_occurred)

    @staticmethod
    def unconditional_risk_each_time_step(unconditional_probability_this_time_step: float,
                                          consequence_this_time_step: float):
        ''' The unconditional risk for a given time step is the probability of an accident at
            the given time step times the price (consequence) of the accident if it occurs at
            the given time step.
        '''
        return unconditional_probability_this_time_step * consequence_this_time_step


if __name__ == '__main__':
    pass
