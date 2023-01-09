feature_order = ["RS1", "RS2", "RS3", "RS4", "RS5", "RS6", "RS7", "RS8", "RR", "LM", "LR",
                 "LU1", "LU2", "LU3", "LU4", "LU5", "PE1", "PE2", "PE3", "PE4", "PE5",
                 "E", "SM", "L_a", "L_b", "L_c", "AQ", "TM_a", "TM_b", "SW_a", "SW_b"]

name_transformation_extra = {
    "feature_bearing_diffs_first": "RS1",
    "feature_bearing_diffs_last": "RS2",
    "feature_bearing_diffs_mean": "RS3",
    "feature_bearing_diffs_mean_first_last": "RS4",
    "feature_bearing_diffs_min": "RS5",
    "feature_bearing_diffs_min_first_last": "RS6",
    "feature_bearing_diffs_max": "RS7",
    "feature_bearing_diffs_max_first_last": "RS8",
    "feature_length_diffs_first": "LU1",
    "feature_length_diffs_last": "LU2",
    "feature_length_diffs_mean": "LU3",
    "feature_length_diffs_min": "LU4",
    "feature_length_diffs_max": "LU5",
    "feature_point_distances_first": "PE1",
    "feature_point_distances_last": "PE2",
    "feature_point_distances_mean": "PE3",
    "feature_point_distances_min": "PE4",
    "feature_point_distances_max": "PE5"
}

name_transformation_base = {
    "feature_bearing_diffs": "RS",
    "feature_route_bearing_change__": "RR",
    "feature_lengths_map_topology": "LM",
    "feature_lengths_projected_map_topology": "LR",
    "feature_length_diffs": "LU",
    "feature_point_distances": "PE",
    "feature_distance__": "E",
    "feature_segment_count__": "SM",
    "feature_side_left": "L_a",
    "feature_side_right": "L_b",
    "feature_side_no_side": "L_c",
    "feature_street_crossings__": "AQ",
    "feature_lsa_lane_type_only_bike": "TM_a",
    "feature_lsa_lane_type_not_only_bike": "TM_b",
    "feature_route_streets_street_changed": "SW_a",
    "feature_route_streets_street_didnt_changed": "SW_b"
}
