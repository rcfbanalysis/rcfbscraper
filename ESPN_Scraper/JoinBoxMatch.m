% Joins the "boxscore-stats.csv" file and the "matchup-stats.csv" file
year = '2015';
[box, head] = xlsread(strcat(year,' Stats/boxscore-stats.csv'));
match = xlsread(strcat(year,' Stats/matchup-stats.csv'));
matchCols = [ExcelCol('R'), ExcelCol('AS'), ExcelCol('BG'):ExcelCol('BM'), ExcelCol('BQ'), ExcelCol('BR')];

tgs = zeros(size(box));
for i = 1:size(box,1)
    matchIdx = box(i,1) == match(:,1) & box(i,2) == match(:,2);
    matchRow = match(matchIdx,:);
    boxRow = box(i,:);
    tgs(i,:) = boxRow;
    tgs(i,matchCols) = matchRow(matchCols);
end

xlswrite(strcat(year,' Stats/team-game-statistics_new.csv'), head(1,:));
xlswrite(strcat(year,' Stats/team-game-statistics_new.csv'), tgs, 1, 'A2');
