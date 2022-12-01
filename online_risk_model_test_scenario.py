from re import T

from ship_in_transit_simulator.models import EngineThrottleFromSpeedSetPoint, SpecificFuelConsumptionBaudouin6M26Dot3, \
    SpecificFuelConsumptionWartila6L26, ThrottleControllerGains, ThrottleFromSpeedSetPointSimplifiedPropulsion, \
        HeadingControllerGains, HeadingByRouteController


if __name__ == '__main__':
    import seacharts
    import shapely.geometry as geo

    from risk_model import GroundingRiskModel, ScenarioAnalysisParameters, RiskModelConfiguration

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from ship_in_transit_simulator.models import SimulationConfiguration, \
        EnvironmentConfiguration, MachineryMode, ShipConfiguration, ShipModelSimplifiedPropulsion,  \
        SimplifiedPropulsionMachinerySystemConfiguration, \
        MachineryModeParams, MachineryModes, StaticObstacle
 

    # Simulation parameters
    risk_calculation_interval = 10
    max_drift_sim_time = 800
    main_sim_time = 2600
    main_time_step = 0.3
    time_between_snapshots = 25
    load_new_map_data = False

    wind_speed = 0
    wind_direction = 270 *np.pi/180

    # Load seachart
    size = 19000, 19000
    center = 182602, 7098749
    files = ['Trondelag.gdb']
    enc = seacharts.ENC(size=size, center=center, files=files, new_data=load_new_map_data)


    # Actual ship and sailing environment setup
    main_engine_capacity = 2160e3
    diesel_gen_capacity = 510e3
    hybrid_shaft_gen_as_generator = 'GEN'
    hybrid_shaft_gen_as_motor = 'MOTOR'
    hybrid_shaft_gen_as_offline = 'OFF'

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
        current_velocity_component_from_east=0,
        wind_speed=wind_speed,
        wind_direction=wind_direction
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

    fuel_curves_me = SpecificFuelConsumptionWartila6L26()
    fuel_curves_dg = SpecificFuelConsumptionBaudouin6M26Dot3()


    machinery_config = SimplifiedPropulsionMachinerySystemConfiguration(
        hotel_load=200e3,
        machinery_modes=MachineryModes([pto_mode, mec_mode, pti_mode]),
        machinery_operating_mode=1,
        specific_fuel_consumption_coefficients_me=fuel_curves_me.fuel_consumption_coefficients(),
        specific_fuel_consumption_coefficients_dg=fuel_curves_dg.fuel_consumption_coefficients(),
        thrust_force_dynamic_time_constant=15,
        rudder_angle_to_sway_force_coefficient=50e3,
        rudder_angle_to_yaw_force_coefficient=1000e3,
        max_rudder_angle_degrees=30
    )

    simulation_setup = SimulationConfiguration(
        initial_north_position_m=7104389.06,
        initial_east_position_m=190165.4,
        initial_forward_speed_m_per_s=7,
        initial_sideways_speed_m_per_s=0,
        initial_yaw_angle_rad=-130*np.pi/180,
        initial_yaw_rate_rad_per_s=0,
        integration_step=main_time_step,
        simulation_time=main_sim_time
    )

    ship_model = ShipModelSimplifiedPropulsion(
        ship_config=ship_config,
        machinery_config=machinery_config,
        environment_config=env_forces_setup,
        simulation_config=simulation_setup
    )

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
        max_drift_time_s=max_drift_sim_time,
        risk_time_interval=risk_calculation_interval
    )

    heading_data = []
    time = []
    rudder_angles = []

    # Lists for storing ships and trails
    ships = []
    id = 0

    # Lists for storing risk data output
    risk_model = []
    probability_of_grounding_in_pto = []
    probability_of_grounding_in_mec = []
    probability_of_grounding_in_pti = []
    relative_probability_of_grounding_in_pto = []
    relative_probability_of_grounding_in_mec = []
    relative_probability_of_grounding_in_pti = []
    drift_ships = []

    time_since_risk_calculation = 25
    risk_time = []

    time_since_snapshot = time_between_snapshots

    shore = enc.shore.geometry

    # Ship controllers
    desired_speed_m_per_sec = 7
    speed_controller = ThrottleFromSpeedSetPointSimplifiedPropulsion(kp=4, ki=0.02, time_step=main_time_step)
    heading_controller_gains = HeadingControllerGains(kp=7, kd=90, ki=0.01)
    auto_pilot = HeadingByRouteController(
        route_name="/Users/borgerokseth/Documents/source/drifting-grounding-risk-model/experiement_route.txt",
        heading_controller_gains=heading_controller_gains,
        time_step=main_time_step,
        max_rudder_angle=machinery_config.max_rudder_angle_degrees * np.pi/180
    )

    while ship_model.int.time <= ship_model.int.sim_time:
        # Measurements
        north_position = ship_model.north
        east_position = ship_model.east
        heading = ship_model.yaw_angle
        speed = ship_model.forward_speed

        # Control actions
        rudder_angle = auto_pilot.rudder_angle_from_route(
            north_position=north_position,
            east_position=east_position,
            heading=heading
        )
        engine_load = speed_controller.throttle(speed_set_point=desired_speed_m_per_sec, measured_speed=speed)
        
        # Store data
        heading_data.append(heading)
        time.append(ship_model.int.time)

        # Update states and step
        ship_model.update_differentials(engine_load, rudder_angle=rudder_angle)
        ship_model.integrate_differentials()
        ship_model.store_simulation_data(load_perc=engine_load)

        # Add ownship snapshot to chart
        if time_since_snapshot > time_between_snapshots:
            id += 1
            ships.append((id, int(ship_model.east), int(ship_model.north), int(ship_model.yaw_angle*180/np.pi), "green"))
            time_since_snapshot = 0
        time_since_snapshot += ship_model.int.dt
        
        if time_since_risk_calculation > risk_calculation_interval:
            drifting_sim_setup = SimulationConfiguration(
                initial_north_position_m=ship_model.north,
                initial_east_position_m=ship_model.east,
                initial_yaw_angle_rad=ship_model.yaw_angle,
                initial_forward_speed_m_per_s=ship_model.forward_speed,
                initial_sideways_speed_m_per_s=ship_model.sideways_speed,
                initial_yaw_rate_rad_per_s=ship_model.yaw_rate,
                integration_step=0.5,
                simulation_time=max_drift_sim_time
            )
            risk_model.append(
                GroundingRiskModel(
                risk_model_config=risk_configuration,
                env_config=env_forces_setup,
                environment=shore,
                scenario_params=scenario_analysis_parameters,
                sim_config=drifting_sim_setup,
                ttg_sim_config=ship_config
                )
            )
            time_since_risk_calculation = 0
            risk_output = risk_model[-1].calculate_risk_output()
            probability_of_grounding_in_pto.append(risk_model[-1].risk_model_output.probability_of_grounding_in_pto)
            probability_of_grounding_in_mec.append(risk_model[-1].risk_model_output.probability_of_grounding_in_mec)
            probability_of_grounding_in_pti.append(risk_model[-1].risk_model_output.probability_of_grounding_in_pti)

            relative_probability_of_grounding_in_pto.append(
                risk_model[-1].risk_model_output.probability_of_grounding_in_pto / 
                risk_model[-1].risk_model_output.probability_of_grounding_in_pto
                )
            relative_probability_of_grounding_in_mec.append(
                risk_model[-1].risk_model_output.probability_of_grounding_in_mec / 
                risk_model[-1].risk_model_output.probability_of_grounding_in_pto
                )
            relative_probability_of_grounding_in_pti.append(
                risk_model[-1].risk_model_output.probability_of_grounding_in_pti / 
                risk_model[-1].risk_model_output.probability_of_grounding_in_pto
                )
            risk_time.append(ship_model.int.time)
        else:
            time_since_risk_calculation += ship_model.int.dt

        ship_model.int.next_time()



    route_line = []
    for northing, easting in zip(auto_pilot.navigate.north, auto_pilot.navigate.east):
        route_line.append((easting, northing))

    for risk_model_instance in risk_model:
        for ship in risk_model_instance.ttg_simulator.drifting_ship_positions:
            ships.append((id, int(ship.east), int(ship.north), int(ship.heading_deg), "red"))
            id += 1



    enc.draw_line(route_line, "white")
    #  enc.draw_line(trace, "green", thickness=1)
    enc.add_vessels(*ships)
    enc.add_hazards(depth=5)


    enc.show_display()

    risk_fig, (risk_ax_1, risk_ax_2) = plt.subplots(nrows=2)
    risk_ax_1.plot(risk_time, probability_of_grounding_in_pto, label="PTO")
    risk_ax_1.plot(risk_time, probability_of_grounding_in_mec, label="MEC")
    risk_ax_1.plot(risk_time, probability_of_grounding_in_pti, label="PTI")
    risk_ax_1.legend()

    risk_ax_2.plot(risk_time, relative_probability_of_grounding_in_pto, label="PTO")
    risk_ax_2.plot(risk_time, relative_probability_of_grounding_in_mec, label="MEC")
    risk_ax_2.plot(risk_time, relative_probability_of_grounding_in_pti, label="PTI")


    plt.show()
