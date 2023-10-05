"""
    Provides classes to estimate drifting grounding risk either for a small time interval or a
    prediction horizon (a set of adjoining small time intervals).
"""
import numpy as np
from tkinter import E
from typing import NamedTuple, List
import shapely.geometry as geo

import scenarios
from ship_in_transit_simulator.models import  \
    EnvironmentConfiguration, ShipModelWithoutPropulsion, ShipConfiguration, SimulationConfiguration


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


class ShipPose:
    def __init__(self, north, east, heading_deg):
        self.north = north
        self.east = east
        self.heading_deg = heading_deg


class ScenarioAnalysisParameters(NamedTuple):
    main_engine_failure_rate: float
    main_engine_mean_restart_time: float
    main_engine_restart_time_std: float
    main_engine_restart_time_shift: float
    main_engine_nominal_restart_prob: float


class GroundingRiskModel:
    def __init__(self, risk_model_config: RiskModelConfiguration,
                 ttg_sim_config: ShipConfiguration,
                 sim_config: SimulationConfiguration,
                 env_config: EnvironmentConfiguration,
                 environment: geo.multipolygon.MultiPolygon,
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
        time_to_grounding = self.ttg_simulator.time_to_grounding()
        return self.scenario_analysis(available_recovery_time=time_to_grounding)


    def scenario_analysis(self, available_recovery_time: float):
        return LossOfMainEngineScenario(
            available_recovery_time=available_recovery_time, 
            risk_time_interval=self.risk_time_interval,
            scenario_parameters=self.scenario_params
            ).scenario_probabilities()


class LossOfMainEngineScenario:
    def __init__(
            self,
            available_recovery_time: float,
            risk_time_interval: float,
            scenario_parameters: ScenarioAnalysisParameters
    ) -> None:
        self.scenario_params = scenario_parameters
        self.risk_time_interval = risk_time_interval
        main_engine_stops = scenarios.TriggeringEvent(rate_of_occurrence=self.scenario_params.main_engine_failure_rate,
                                                      time_interval=self.risk_time_interval)
        loss_of_main_engine = scenarios.LossOfPropulsionScenario([main_engine_stops])

        restart_main_engine_params = scenarios.StartUpEventParameters(
            mean_time_to_restart_s=self.scenario_params.main_engine_mean_restart_time,
            standard_deviation_time_to_restart=self.scenario_params.main_engine_restart_time_std,
            time_shift_time_to_restart=self.scenario_params.main_engine_restart_time_shift,
            nominal_success_probability=self.scenario_params.main_engine_nominal_restart_prob
        )
        restart_main_engine = scenarios.StartUpEvent(parameters=restart_main_engine_params,
                                                     time_available=available_recovery_time)

        restore_from_loss_of_main_engine = scenarios.PowerRestorationEventTree(
            success_paths=[
                scenarios.EventTreePath(
                    path=[scenarios.PathElement(event=restart_main_engine, occurs=True),]
                )
            ],
            time_to_grounding=available_recovery_time
        )

        self.loss_of_main_engine = scenarios.Scenario(
            loss_scenario=loss_of_main_engine,
            restoration_scenario=restore_from_loss_of_main_engine
        )
    
    def scenario_probabilities(self) -> float:
        return scenarios.ScenarioProbabilityCalculation(
            possible_scenarios=[self.loss_of_main_engine]
        ).probability_of_grounding


class TimeToGroundingSimulator:
    ''' Simulate a ship drifting from given initial states until a grounding occurs
        or the maximum simulation time has elapsed.
    '''

    def __init__(self, initial_states: MotionStateInput,
                 environment: geo.multipolygon.MultiPolygon,
                 max_simulation_time: float,
                 ship_config: ShipConfiguration,
                 simulation_config: SimulationConfiguration,
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
        grounded = False
        while self.ship_model.int.time <= self.ship_model.int.sim_time and not grounded:
            self.ship_model.update_differentials()
            self.ship_model.integrate_differentials()
            self.ship_model.store_simulation_data()
            self.ship_model.int.next_time()
            grounded = self.check_if_grounded(self.ship_model.north, self.ship_model.east)
        time_to_grounding = self.ship_model.int.time
        return time_to_grounding

    def check_if_grounded(self, ship_north_position_m, ship_east_position_m):
        ship_center_point = geo.Point(ship_east_position_m, ship_north_position_m)
        distance = ship_center_point.distance(self.environment)
        if abs(distance) <= 50:
            return True
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
            - the unconditional risk ('probability of occurrence' times 'consequence of occurrence')
            - the accumulated (cumulative) probability of the event having occurred in any of the
            preceding time intervals after each time interval
            - the accumulated risk so far in the prediction horizon after each time interval (i.e.
            the cumulative distribution)
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
            event might have occurred already. Thus, the further out in the prediction
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
