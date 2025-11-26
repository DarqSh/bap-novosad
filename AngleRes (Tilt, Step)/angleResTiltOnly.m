theta = linspace(10, 80, 100);  % in degrees
res = zeros(size(theta));
step = 1.8; % in degrees
res = step*sin(2*pi/360*theta);

[~, idx] = min(abs(res - lidar_res));
theta_intersect = theta(idx);
res_intersect = res(idx);

figure;
plot(theta, res, 'b', 'LineWidth', 1); 
hold on;
plot(theta, 0.72*ones(size(theta)), 'r--', 'LineWidth', 1);
grid on;

plot(theta_intersect, res_intersect, 'ko', 'MarkerFaceColor', 'k');
text(theta_intersect+2.5, res_intersect+0.05, ...
    sprintf('(%.1f°, %.2f°)', theta_intersect, res_intersect), ...
    'FontSize', 14);

legend('Resolution for different \theta', 'LiDAR Resolution', 'Location','northwest');
xlabel('Tilt angle \theta', 'FontSize');
ylabel('Resolution between steps', 'FontSize');

matlab2tikz('angleRes_TiltOnly.tex')





