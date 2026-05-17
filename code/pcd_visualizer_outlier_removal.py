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

# write your own point cloud file path here
pcd = o3d.io.read_point_cloud("examples/pcd_2026.05.16_13:41:33_495468-badalign-nocompensation.ply")


# pcd = pcd.voxel_down_sample(0.05) # in a case where point cloud is too dense, downsampling is recommended before outlier removal and visualisation to speed up the process.
                                    # do this for point cloud larger than 500k points. The number of points is written after the date in the file name
                                    # visualisation of 500k takes 3s on Macbook with M1 Pro chip, filtering with parameters in the code below takes 15s


# https://www.open3d.org/docs/release/tutorial/geometry/pointcloud_outlier_removal.html
pcd_radius, ind_radius = pcd.remove_radius_outlier(nb_points=2, radius=0.1) # change parameters at your will
display_inlier_outlier(pcd, ind_radius)
pcd_stat, ind_stat = pcd_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8) # change parameters at your will
display_inlier_outlier(pcd_radius, ind_stat)
o3d.visualization.draw_geometries([pcd_stat],
                                  zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
