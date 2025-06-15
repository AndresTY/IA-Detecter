[Setup]
AppName=IADetecter_Server
AppVersion=1.0
AppPublisher=Andres Ducuara
DefaultDirName={localappdata}\IADetecter_Server
DefaultGroupName=IADetecter_Server
OutputDir=.
OutputBaseFilename=IADetecter_Server_Setup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\server.exe
Uninstallable=yes
LicenseFile=license.txt
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=..\icono.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\server.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "license.txt"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "README.txt"; DestDir: "{app}"; Flags: isreadme
Source: "..\icono.ico"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\IADetecter_Server"; Filename: "{app}\server.exe"; Comment: "Run IADetecter"; IconFilename: "{app}\icono.ico"
Name: "{group}\Desinstalar IADetecter_Server"; Filename: "{uninstallexe}"; IconFilename: "{app}\icono.ico"
Name: "{userdesktop}\IADetecter_Server"; Filename: "{app}\server.exe"; Tasks: desktopicon; IconFilename: "{app}\icono.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Aditionals Icons:"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  PortPage: TInputQueryWizardPage;
  DetectedIP: String;

function GetLocalIP: string;
var
  TempFile: string;
  Lines: TArrayOfString;
  I, PosIni: Integer;
  FoundInterface: Boolean;
  Line, IP: string;
  ExitCode: Integer;
begin
  Result := '';
  TempFile := ExpandConstant('{tmp}\ipconfig_output.txt');

  if Exec('cmd.exe', '/C ipconfig > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
  begin
    if LoadStringsFromFile(TempFile, Lines) then
    begin
      FoundInterface := False;
      for I := 0 to GetArrayLength(Lines) - 1 do
      begin
        Line := Lines[I];

        if (Pos('Adaptador de Ethernet Ethernet', Line) > 0) or (Pos('Ethernet adapter Ethernet', Line) > 0) or
           (Pos('Adaptador de LAN inalámbrica Wi-Fi', Line) > 0) or (Pos('Wireless LAN adapter Wi-Fi', Line) > 0) then
        begin
          FoundInterface := True;
        end
        else if (FoundInterface and ((Pos('IPv4', Line) > 0) or (Pos('Dirección IPv4', Line) > 0))) then
        begin
          PosIni := Pos(':', Line);
          if PosIni > 0 then
          begin
            IP := Trim(Copy(Line, PosIni + 1, Length(Line)));
            if IP <> '' then
            begin
              Result := IP;
              Break;
            end;
          end;
        end
        else if (FoundInterface and (Trim(Line) = '')) then
        begin
          FoundInterface := False;
        end;
      end;
    end;
  end;

  if Result = '' then
    Result := '127.0.0.1';
end;

procedure InitializeWizard;
begin
  DetectedIP := GetLocalIP;

  PortPage := CreateInputQueryPage(wpSelectDir,
    'Port Configuration',
    'Enter the port to be used by the server',
    '');

  PortPage.Add('Port:',False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  IniFile: String;
begin
  if CurStep = ssPostInstall then
  begin
    IniFile := ExpandConstant('{app}\config.ini');
    SaveStringToFile(IniFile,
      '[Settings]' + #13#10 +
      'host=' + DetectedIP + #13#10 +
      'port=' + PortPage.Values[0] + #13#10,
      False);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  PortStr: String;
  PortNum: Integer;
begin
  Result := True;

  if CurPageID = PortPage.ID then
  begin
    PortStr := Trim(PortPage.Values[0]);
    if PortStr = '' then
    begin
      MsgBox('Please enter a port number.', mbError, MB_OK);
      Result := False;
    end
    else
begin
  PortNum := StrToIntDef(PortStr, -1);
  if PortNum <= 0 then
  begin
    MsgBox('The port must be a valid integer.', mbError, MB_OK);
    Result := False;
  end;
end;
  end;
end;
