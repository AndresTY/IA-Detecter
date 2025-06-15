[Setup]
AppName=IADetecter
AppVersion=1.0
AppPublisher=Andres Ducuara
DefaultDirName={localappdata}\IADetecter
DefaultGroupName=IADetecter
OutputDir=.
OutputBaseFilename=IADetecter_Setup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\script.exe
Uninstallable=yes
LicenseFile=license.txt
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=..\icon.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\script.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "license.txt"; DestDir: "{app}"; Flags: onlyifdoesntexist 
Source: "README.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\IADetecter"; Filename: "{app}\script.exe"; Comment: "Ejecutar IADetecter"
Name: "{group}\Desinstalar IADetecter"; Filename: "{uninstallexe}"
Name: "{userdesktop}\IADetecter"; Filename: "{app}\script.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un ícono en el escritorio"; GroupDescription: "Iconos adicionales:"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  PasswordPage: TInputQueryWizardPage;
  AgreementPage: TWizardPage;

const
  DefaultLaws = 'The use of tools based on Artificial Intelligence and/or Large Language Models (LLMs) in the preparation of academic work or activities is strictly restricted. Their use without explicit prior authorization will be considered a form of academic dishonesty, equivalent to plagiarism, and will be subject to the corresponding sanctions in accordance with institutional regulations.';

procedure InitializeWizard;
begin
  AgreementPage := CreateCustomPage(wpLicense, 'License Agreement', 
    'Please read the license agreement carefully.');

  PasswordPage := CreateInputQueryPage(wpSelectDir, 
    'Configure Application', 
    'Enter configuration parameters for IADetecter.', '');

  PasswordPage.Add('password:', True);     // index 0
  PasswordPage.Add('IP:', False);            // index 1
  PasswordPage.Add('port:', False);        // index 2
  PasswordPage.Add('Listener:', False);      // index 3
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  IniFile: String;
begin
  if CurStep = ssPostInstall then
  begin
    IniFile := ExpandConstant('{app}\config.ini');

    if PasswordPage.Values[0] <> '' then
    begin
      SaveStringToFile(IniFile, 
        '[Settings]' + #13#10 +
        'password=' + PasswordPage.Values[0] + #13#10 +
        'host=' + PasswordPage.Values[1] + #13#10 +
        'port=' + PasswordPage.Values[2] + #13#10 +
        'listener=' + PasswordPage.Values[3] + #13#10 +
        'laws=' + DefaultLaws + #13#10,
        False);
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  PortNum: Integer;
begin
  Result := True;

  if CurPageID = PasswordPage.ID then
  begin
    if Trim(PasswordPage.Values[0]) = '' then
    begin
      MsgBox('Please enter a password.', mbError, MB_OK);
      Result := False;
    end
    else if Trim(PasswordPage.Values[1]) = '' then
    begin
      MsgBox('Please enter an IP address.', mbInformation, MB_OK);
      Result := False;
    end
    else if Trim(PasswordPage.Values[2]) = '' then
    begin
      MsgBox('Please enter a port number.', mbInformation, MB_OK);
      Result := False;
    end
    else
    begin
      PortNum := StrToIntDef(PasswordPage.Values[2], -1);
      if PortNum <= 0 then
      begin
        MsgBox('The port must be a valid integer.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;
