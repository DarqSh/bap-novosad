import open3d as o3d
import numpy as np

def downsample_numpy(np_points):
    temp = o3d.geometry.PointCloud()
    temp.points = o3d.utility.Vector3dVector(np_points)
    temp = temp.voxel_down_sample(voxel_size = 0.1)
    return np.asarray(temp.points)


pcd = o3d.io.read_point_cloud("successes/pcd_2026.05.16_13:41:33_495468-badalign-nocompensation.ply")

# https://www.open3d.org/docs/latest/tutorial/geometry/transformation.html#Transformation
angle = np.pi/4+np.pi
R = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
pcd.rotate(R, center = (0,0,0))

# np_pcd = np.asarray(pcd.points)
# np_pcd = downsample_numpy(np_pcd)
# pcd.points = o3d.utility.Vector3dVector(np_pcd)


o3d.visualization.draw_geometries([pcd],
                                  zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
