import open3d as o3d
import numpy as np

def downsample_numpy(np_points):
    temp = o3d.geometry.PointCloud()
    temp.points = o3d.utility.Vector3dVector(np_points)
    temp = temp.voxel_down_sample(voxel_size = 0.1)
    return np.asarray(temp.points)

# write your own point cloud file path here. 
# examples/ folder contains some sample point clouds. The name of the file usually follows this structure: pcd_[date]_[number of points]-[description].ply
pcd = o3d.io.read_point_cloud("examples/pcd_2026.05.16_13:41:33_495468-badalign-nocompensation.ply")

# pcd = pcd.voxel_down_sample(0.05) # in a case where point cloud is too dense, downsampling is recommended before outlier removal and visualisation to speed up the process.
                                    # do this for point cloud larger than 500k points. The number of points is written after the date in the file name
                                    # visualisation of 500k takes 5s on Macbook with M1 Pro chip

o3d.visualization.draw_geometries([pcd],
                                  zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
