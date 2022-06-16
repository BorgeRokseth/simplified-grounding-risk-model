import risk_model as risk_model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ship_in_transit_simulator.models import DriftSimulationConfiguration, \
    EnvironmentConfiguration, ShipConfiguration

max_sim_time =400
time_interval = 120
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
simulation_setup = DriftSimulationConfiguration(
    initial_north_position_m=0,
    initial_east_position_m=0,
    initial_yaw_angle_rad=45 * np.pi / 180,
    initial_forward_speed_m_per_s=7,
    initial_sideways_speed_m_per_s=0,
    initial_yaw_rate_rad_per_s=0,
    integration_step=0.5,
    simulation_time=400
)
risk_configuration = risk_model.RiskModelConfiguration(
    max_drift_time_s=max_sim_time,
    risk_time_interval=time_interval
)
risk_model = risk_model.GroundingRiskModel(risk_model_config=risk_configuration,
                                           env_config=env_forces_setup,
                                           environment=placeholder_environment,
                                           scenario_params=scenario_analysis_parameters,
                                           sim_config=simulation_setup,
                                           ttg_sim_config=ship_config)

results = pd.DataFrame().from_dict(risk_model.ttg_simulator.ship_model.simulation_results)
results.plot()

print(risk_model.risk_model_output.probability_of_grounding_in_pto)
print(risk_model.risk_model_output.probability_of_grounding_in_mec)
print(risk_model.risk_model_output.probability_of_grounding_in_pti)
plt.show()