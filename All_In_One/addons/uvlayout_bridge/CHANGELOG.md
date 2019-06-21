# Changelog
All notable changes to this project will be documented in this file.

ChangeLog
---------
## [0.6.5] - 2019-02-26
### Fixed
- Error caused by items inside collection (bl 2.80)
- Non Mesh types where added when "selection only" was off

## [0.6.4] - 2019-01-12
### Changed
- Popup menu doesnt have 2 buttons at the bottom, makes it more clear what export is
- Label was replace due to new WM menu
- Export button has more logical label

### Fixed
- Apply modifier for bl 2.80

### Added
- Undo for export operation in case of error or malfunction

## [0.6.3] - 2019-01-12
### Fixed
- Issue with swapped keymap code

### Added
- Missing "skip localview" in popup menu
- Support for bl 2.80, see bl2.80_deb branch

## [0.6.2] - 2018-09-22
### Changed
- Added "skip localview check", can give errors so skip is added

## [0.6.1] - 2018-09-22
### Fixed
- Set config read/writing, errors occurred reading and writing file
- Keymap name errors

## [0.6] - 2017-12-16
### Fixed
- Set config file, errors occurred with custom path.
- WM call menu, now resizes when automation is checked.

## [0.5] - 2017-12-15
### Added
- OSX support for load options
- Extra load options (Weld UVs, Clean, Detach Flipped UVs)
- Checker for export from local view (is not supported)
- Automation, automatic packing and automatic save and return
- Hotkeys for popup menu (for clean workflow)
- Hotkeys to add-on panel for quick acces
- Quick Export shortcut (quick exports according to last settings)
- Add-on preferences saving options. On restart all settings will be loaded
- Custom export folder. Useful for when errors occur and file needs to be saved, quick access to files.

## [0.4] - 2017-12-07
### Added
- Create backup when ‘Apply Modifier’ is added.
- Option to export all visible objects, hidden and layers OFF won’t be exported.

## [0.3] - 2017-12-05
### Added
- Apply modifier option

## [0.2]
### Added
- Functionality with better selection of objects
- Selection only option
- Checker for selection only
- OSX support

## [0.1]
### Added
- Initial start plugin by Titus

## Notes
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[0.6.5]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6.5_2.80
[0.6.4]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6.4
[0.6.3]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6.3
[0.6.2]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6.2
[0.6.1]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6.1
[0.6]:https://github.com/schroef/uvlayout_bridge/releases/tag/v0.6
