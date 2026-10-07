; ---------------------------------------------------------------------------
; virusShare - Inno Setup installer script (Phase 6)
;
; Build (called by build_windows.bat, or manually):
;
;     ISCC.exe installer\virusShare.iss
;
; Input : dist\virusShare\*            (PyInstaller onedir build, virusShare.spec)
; Output: dist\virusShare-Setup.exe
;
; Version strings default to core/constants.py (APP_VERSION = 1.0.0) and may be
; overridden from the command line:
;     ISCC.exe /DMyAppVersion=1.2.3 installer\virusShare.iss
; ---------------------------------------------------------------------------

#define MyAppName "virusShare"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppVersionFull "1.0.0.0"
#define MyAppPublisher "virusShare"
#define MyAppURL "https://github.com/ratneshsahu9098/VIRUSSHARE"
#define MyAppExeName "virusShare.exe"

[Setup]
AppId={{9B7A4C2E-5D31-4F8A-9E60-2C4D8F1A7B53}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
InfoAfterFile=..\README.md

; The *installer* elevates (per-machine install into Program Files); the
; application itself carries an asInvoker manifest and never needs admin.
PrivilegesRequired=admin

; Uninstaller
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Version resource of the setup exe itself
VersionInfoVersion={#MyAppVersionFull}
VersionInfoProductVersion={#MyAppVersionFull}
VersionInfoTextVersion={#MyAppVersionFull}
VersionInfoProductTextVersion={#MyAppVersion}
VersionInfoDescription=Secure Windows File Sharing Application
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}

; Output
OutputDir=..\dist
OutputBaseFilename=virusShare-Setup
SetupIconFile=..\resources\icons\virusShare.ico
UninstallFilesDir={app}

; Compression
Compression=lzma2/max
SolidCompression=yes
LZMANumBlockThreads=4

; Presentation
WizardStyle=modern
DisableWelcomePage=no

; Platform
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

; Running app: ask to close it before upgrading/removing
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Full PyInstaller onedir tree: virusShare.exe + _internal\*
Source: "..\dist\virusShare\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    Comment: "Secure Windows file sharing over your local network"
Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent

[Code]
function InitializeUninstall(): Boolean;
begin
  Result := True;
  { App data (%LOCALAPPDATA%\virusShare: settings, identity, history.db,
    logs) is deliberately kept so a reinstall restores the same identity. }
end;
