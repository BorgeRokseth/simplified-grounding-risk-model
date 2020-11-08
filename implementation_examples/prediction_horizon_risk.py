from risk_model import GroundingRiskModel, AccumulatedRiskInPredictionHorizon,\
    RiskModelConfiguration, MotionStateInput

risk_model_configuration = RiskModelConfiguration(
    max_drift_time_s=1000,
    risk_time_interval=0.5
)
grounding_risk_model = GroundingRiskModel(risk_model_configuration)

probability_each_time_interval = []
consequence_each_time_interval = []
conditional_risk = []
for time_instance in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
    # Update motion states
    n = 3 - time_instance
    e = 0
    psi = 0
    u = 5 + time_instance * 2
    v = 0.2
    r = 0

    motion_states = MotionStateInput(
        north_position=n,
        east_position=e,
        yaw_angle_rad=psi,
        surge_speed=u,
        sway_speed=v,
        yaw_rate=r
    )

    probability, consequence = grounding_risk_model.calculate_risk_output(current_motion_states=motion_states, delta_t=0.5)
    probability_each_time_interval.append(probability)
    consequence_each_time_interval.append(consequence)
    conditional_risk.append(probability * consequence)

risk_over_prediction_horizon = AccumulatedRiskInPredictionHorizon(
    conditional_probabilities_for_each_time_interval=probability_each_time_interval,
    consequence_of_accident_for_each_time_step=consequence_each_time_interval
)

print('Conditional probability for each time interval: ')
print(probability_each_time_interval)
print('Unconditional probability for each time interval: ')
print(risk_over_prediction_horizon.unconditional_probability_for_each_time_interval)
print('\n')

print('Conditional risk for each time interval: ')
print(conditional_risk)
print('Unconditional risk for each time interval: ')
print(risk_over_prediction_horizon.unconditional_risk_at_each_time_interval)
print('\n')

print('Accumulated probability after each time interval: ')
print(risk_over_prediction_horizon.accumulated_probability_after_each_time_interval)
print('\n')

print('Accumulated risk after each time interval: ')
print(risk_over_prediction_horizon.accumulated_risk_after_each_time_interval)
print('\n')