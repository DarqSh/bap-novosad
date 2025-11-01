theta = linspace(30, 60, 100); % in degrees
step = linspace(0.6, 1.8, 64);       % step degrees

[thetamat, stepmat] = meshgrid(theta, step);

resmat = 360/2/pi*sin(thetamat/360*2*pi).*sqrt((cos(stepmat/360*2*pi)-cos(0)).^2+(sin(stepmat/360*2*pi)-sin(0)).^2);

ref = 0.72*ones(size(resmat));



surf(thetamat, stepmat, resmat, 'FaceColor', 'interp', 'EdgeColor','none');
hold on
refsurf = surf(thetamat, stepmat, ref, 'FaceAlpha', 0.7, 'FaceColor', [1 0.3 0.3]); % ref surface 0.72

xlabel('\theta (degrees)');
ylabel('Step Size (degrees)');
zlabel('Angular resolution');
title('Resolution for different \theta and Step Size');

legend(refsurf, 'LiDAR Resolution', 'Location', 'best');

hold off;

