import risk_model
import numpy as np
import matplotlib.pyplot as plt

# Define triggering events (looking at one year of operation)
main_engine_stops = risk_model.TriggeringEvent(rate_of_occurrence=8e-9, time_interval=3600*24*365)
diesel_genset_1_stops = risk_model.TriggeringEvent(rate_of_occurrence=14e-9, time_interval=3600*24*365)
diesel_genset_2_stops = risk_model.TriggeringEvent(rate_of_occurrence=14e-9, time_interval=3600*24*365)
hybrid_shaft_generator_stops = risk_model.TriggeringEvent(rate_of_occurrence=5e-9, time_interval=3600*24*365)

# Define loss-of-propulsion-power scenarios
loss_of_main_engine = risk_model.LossOfPropulsionScenario([main_engine_stops])
loss_of_both_gensets = risk_model.LossOfPropulsionScenario([diesel_genset_1_stops,
                                                            diesel_genset_2_stops])
loss_of_hybrid_shaft_gen = risk_model.LossOfPropulsionScenario([hybrid_shaft_generator_stops])

pto_mode_scenarios = risk_model.MachinerySystemOperatingMode([loss_of_main_engine])
mec_mode_scenarios = risk_model.MachinerySystemOperatingMode([loss_of_main_engine])
pti_mode_scenarios = risk_model.MachinerySystemOperatingMode([loss_of_both_gensets, loss_of_hybrid_shaft_gen])

# Print results
print('Prob of TE-1 (main engine stops): ' + str(main_engine_stops.probability))
print('Prob of TE-2 (genset 1 stops): ' + str(diesel_genset_1_stops.probability))
print('Prob of TE-3 (genset 2 stops): ' + str(diesel_genset_2_stops.probability))
print('Prob of TE-1 (shaft gen stops): ' + str(hybrid_shaft_generator_stops.probability))

print('\n')
print('Prob of LOPP-scenario 1: ' + str(loss_of_main_engine.probability))
print('Prob of LOPP-scenario 2: ' + str(loss_of_both_gensets.probability))
print('Prob of LOPP-scenario 3: ' + str(loss_of_hybrid_shaft_gen.probability))