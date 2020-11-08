import risk_model
import numpy as np
import matplotlib.pyplot as plt
from ship_in_transit_simulator.models import DriftSimulationConfiguration, \
    EnvironmentConfiguration, ShipConfiguration

max_sim_time = 250
time_step = 24 * 3600
n = 10
time_intervals = np.arange(start=0, stop=n * time_step, step=time_step)

placeholder_environment = risk_model.ENC()

ship_config = ShipConfiguration(
    coefficient_of_deadweight_to_displacement=0.7,
    bunkers=200000,
    ballast=200000,
    length_of_ship=80,
    width_of_ship=16,
    added_mass_coefficient_in_surge=0.4,
    added_mass_coefficient_in_sway=0.4,
    added_mass_coefficient_in_yaw=0.4,
    dead_weight_tonnage=3850000,
    mass_over_linear_friction_coefficient_in_surge=130,
    mass_over_linear_friction_coefficient_in_sway=18,
    mass_over_linear_friction_coefficient_in_yaw=90,
    nonlinear_friction_coefficient__in_surge=2400,
    nonlinear_friction_coefficient__in_sway=4000,
    nonlinear_friction_coefficient__in_yaw=400
)
scenario_analysis_parameters = risk_model.ScenarioAnalysisParameters(
    main_engine_failure_rate=3e-9,
    genset_one_failure_rate=6e-9,
    genset_two_failure_rate=6e-9,
    hsg_failure_rate=2e-9,
    main_engine_mean_start_time=50,
    main_engine_start_time_std=1.2,
    main_engine_start_time_shift=20,
    main_engine_nominal_start_prob=1,
    main_engine_mean_restart_time=50,
    main_engine_restart_time_std=1.2,
    main_engine_restart_time_shift=20,
    main_engine_nominal_restart_prob=0.4,
    genset_one_mean_start_time=35,
    genset_one_start_time_std=1.0,
    genset_one_start_time_shift=14,
    genset_one_nominal_start_prob=1,
    genset_two_mean_start_time=35,
    genset_two_start_time_std=1.0,
    genset_two_start_time_shift=14,
    genset_two_nominal_start_prob=1,
    genset_one_mean_restart_time=35,
    genset_one_restart_time_std=1.0,
    genset_one_restart_time_shift=14,
    genset_one_nominal_restart_prob=0.5,
    genset_two_mean_restart_time=35,
    genset_two_restart_time_std=1.0,
    genset_two_restart_time_shift=14,
    genset_two_nominal_restart_prob=0.5,
    hsg_mean_start_time=12,
    hsg_start_time_std=1,
    hsg_start_time_shift=3,
    hsg_nominal_start_prob=1,
    hsg_mean_restart_time=12,
    hsg_restart_time_std=1,
    hsg_restart_time_shift=3,
    hsg_nominal_restart_prob=0.8,
)
env_forces_setup = EnvironmentConfiguration(
    current_velocity_component_from_north=0,
    current_velocity_component_from_east=1,
    wind_speed=5,
    wind_direction=0
)

risk_configuration = risk_model.RiskModelConfiguration(
    max_drift_time_s=max_sim_time,
    risk_time_interval=time_step
)

probability_each_time_interval = []
consequence_each_time_interval = []
conditional_risk = []
risk_mod = []

for time_instance in time_intervals:  # prediction horizon
    # Update motion states
    n = 0
    e = 0
    psi = 0
    u = 7
    v = 0
    r = 0

    simulation_setup = DriftSimulationConfiguration(
        initial_north_position_m=n,
        initial_east_position_m=e,
        initial_yaw_angle_rad=psi,
        initial_forward_speed_m_per_s=u,
        initial_sideways_speed_m_per_s=v,
        initial_yaw_rate_rad_per_s=r,
        integration_step=0.5,
        simulation_time=4000
    )

    risk_mod.append(risk_model.GroundingRiskModel(risk_model_config=risk_configuration,
                                                  env_config=env_forces_setup,
                                                  environment=placeholder_environment,
                                                  scenario_params=scenario_analysis_parameters,
                                                  sim_config=simulation_setup,
                                                  ttg_sim_config=ship_config))

    probability_each_time_interval.append(risk_mod[-1].risk_model_output.probability_of_grounding_in_pto)
    consequence_each_time_interval.append(risk_mod[-1].risk_model_output.consequence_of_grounding)
    conditional_risk.append(risk_mod[-1].risk_model_output.probability_of_grounding_in_pto
                            * risk_mod[-1].risk_model_output.consequence_of_grounding)

risk_over_prediction_horizon = risk_model.AccumulatedRiskInPredictionHorizon(
    conditional_probabilities_for_each_time_interval=probability_each_time_interval,
    consequence_of_accident_for_each_time_step=consequence_each_time_interval
)

fig, (ax1, ax2) = plt.subplots(2, 1)

ax1.step(time_intervals, probability_each_time_interval, label='P(g|not grounded already)')
ax1.step(time_intervals,
         risk_over_prediction_horizon.unconditional_probability_for_each_time_interval,
         label='p(g)')
ax2.step(time_intervals, risk_over_prediction_horizon.accumulated_probability_after_each_time_interval,
         label='P(grounded already)')
ax1.legend()
ax2.legend()
plt.show()
