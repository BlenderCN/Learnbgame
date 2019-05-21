function Coords = MRToChamberCoords(TransformFile, FiducialsFile)

%=========== Get user to select files
if ~exist('TransformFile', 'var')
    [file, path] = uigetfile('*.mat', 'Select transform matrix file');
    if file == 0
        return;
    else
        TransformFile = fullfile(path, file);
    end
end
if ~exist('FiducialsFile','var')
    if exist('path','var')
        DefaultPath = path;
    else
        DefaultPath = cd;
    end
    [file, path] = uigetfile('*.fcsv', 'Select fiducial coordinates file',path);
    if file == 0
        return;
    else
        FiducialsFile = fullfile(path, file);
    end
end

%=========== Load transform matrix and reshape
load(TransformFile);
TransformMatrix             = [AffineTransform_double_3_3([1:3; 4:6; 7:9]), AffineTransform_double_3_3(10:12)];
TransformMatrix(end+1,:)    = [0,0,0,1];   

%=========== Convert transfrom matrix from LPS to RAS
Ras2lps     = [-1,-1,1,1];
Tform      	= TransformMatrix.*Ras2lps;
InvTform    = inv(Tform); 

%=========== Load coordinate data and tarnsform
fid     = fopen(FiducialsFile);
A       = textscan(fid, '%s%f%f%f%f%f%f%f%f%f%f%s%s%s', 'delimiter',',','Headerlines',3);
for f = 1:numel(A{1})
    Coords(f).Name          = A{12}{f};
    Coords(f).Description   = A{13}{f};
    Coords(f).TformFile     = TransformFile;
    Coords(f).TformMatrix   = Tform;
    Coords(f).XYZ_RAS       = [A{2}(f),A{3}(f),A{4}(f)];
    XYZ_Chamber             = Tform*[Coords(f).XYZ_RAS,1]';
    Coords(f).XYZ_Chamber   = -XYZ_Chamber(1:3)';
end

