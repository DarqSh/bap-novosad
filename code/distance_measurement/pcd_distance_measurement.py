# https://www.open3d.org/docs/0.19.0/python_api/open3d.visualization.VisualizerWithEditing.html#open3d.visualization.VisualizerWithEditing
import open3d as o3d
import numpy as np

pcd = o3d.io.read_point_cloud("pcd_2026.06.01_16:51:32_263851_source.ply")
pcd_radius, ind_radius = pcd.remove_radius_outlier(nb_points=2, radius=0.1)

print("Instructions:")
print("  Shift + left click  = pick point")
print("  Shift + right click = undo pick")
print("  Q or Esc            = close window")
print()

vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.add_geometry(pcd_radius)
vis.run()
vis.destroy_window()

picked_indices = vis.get_picked_points()
points = np.asarray(pcd_radius.points)

for i in range(len(picked_indices) - 1):
    p1 = points[picked_indices[i]]
    p2 = points[picked_indices[i + 1]]

    distance = np.linalg.norm(p2 - p1)

    print(f"|P{i+1} - P{i}|: {distance:.4f}")