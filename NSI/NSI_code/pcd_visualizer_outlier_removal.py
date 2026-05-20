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


pcd = o3d.io.read_point_cloud("successes/pcd_2026.05.16_13:41:33_495468-badalign-nocompensation.ply")

# https://www.open3d.org/docs/latest/tutorial/geometry/transformation.html#Transformation
angle = np.pi/4+np.pi
R = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
pcd.rotate(R, center = (0,0,0))

# pcd = pcd.voxel_down_sample(0.01)

pcd_radius, ind_radius = pcd.remove_radius_outlier(nb_points=2, radius=0.1)
display_inlier_outlier(pcd, ind_radius)
pcd_stat, ind_stat = pcd_radius.remove_statistical_outlier(nb_neighbors=30, std_ratio=8)
display_inlier_outlier(pcd_radius, ind_stat)
o3d.visualization.draw_geometries([pcd_stat],
                                  zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
