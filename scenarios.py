from typing import NamedTuple, List
import numpy as np
import scipy.stats


class StartUpEventParameters(NamedTuple):
    mean_time_to_restart_s: float
    standard_deviation_time_to_restart: float
    time_shift_time_to_restart: float
    nominal_success_probability: float


class StartUpEvent:
    def __init__(self, parameters: StartUpEventParameters, time_available):
        self.mu = parameters.mean_time_to_restart_s
        self.sigma = parameters.standard_deviation_time_to_restart
        self.startup_time_distribution = scipy.stats.lognorm(
            scale=parameters.mean_time_to_restart_s,
            s=np.sqrt(parameters.standard_deviation_time_to_restart),
            loc=parameters.time_shift_time_to_restart,
        )
        self.nominal_success_probability = parameters.nominal_success_probability
        self.probability = self.probability(time=time_available)

    def probability(self, time):
        return self.nominal_success_probability \
               * self.startup_time_distribution.cdf(time)

    def update_probability(self, time):
        self.probability = self.probability(time)

class StartupEventSequence:
    ''' Assumes that all restart events are independent of each other
    '''

    def __init__(self, list_of_startup_events: List[StartUpEvent]):
        list_of_restoration_probabilities = []
        self.startup_events = list_of_startup_events
        for event in self.startup_events:
            list_of_restoration_probabilities.append(event.probability)
        self.probability_of_restoration_sequence = np.prod(list_of_restoration_probabilities)

    def update_startup_events(self, time):
        for event in self.startup_events:
            event.update_probability(time)

class PowerRestorationEventTree:
    def __init__(self, startup_event_sequences: List[StartupEventSequence]):
        probability_of_no_success = 1
        for sequence in startup_event_sequences:
            probability_of_no_success = probability_of_no_success * (1 - sequence.probability_of_restoration_sequence)
        self.probability = 1 - probability_of_no_success


class TriggeringEvent:
    def __init__(self, rate_of_occurrence, time_interval):
        self.rate = rate_of_occurrence
        self.dt = time_interval
        self.probability = self.probability_of_occurrence()

    def probability_of_occurrence(self):
        return 1 - np.exp(-self.rate * self.dt)


class LossOfPropulsionScenario:
    ''' A LOPP-scenario is described as a minimial cutset of triggering events.
    '''

    def __init__(self, triggering_events: List[TriggeringEvent]):
        list_of_triggering_event_probabilities = []
        for event in triggering_events:
            list_of_triggering_event_probabilities.append(event.probability)
        self.probability = np.prod(list_of_triggering_event_probabilities)


class Scenario:
    def __init__(self, loss_scenario: LossOfPropulsionScenario,
                 restoration_scenario: PowerRestorationEventTree):
        self.loss_scenario = loss_scenario
        self.restoration_scenario = restoration_scenario


class MachinerySystemOperatingMode:
    def __init__(self, possible_scenarios: List[Scenario]):
        self.scenarios = possible_scenarios
        prod = 1
        for s in self.scenarios:
            prob_of_grounding_given_loss = 1 - s.restoration_scenario.probability
            prod = prod * 1 - prob_of_grounding_given_loss * s.loss_scenario.probability
        self.probability_of_grounding = 1 - prod

