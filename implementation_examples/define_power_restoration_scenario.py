''' Illustrate how the classes defined in "risk_model.py" can be used to define power restoration scenarios

    In this example, we have a ship with a main engine connected to the propeller and a set of two diesel
    generators that can feed power to the propeller through a hybrid shaft generator that can be operated
    as a motor. We look at power restoration after the main engine has stopped. In this case, propulsion
    power is restored if either the main engine is restarted or one of the diesel generators (initially in
    standby mode) and the hybrid shaft generator (initially operated as a generator).

    We start by defining each of the events as startup events (restart ME, start DG1, start DG2 and start
    HSG as motor) using the class "StartUpEvent". The the possible sequences (start ME, start DG1 and HSG,
    and start DG2 and HSG) are defined as start up sequences using the class "StartUpEventSequence".
    Finally, a power restoration scenario is defined using the class "PowerRestorationScenario".
'''

import risk_model
import numpy as np
import matplotlib.pyplot as plt

time = 25

restart_main_engine_parameters = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=10,
    standard_deviation_time_to_restart=0.5,
    time_shift_time_to_restart=20,
    nominal_success_probability=0.7
)
restart_main_engine_event = risk_model.StartUpEvent(restart_main_engine_parameters, time)

start_diesel_generator_1_parameters = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=8,
    standard_deviation_time_to_restart=0.4,
    time_shift_time_to_restart=10,
    nominal_success_probability=1
)
start_diesel_generator_1_event = risk_model.StartUpEvent(start_diesel_generator_1_parameters, time)
start_diesel_generator_2_event = risk_model.StartUpEvent(start_diesel_generator_1_parameters, time)

start_hsg_as_motor_parameters = risk_model.StartUpEventParameters(
    mean_time_to_restart_s=8,
    standard_deviation_time_to_restart=0.3,
    time_shift_time_to_restart=2,
    nominal_success_probability=1
)
start_hsg_as_motor_event = risk_model.StartUpEvent(start_hsg_as_motor_parameters, time)

''' Possible startup sequences are: 
    - restart ME
    - Start DG1 and start HSG as motor, or
    - Start DG2 and start HSG as motor
'''

restore_power_from_main_engine_sequence = risk_model.StartupEventSequence([restart_main_engine_event])
restore_power_from_genset_1_sequence = risk_model.StartupEventSequence([start_diesel_generator_1_event,
                                                                        start_hsg_as_motor_event])
restore_power_from_genset_2_sequence = risk_model.StartupEventSequence([start_diesel_generator_2_event,
                                                                        start_hsg_as_motor_event])

power_restoration_scenairo = risk_model.PowerRestorationScenario([restore_power_from_main_engine_sequence,
                                                                  restore_power_from_genset_1_sequence,
                                                                  restore_power_from_genset_2_sequence])

print('Prob of restarting ME: ' + str(restart_main_engine_event.probability))
print('Prob of starting genset 1 / 2: ' + str(start_diesel_generator_1_event.probability))
print('Prob of starting HSG as motor: ' + str(start_hsg_as_motor_event.probability))

print('\n')
print('Prob of restoration sequence 1 (start ME): ' + str(
    restore_power_from_main_engine_sequence.probability_of_restoration_sequence))
print('Prob of restoration sequence 2 (start DG1 and HSG): ' + str(
    restore_power_from_genset_1_sequence.probability_of_restoration_sequence))
print('Prob of restoration sequence 1 (start DG2 and HSG): ' + str(
    restore_power_from_genset_2_sequence.probability_of_restoration_sequence))

print('\n')
print('Probability of restoring power: ' + str(power_restoration_scenairo.probability_of_power_restoration))

t = np.arange(0, 50, 0.01)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

ax1.plot(t, restart_main_engine_event.startup_time_distribution.pdf(t))
ax2.plot(t, start_diesel_generator_1_event.startup_time_distribution.pdf(t))
ax3.plot(t, start_hsg_as_motor_event.startup_time_distribution.pdf(t))

plt.show()