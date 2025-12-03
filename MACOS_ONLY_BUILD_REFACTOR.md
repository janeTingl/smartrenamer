# macOS-Only Build Scripts Refactoring

## Overview

The local build tooling has been refactored to focus exclusively on macOS. This change simplifies the build scripts by removing Windows and Linux specific code, making them macOS-only with clear error messages for unsupported platforms.

## Changes Made

### 1. scripts/build.py - macOS-Only Build Script

**Changes:**
- Added platform check at module level to fail fast if not running on macOS (Darwin)
- Removed Windows UTF-8 encoding configuration (lines 17-27)
- Updated docstring to reflect macOS-only support
- Simplified `install_dependencies()` method by removing Windows/Linux dependency handling
- Removed `create_windows_installer()` method entirely
- Removed `create_linux_appimage()` method entirely
- Simplified `create_installer()` method to only call `create_macos_dmg()`
- Updated `generate_checksums()` to mention macOS outputs specifically
- Updated all logging messages to reflect macOS-only status
- Updated `Builder` class to hardcode platform as 'darwin'

**Key Features:**
- Exits with clear error message when run on non-macOS platforms
- Streamlined build flow: check environment → install deps → generate icons → build .app → create DMG → generate checksums
- All messages and logs reference macOS specifically

### 2. build.sh - macOS-Only Shell Entry Point

**Changes:**
- Updated header comment to state "仅支持 macOS" (macOS only)
- Added platform check using `uname -s` to verify Darwin before proceeding
- Updated all echo messages to reference macOS
- Added output information about generated files (.app and .dmg)
- Continues to chain into `scripts/build.py --clean`

**Key Features:**
- Checks for macOS platform before any operations
- Exits with clear error message on non-macOS platforms
- Provides informative success messages

### 3. build.bat - Windows Batch File

**Changes:**
- **REMOVED** - No Windows batch entry point remains

## Acceptance Criteria

✅ **Platform Detection:**
- Running `scripts/build.py` on non-macOS platforms exits immediately with error:
  ```
  错误: 此构建脚本仅支持 macOS 平台
  当前平台: <detected platform>
  请在 macOS 系统上运行此脚本
  ```

✅ **build.sh Behavior:**
- Running `build.sh` on non-macOS platforms exits with clear error before executing Python script
- Error message clearly states macOS-only requirement

✅ **No Windows Entry Point:**
- `build.bat` file has been removed from the repository

✅ **macOS Functionality:**
- On macOS systems, scripts still produce:
  - `SmartRenamer.app` bundle
  - `SmartRenamer-macOS.dmg` disk image
  - `checksums.txt` with SHA256 hashes

## Testing

Run the test script on non-macOS platforms:
```bash
bash test_build_scripts.sh
```

Expected output:
- Both scripts detect non-macOS platform
- Clear error messages displayed
- build.bat confirmed removed
- Scripts exit with error code 1

On macOS:
```bash
./build.sh
# or
python3 scripts/build.py --clean
```

Expected output:
- Full build process executes
- Generates .app bundle and .dmg file
- Checksums generated for macOS outputs

## Files Modified

1. `scripts/build.py` - Refactored to macOS-only (283 lines)
2. `build.sh` - Updated with macOS check (47 lines)
3. `build.bat` - DELETED

## Breaking Changes

⚠️ **Windows Users:**
- Can no longer use local build scripts
- Must use GitHub Actions or cross-platform CI/CD
- Docker builds still available as alternative

⚠️ **Linux Users:**
- Can no longer use local build scripts
- Must use GitHub Actions or cross-platform CI/CD
- Docker builds still available as alternative

## Migration Guide

For Windows/Linux developers:
1. Use GitHub Actions for building releases
2. Use Docker for local development and testing
3. Use macOS VM/hardware for local builds if needed

## Related Documentation

- `PACKAGING_GUIDE.md` - May need updates to reflect macOS-only local builds
- `README.md` - Build instructions already focus on macOS
- `.github/workflows/build-release.yml` - CI/CD still supports all platforms

## Version

This refactoring is part of the macOS-focused build tooling initiative.
Created: 2024-12-03
