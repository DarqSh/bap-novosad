theta = linspace(30, 80, 100); % in degrees
step = linspace(0.6, 1.4, 64);       % step degrees

[thetamat, stepmat] = meshgrid(theta, step);

resmat = stepmat.*sin(2*pi/360*thetamat);

ref = 0.72*ones(size(resmat));



surf(thetamat, stepmat, resmat, 'FaceColor', 'interp', 'EdgeColor','none');
hold on
refsurf = surf(thetamat, stepmat, ref, 'FaceAlpha', 0.7, 'FaceColor', [1 0.3 0.3]); % ref surface 0.72

% plot3(36.99, 1.19, 0.72, 'ko', 'MarkerFaceColor', 'k');
% text(36.99, 1.19, 0.72, ...
%      sprintf('(%.1f°, %.2f°, %.2f°)', 36.99, 1.19, 0.72), ...
%      'BackgroundColor', 'w', ...      % white background
%      'EdgeColor', 'k', ...            % black border
%      'Margin', 4, ...                 % padding inside the box
%      'FontSize', 10, ...
%      'VerticalAlignment', 'bottom', ...
%      'HorizontalAlignment', 'left');



xlabel('$\theta$ [$\deg$]','Interpreter','latex','FontSize',16);
ylabel('Step size [$\deg$]','Interpreter','latex','FontSize',16);
zlabel('Angular resolution [$\deg$]','Interpreter','latex','FontSize',16);

legend(refsurf, 'LiDAR Resolution 0.72 $\deg$',...
       'Interpreter','latex','FontSize',15,'Location','northwest');

hold off;
matlab2tikz('test.tex')