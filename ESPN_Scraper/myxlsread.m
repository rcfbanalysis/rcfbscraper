% file, getNum, getStr, rmNumHead, rmNumStr
function [out, varargout] = myxlsread(file, getNum, getStr, rmNumHead, rmStrHead)
% Read in file
fprintf('Loading %s... ', file);
[num str] = xlsread(file);
% Remove headers
if rmNumHead
    num = num(2:end,:);
end
if rmStrHead
    str = str(2:end,:);
end
% Grab desired data
if getNum && getStr
    out = num;
    varargout{1} = str;
elseif getNum
    out = num;
elseif getStr
    out = str;
else
    warning('MATLAB:noDataRequested','No data was selected!');
end
fprintf('done\n');
end