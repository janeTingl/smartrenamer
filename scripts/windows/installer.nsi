; SmartRenamer Windows 安装程序脚本
; 使用 NSIS (Nullsoft Scriptable Install System) 创建

;--------------------------------
; 包含现代UI
!include "MUI2.nsh"
!include "x64.nsh"

;--------------------------------
; 通用设置

; 应用程序名称和版本
!define APP_NAME "SmartRenamer"
!define APP_VERSION "0.6.0"
!define APP_PUBLISHER "SmartRenamer Team"
!define APP_URL "https://github.com/smartrenamer/smartrenamer"
!define APP_EXE "SmartRenamer.exe"

; 安装程序名称
Name "${APP_NAME} ${APP_VERSION}"
OutFile "../../dist/SmartRenamer-${APP_VERSION}-Windows-Setup.exe"

; 默认安装目录
InstallDir "$PROGRAMFILES64\${APP_NAME}"

; 从注册表获取安装目录（如果已安装）
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"

; 请求管理员权限
RequestExecutionLevel admin

; 安装程序图标
; Icon "..\..\assets\icon.ico"

;--------------------------------
; 界面设置

; 现代UI配置
!define MUI_ABORTWARNING
!define MUI_ICON "..\..\assets\icon.ico"
!define MUI_UNICON "..\..\assets\icon.ico"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME

; 许可协议页面
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"

; 组件选择页面
!insertmacro MUI_PAGE_COMPONENTS

; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY

; 安装文件页面
!insertmacro MUI_PAGE_INSTFILES

; 完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "运行 ${APP_NAME}"
!insertmacro MUI_PAGE_FINISH

; 卸载确认页面
!insertmacro MUI_UNPAGE_CONFIRM

; 卸载进度页面
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

;--------------------------------
; 版本信息

VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileDescription" "${APP_NAME} 安装程序"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "LegalCopyright" "© 2024 ${APP_PUBLISHER}"

;--------------------------------
; 安装器段落

Section "${APP_NAME} (必需)" SecMain

  SectionIn RO
  
  ; 设置输出路径到安装目录
  SetOutPath $INSTDIR
  
  ; 复制主要文件
  File /r "..\..\dist\${APP_EXE}"
  File /r "..\..\dist\_internal"
  File "..\..\LICENSE"
  File "..\..\README.md"
  
  ; 写入注册表信息
  WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
  
  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; 写入卸载信息到注册表
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

SectionEnd

; 可选段落：桌面快捷方式
Section "桌面快捷方式" SecDesktop

  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"

SectionEnd

; 可选段落：开始菜单快捷方式
Section "开始菜单快捷方式" SecStartMenu

  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\卸载.lnk" "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
; 描述

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "安装 ${APP_NAME} 的核心文件（必需）"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "在桌面上创建快捷方式"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "在开始菜单中创建快捷方式"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; 卸载器段落

Section "Uninstall"

  ; 删除注册表键
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"

  ; 删除文件和目录
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR\_internal"
  RMDir "$INSTDIR"

  ; 删除快捷方式
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\卸载.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

SectionEnd

;--------------------------------
; 函数

Function .onInit
  ; 检查是否已安装
  ReadRegStr $R0 HKLM "Software\${APP_NAME}" "Install_Dir"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APP_NAME} 已经安装。$\n$\n点击 `确定` 继续安装（将覆盖现有版本），或点击 `取消` 退出安装。" \
    IDOK done
  Abort
  
  done:
FunctionEnd
