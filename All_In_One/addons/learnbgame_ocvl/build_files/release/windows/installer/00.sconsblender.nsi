;
;
; OCVL Self-Installer for Windows (NSIS - http://nsis.sourceforge.net)
;

SetCompressor /SOLID lzma

Name "OpenCV Laboratory [VERSION]"

RequestExecutionLevel admin

!include "MUI.nsh"
!include "WinVer.nsh"
!include "FileFunc.nsh"
!include "WordFunc.nsh"
!include "nsDialogs.nsh"
!include "x64.nsh"

!define MUI_ABORTWARNING

!define MUI_WELCOMEPAGE_TEXT  "This wizard will guide you through the installation of OpenCV Laboratory. It is recommended that you close all other applications before starting Setup."
!define MUI_WELCOMEFINISHPAGE_BITMAP "[RELDIR]\installer\01.installer.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP  "[RELDIR]\installer\00.header.bmp"
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_FINISHPAGE_RUN "$INSTDIR\OpenCVLaboratory.exe"
!define MUI_CHECKBITMAP "[RELDIR]\00.checked.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "[RELDIR]\installer\01.installer.bmp"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "[DISTDIR]\copyright.txt"
!insertmacro MUI_PAGE_COMPONENTS
    
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
  
!insertmacro MUI_UNPAGE_WELCOME
UninstPage custom un.OptionalRemoveConfig un.OptionalRemoveConfigOnLeave
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro Locate
!insertmacro VersionCompare


Icon "[RELDIR]\installer\00.installer.ico"
UninstallIcon "[RELDIR]\installer\00.installer.ico"

;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"
    
;--------------------------------
;Language Strings

  ;Description
  LangString DESC_InstallFiles ${LANG_ENGLISH} "Copy all required files to the application folder."
  LangString DESC_StartMenu ${LANG_ENGLISH} "Add shortcut items to the Start Menu. (Recommended)"
  LangString DESC_DesktopShortcut ${LANG_ENGLISH} "Add a shortcut to OpenCV Laboratory on your desktop."
  LangString DESC_BlendRegister ${LANG_ENGLISH} "OpenCV Laboratory can register itself with .blend files to allow double-clicking from Windows Explorer, etc."
;--------------------------------
;Data

Caption "OpenCV Laboratory [VERSION] Installer"
OutFile "[DISTDIR]\..\OCVL-[VERSION]-windows[BITNESS].exe"
InstallDir $INSTDIR ; $INSTDIR is set inside .onInit
BrandingText "OpenCV Laboratory Blog | https://kube.pl/index.php/en/"
ComponentText "This will install OpenCV Laboratory [VERSION] on your computer."

VIAddVersionKey "ProductName" "OpenCV Laborator"
VIAddVersionKey "CompanyName" "http://www.teredo.tech/"
VIAddVersionKey "FileDescription" "Software to easy manage OpenCV content."
VIAddVersionKey "FileVersion" "[SHORTVERSION].0.0"

VIProductVersion "[SHORTVERSION].0.0"

DirText "Use the field below to specify the folder where you want OpenCV Laboratory to be copied to. To specify a different folder, type a new name or use the Browse button to select an existing folder."

SilentUnInstall normal

Var SHORTVERSION ; This is blender_version_decimal() from path_util.c
Var OCVLCONFIG
Var REMOVECONFIG

; Custom controls
Var HWND

Var HWND_KEEPCONFIG
Var HWND_REMOVECONFIG

Function .onInit
  ClearErrors
  StrCpy $SHORTVERSION "[SHORTVERSION]"

  ${If} ${RunningX64}
    ${If} "[BITNESS]" == "32"
      StrCpy $INSTDIR "$PROGRAMFILES32\Teredo\OpenCV Laboratory" ; Can't use InstallDir inside Section
    ${ElseIf} "[BITNESS]" == "64"
      StrCpy $INSTDIR "$PROGRAMFILES64\Teredo\OpenCV Laboratory"
    ${EndIf}
  ${Else}
    StrCpy $INSTDIR "$PROGRAMFILES\Teredo\OpenCV Laboratory"
  ${EndIf}
FunctionEnd

Function un.onInit
  SetShellVarContext current
  StrCpy $OCVLCONFIG "$APPDATA\Teredo\OpenCV Laboratory"
  SetShellVarContext all
FunctionEnd

Function un.OptionalRemoveConfig
  nsDialogs::Create /NOUNLOAD 1018
  Pop $HWND

  ${If} $HWND == error
    Abort
  ${EndIf}

  ${NSD_CreateRadioButton} 0 50 100% 12u "Keep configuration files, autosaved .blend files and installed addons (recommended)"
  Pop $HWND_KEEPCONFIG
  ${NSD_CreateRadioButton} 0 80 100% 12u "Remove all files, including configuration files, autosaved .blend files and installed addons"
  Pop $HWND_REMOVECONFIG

  SendMessage $HWND_KEEPCONFIG ${BM_SETCHECK} 1 0

  nsDialogs::Show

FunctionEnd

Function un.OptionalRemoveConfigOnLeave
  ${NSD_GetState} $HWND_REMOVECONFIG $R0
  ${If} $R0 == "1"
    StrCpy $REMOVECONFIG "1"
  ${Else}
    StrCpy $REMOVECONFIG "0"
  ${EndIf}
FunctionEnd


Section "OpenCV Laborator [VERSION] (required)" InstallFiles
  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  ; The contents of OpenCV Laborator installation root dir
  [ROOTDIRCONTS]

  ; All datafiles (python, scripts, datafiles)
  [DODATAFILES]

  SetOutPath $INSTDIR
  ${If} ${RunningX64}
    SetRegView 64
  ${EndIf}
  ; Write the installation path into the registry
  WriteRegStr HKLM "SOFTWARE\Teredo" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "SOFTWARE\Teredo" "ShortVersion" "[SHORTVERSION]"
  ; Write the uninstall keys for Windows
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "DisplayName" "OpenCV Laboratory"
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "Publisher" "Teredo"
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "URLInfoAbout" "http://www.kube.pl/"
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "DisplayVersion" "[VERSION]"
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "DisplayIcon" "$INSTDIR\OpenCVLaboratory.exe"
  WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory" "NoRepair " 1
  WriteUninstaller "uninstall.exe"

SectionEnd

Section "Add Start Menu Shortcuts" StartMenu
  SetShellVarContext all
  CreateDirectory "$SMPROGRAMS\Teredo\OpenCV Laboratory\"
  CreateShortCut "$SMPROGRAMS\Teredo\OpenCV Laboratory\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\Teredo\OpenCV Laboratory\OpenCVLaboratory.lnk" "$INSTDIR\OpenCVLaboratory.exe" "" "$INSTDIR\OpenCVLaboratory.exe" 0
  CreateShortCut "$SMPROGRAMS\Teredo\OpenCV Laboratory\Readme.lnk" "$INSTDIR\readme.html" "" "" 0
  CreateShortCut "$SMPROGRAMS\Teredo\OpenCV Laboratory\Copyright.lnk" "$INSTDIR\Copyright.txt" "" "$INSTDIR\copyright.txt" 0
  CreateShortCut "$SMPROGRAMS\Teredo\OpenCV Laboratory\GPL-license.lnk" "$INSTDIR\GPL-license.txt" "" "$INSTDIR\GPL-license.txt" 0
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)' ; refresh icons
SectionEnd

Section "Add Desktop Shortcut" DesktopShortcut
  CreateShortCut "$DESKTOP\OpenCVLaboratory.lnk" "$INSTDIR\OpenCVLaboratory.exe" "" "$INSTDIR\OpenCVLaboratory.exe" 0
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)' ; refresh icons
SectionEnd

Section "Open .blend files with OpenCV Laboratory" BlendRegister
  ExecWait '"$INSTDIR\OpenCVLaboratory.exe" -r'
SectionEnd

UninstallText "This will uninstall OpenCV Laboratory [VERSION], and all installed files. Hit 'Uninstall' to continue."

Section "Uninstall"
  ; Remove registry keys
  ${If} ${RunningX64}
    SetRegView 64
  ${EndIf}

  ReadRegStr $SHORTVERSION HKLM "SOFTWARE\Teredo" "ShortVersion"
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\OpenCVLaboratory"
  DeleteRegKey HKLM "SOFTWARE\Teredo"
  DeleteRegKey HKCR ".blend"
  DeleteRegKey HKCR "blendfile"
  DeleteRegKey HKCR "CLSID\{D45F043D-F17F-4e8a-8435-70971D9FA46D}"
  SetShellVarContext all

  ; Remove files
  [DELROOTDIRCONTS]
  [DELDATAFILES]
  [DELDATADIRS]

  Delete "$INSTDIR\uninstall.exe"

  ${If} $REMOVECONFIG == "1"
    RMDir /r "$OCVLCONFIG\$SHORTVERSION"
  ${Endif}

  ; Remove install directory if it's empty
  RMDir $INSTDIR
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Teredo\OpenCV Laboratory\*.*"
  Delete "$DESKTOP\OpenCVLaboratory.lnk"
  ; Remove all link related directories and files
  RMDir "$SMPROGRAMS\Teredo\OpenCV Laboratory"
  RMDir "$SMPROGRAMS\Teredo"

  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)' ; Refresh icons
SectionEnd

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${InstallFiles} $(DESC_InstallFiles)
  !insertmacro MUI_DESCRIPTION_TEXT ${StartMenu} $(DESC_StartMenu)
  !insertmacro MUI_DESCRIPTION_TEXT ${DesktopShortcut} $(DESC_DesktopShortcut)
  !insertmacro MUI_DESCRIPTION_TEXT ${BlendRegister} $(DESC_BlendRegister)
!insertmacro MUI_FUNCTION_DESCRIPTION_END