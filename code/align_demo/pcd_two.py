import open3d as o3d
import numpy as np

def display_inlier_outlier(cloud, ind):
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                      zoom=0.3412,
                                      front=[0.4257, -0.2125, -0.8795],
                                      lookat=[2.6172, 2.0475, 1.532],
                                      up=[-0.0694, -0.9768, 0.2024])


pcd_one = o3d.io.read_point_cloud("pcd_2026.06.01_16:51:32_263851_source.ply")
pcd_two = o3d.io.read_point_cloud("pcd_2026.06.01_16:53:58_264111_smallrotate.ply")


# pcd = pcd.voxel_down_sample(0.01)

pcd_one_radius, ind_one_radius = pcd_one.remove_radius_outlier(nb_points=2, radius=0.1)
display_inlier_outlier(pcd_one, ind_one_radius)
pcd_one_stat, ind_one_stat = pcd_one_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8)
display_inlier_outlier(pcd_one_radius, ind_one_stat)

pcd_two_radius, ind_two_radius = pcd_two.remove_radius_outlier(nb_points=2, radius=0.1)
display_inlier_outlier(pcd_two, ind_two_radius)
pcd_two_stat, ind_two_stat = pcd_two_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8)
display_inlier_outlier(pcd_two_radius, ind_two_stat)

pcd_one_stat.paint_uniform_color([1,0,0])
pcd_two_stat.paint_uniform_color([0,0,1])
o3d.visualization.draw_geometries([pcd_one_stat, pcd_two_stat],
                                  zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
