'''
    Provides classes to estimate drifting grounding risk either for a small time interval or a
    prediction horizon (a set of adjoining small time intervals.
'''

from typing import NamedTuple, List
import numpy as np


class MotionStateInput(NamedTuple):
    north_position: float
    east_position: float
    yaw_angle_rad: float
    surge_speed: float
    sway_speed: float
    yaw_rate: float


class RiskModelConfiguration(NamedTuple):
    max_drift_time_s: float


class GroundingRiskModel:
    def __init__(self, config: RiskModelConfiguration):
        self.max_simulation_time = config.max_drift_time_s

    def risk(self, current_motion_states: MotionStateInput, delta_t: float):
        ''' Calculate the probability and consequence (cost) of grounding during a small time interval
            'delta_t' where the ship is in the states given by 'current_motion_states'.

            The method is currently implemented as temporary mock-up

            args:
            - current_motion_states (MotionStateInput): See MotionStateInput-class
            - delta_t (float): The duration of the small time interval

            returns:
            - probability_of_grounding (float): The probability of grounding during the time interval
            - consequence_of_grounding (float): The cost of grounding during the time interval
        '''

        # Probability (and consequence) of grounding given the loss of propulsion power
        ttg_simulator = TimeToGroundingSimulator(current_motion_states, max_simulation_time=self.max_simulation_time)
        time_to_grounding, consequence_of_grounding = ttg_simulator.time_to_grounding()

        # Probability of experiencing LOPP over the current time interval
        probability_of_lopp = delta_t
        probability_of_grounding = probability_of_lopp \
                                   * (1 - (self.max_simulation_time - time_to_grounding) / self.max_simulation_time)
        return probability_of_grounding, consequence_of_grounding


class TimeToGroundingSimulator:
    ''' Simulate a ship drifting from given initial states until a grounding occurs
        or the maximum simulation time has elapsed.
    '''

    def __init__(self, initial_states: MotionStateInput, max_simulation_time: float):
        ''' Set up simulation.

            args:
            - initial_states (MotionStateInput): See MotionStateInput-class
            - max_simulation_time (float): Number of seconds after which to terminate simulation if
            grounding has not occurred.
        '''
        self.north_position = initial_states.north_position
        self.speed = np.sqrt(initial_states.surge_speed ** 2 + initial_states.sway_speed ** 2)
        self.max_sim_time = max_simulation_time

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
        time_to_grounding = max(min(400 * self.north_position, self.max_sim_time), 0)
        print(time_to_grounding)
        consequence_of_grounding = self.speed ** 2 * 100
        return time_to_grounding, consequence_of_grounding


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
        pass

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
