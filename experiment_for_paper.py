from risk_model import GroundingRiskModel, ScenarioAnalysisParameters, RiskModelConfiguration

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ship_in_transit_simulator.models import DriftSimulationConfiguration, \
    EnvironmentConfiguration, MachineryMode, ShipConfiguration, SimplifiedPropulsionSimulationConfiguration,  \
    ShipModelSimplifiedPropulsion, SimplifiedPropulsionMachinerySystemConfiguration, \
    MachineryModeParams, MachineryModes, StaticObstacle

# Actual ship and sailing environment setup
main_engine_capacity = 2160e3
diesel_gen_capacity = 510e3
hybrid_shaft_gen_as_generator = 'GEN'
hybrid_shaft_gen_as_motor = 'MOTOR'
hybrid_shaft_gen_as_offline = 'OFF'

max_sim_time = 800
time_interval = 120

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
env_forces_setup = EnvironmentConfiguration(
    current_velocity_component_from_north=0,
    current_velocity_component_from_east=1,
    wind_speed=3,
    wind_direction=0
)

pto_params = MachineryModeParams(
    main_engine_capacity=main_engine_capacity,
    electrical_capacity=0,
    shaft_generator_state=hybrid_shaft_gen_as_generator
)

mec_params = MachineryModeParams(
    main_engine_capacity=main_engine_capacity,
    electrical_capacity=diesel_gen_capacity,
    shaft_generator_state=hybrid_shaft_gen_as_offline
)

pti_params = MachineryModeParams(
    main_engine_capacity=0,
    electrical_capacity=2*diesel_gen_capacity,
    shaft_generator_state=hybrid_shaft_gen_as_motor
)

pto_mode = MachineryMode(params=pti_params)
mec_mode = MachineryMode(params=mec_params)
pti_mode = MachineryMode(pti_params)


machinery_config = SimplifiedPropulsionMachinerySystemConfiguration(
    hotel_load=200e3,
    machinery_modes=MachineryModes([pto_mode, mec_mode, pti_mode]),
    thrust_force_dynamic_time_constant=15,
    rudder_angle_to_sway_force_coefficient=50e3,
    rudder_angle_to_yaw_force_coefficient=1000e3,
    max_rudder_angle_degrees=30
)

simulation_setup = SimplifiedPropulsionSimulationConfiguration(
    route_name="/Users/borgerokseth/Documents/source/drifting-grounding-risk-model/experiement_route.txt",
    initial_north_position_m=0,
    initial_east_position_m=0,
    initial_forward_speed_m_per_s=7,
    initial_sideways_speed_m_per_s=0,
    initial_thrust_force=0,
    initial_yaw_angle_rad=45*np.pi/180,
    initial_yaw_rate_rad_per_s=0,
    machinery_system_operating_mode=1,
    integration_step=0.3,
    simulation_time=600
)

ship_model = ShipModelSimplifiedPropulsion(
    ship_config=ship_config,
    machinery_config=machinery_config,
    environment_config=env_forces_setup,
    simulation_config=simulation_setup
)

obstacle = StaticObstacle(n_pos=1500, e_pos=1600, radius=250)
secondary_obstacle = StaticObstacle(n_pos=1700, e_pos=2300, radius=250)
third_obstacle = StaticObstacle(n_pos=2300, e_pos=1450, radius=250)
time_since_last_ship_drawing = 0
desired_heading = []
rudder_angles = []


# Simulation-based online risk model setup
max_sim_time = 400
time_interval = 120

scenario_analysis_parameters = ScenarioAnalysisParameters(
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

risk_configuration = RiskModelConfiguration(
    max_drift_time_s=max_sim_time,
    risk_time_interval=time_interval
)

risk_model = []
probability_of_grounding_in_pto = []
probability_of_grounding_in_mec = []
probability_of_grounding_in_pti = []
risk_model_interval = 0
risk_time = []

while ship_model.int.time <= ship_model.int.sim_time:
    desired_speed_m_per_sec = 7
    rudder_angle, psi_d = ship_model.rudderang_from_route()
    desired_heading.append(psi_d*180/np.pi)
    rudder_angles.append(rudder_angle)
    engine_load = ship_model.loadperc_from_speedref(
        speed_ref=desired_speed_m_per_sec)

    ship_model.update_differentials(engine_load, rudder_angle)
    ship_model.integrate_differentials()
    ship_model.store_simulation_data(load_perc=engine_load)
    # Make a drawing of the ship from above every 20 second
    if time_since_last_ship_drawing > 30:
        ship_model.ship_snap_shot()
        time_since_last_ship_drawing = 0
    time_since_last_ship_drawing += ship_model.int.dt

    
    if risk_model_interval > 5:
        drifting_sim_setup = DriftSimulationConfiguration(
            initial_north_position_m=ship_model.n,
            initial_east_position_m=ship_model.e,
            initial_yaw_angle_rad=ship_model.psi,
            initial_forward_speed_m_per_s=ship_model.u,
            initial_sideways_speed_m_per_s=ship_model.v,
            initial_yaw_rate_rad_per_s=ship_model.r,
            integration_step=0.5,
            simulation_time=max_sim_time
        )
        risk_model.append(
            GroundingRiskModel(
            risk_model_config=risk_configuration,
            env_config=env_forces_setup,
            environment=[obstacle, secondary_obstacle, third_obstacle],
            scenario_params=scenario_analysis_parameters,
            sim_config=drifting_sim_setup,
            ttg_sim_config=ship_config
            )
        )
        risk_model_interval = 0
        risk_output = risk_model[-1].calculate_risk_output()
        probability_of_grounding_in_pto.append(risk_model[-1].risk_model_output.probability_of_grounding_in_pto)
        probability_of_grounding_in_mec.append(risk_model[-1].risk_model_output.probability_of_grounding_in_mec)
        probability_of_grounding_in_pti.append(risk_model[-1].risk_model_output.probability_of_grounding_in_pti)
        risk_time.append(ship_model.int.time)
    else:
        risk_model_interval += ship_model.int.dt


    ship_model.int.next_time()

# Store the simulation results in a pandas dataframe
results = pd.DataFrame().from_dict(ship_model.simulation_results)
risk_model_results = []
for risk_model_instance in risk_model:
    risk_model_results.append(pd.DataFrame().from_dict(risk_model_instance.ttg_simulator.ship_model.simulation_results))

# Example on how a map-view can be generated
map_fig, map_ax = plt.subplots()
map_ax.plot(results['east position [m]'], results['north position [m]'])
for drift_off in risk_model_results:
    map_ax.plot(drift_off["east position [m]"], drift_off["north position [m]"], color="red")

map_ax.scatter(ship_model.navigate.east, ship_model.navigate.north,
               marker='x', color='green')  # Plot the waypoints
for x, y in zip(ship_model.ship_drawings[1], ship_model.ship_drawings[0]):
    map_ax.plot(x, y, color='black')

obstacle.plot_obst(ax=map_ax)
secondary_obstacle.plot_obst(ax=map_ax)
third_obstacle.plot_obst(ax=map_ax)

heading_fig, heading_ax = plt.subplots()
heading_ax.plot(results["time [s]"], desired_heading, label="desired")
heading_ax.plot(results["time [s]"], results["yaw angle [deg]"])
heading_ax.legend()

rudder_fig, rudder_ax = plt.subplots()
rudder_ax.plot(results["time [s]"], rudder_angles, label="rudder")
rudder_ax.legend()

map_ax.set_aspect('equal')

risk_fig, risk_ax = plt.subplots()
risk_ax.plot(risk_time, probability_of_grounding_in_pto, label="PTO")
risk_ax.plot(risk_time, probability_of_grounding_in_mec, label="MEC")
risk_ax.plot(risk_time, probability_of_grounding_in_pti, label="PTI")
plt.show()
