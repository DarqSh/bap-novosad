# https://www.open3d.org/docs/0.19.0/tutorial/pipelines/global_registration.html
import open3d as o3d
import numpy as np
import copy

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1,0.4,0])
    target_temp.paint_uniform_color([0,0.8,1])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp],
                                      zoom=0.4559,
                                      front=[0.6452, -0.3036, -0.7011],
                                      lookat=[1.9892, 2.0208, 1.8945],
                                      up=[-0.2779, -0.9482, 0.1556])    

def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh
    
def prepare_dataset(voxel_size):
    pcd_source = o3d.io.read_point_cloud("pcd_2026.06.01_16:51:32_263851_source.ply")
    pcd_target = o3d.io.read_point_cloud("pcd_2026.06.02_20:37:36_263845_ransacalign.ply")

    pcd_source.paint_uniform_color([1,0.4,0])
    pcd_target.paint_uniform_color([0,0.8,1])
    o3d.visualization.draw_geometries([pcd_source, pcd_target])

    pcd_source_radius, ind_source_radius = pcd_source.remove_radius_outlier(nb_points=2, radius=0.1)
    pcd_source_stat, ind_source_stat = pcd_source_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8)
    
    pcd_target_radius, ind_target_radius = pcd_target.remove_radius_outlier(nb_points=2, radius=0.1)
    pcd_target_stat, ind_target_stat = pcd_target_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8)

    source_down, source_fpfh = preprocess_point_cloud(pcd_source_stat, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(pcd_target_stat, voxel_size)
    return pcd_source_stat, pcd_target_stat, source_down, target_down, source_fpfh, target_fpfh

# Global registration -- RANSAC
def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5

    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result

# Local registration -- Point-to-Point refinement
def refine_registration(source, target, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.4

    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, result_ransac.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPoint())
    return result




voxel_size = 0.1  
source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(
    voxel_size)



result_ransac = execute_global_registration(source_down, target_down,
                                            source_fpfh, target_fpfh,
                                            voxel_size)
print(result_ransac)
draw_registration_result(source_down, target_down, result_ransac.transformation)


result_icp = refine_registration(source, target, source_fpfh, target_fpfh,
                                 voxel_size)
print(result_icp)
draw_registration_result(source, target, result_icp.transformation)