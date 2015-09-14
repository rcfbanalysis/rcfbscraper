% Compare two team-game-statistics files
path = 'C:\Users\Dylan\Documents\GitHub\rcfbscraper\ESPN_Scraper\2013 Stats\';
file1 = [path, 'team-game-statistics_cfbstats.csv'];
% file1 = [path, 'play_TGS.csv'];
file2 = [path, 'team-game-statistics_new.csv'];
% Find shared stats
goodStats1 = [1:68];
% goodStats1 = [1:10, 36, 45:46, 56:57, 62:65];
% goodStats2 = [1:10, 18, 21:23, 27:30, 36:38, 45, 59:65, 69:70];
goodStats2 = [1:17, 69:70];
statVecTmp = max(min(goodStats1),min(goodStats2)):min(max(goodStats1),max(goodStats2));
statVec = zeros(size(statVecTmp));
for i = statVecTmp
    if sum(i==goodStats1) > 0 && sum(i==goodStats2) > 0
        statVec(length(statVec)+1) = i;
    end
end
statVec = statVec(statVec>0);
% Read in files
[dataNum1, dataStr1] = myxlsread(file1, 1, 1, 0, 0);
[dataNum2, dataStr2] = myxlsread(file2, 1, 1, 0, 0);
% Match games
data = zeros(max(size(dataNum1,1),size(dataNum1,1)),length(statVec),2);
for i = 1:size(data,1)
    tmpRow = dataNum1(i,statVec);
    teamCode = tmpRow(1);
    gameCode = tmpRow(2);
    matches = dataNum2(:,1)==teamCode & dataNum2(:,2)==gameCode;
    if sum(matches) == 1
        data(i,:,1) = tmpRow;
        data(i,:,2) = dataNum2(matches,statVec);
    elseif sum(matches) > 1
        fprintf('More than 1 game for\n  Team: %d\n  Game: %d\n',teamCode,gameCode);
    end
end

%% Display results
X = abs(data(:,:,1)-data(:,:,2));
figure(1); bar((sum(X==0)/length(X==0)));
title('No. of games differing');
Y = zeros(length(statVec),2);
for i = 1:length(statVec)
    if size(X(X(:,i)~=0,i),1) == 0
        Y(i,:) = 0;
    else
        Y(i,1) = mean(X(X(:,i)~=0,i));
        Y(i,2) = max(X(X(:,i)~=0,i));
    end
end
figure(2); bar(Y(:,1));
title('Mean of differing games');
figure(3); bar(Y(:,2));
title('Max of differing games');
figure(4); bar(100*Y(:,1)'./mean(data(:,:,1)));
title('Percent mean of differing games');
figure(5); bar(100*Y(:,2)'./mean(data(:,:,1)));
title('Percent max of differing games');
A = cell(length(statVec),1);
for i = 1:length(statVec)
    A{i} = strcat(num2str(i), '.....', dataStr1(statVec(i)));
    disp(A{i})
end

%% Sort by a stat
stat = input('Select stat to sort by: ');
[srtDif, difIdx] = sort(X(stat,:));
[srtData1,data1Idx] = sort(data(:,stat,1));
figure;
plot(srtData1,'-o');
hold on;
plot(data(data1Idx,stat,2),'-go')
hold off;