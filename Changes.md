## v1.4.0 (June 19, 2020)

### New Features
- Added new setting for imposing a size limit on log files.

### Changes
- Changed this mod's namespace from NeonOcean.Debug to NeonOcean.S4.Debug.
- Added icons to some mod interactions and interaction categories.

### Fixed bugs
- Fixed mod documentation links.

______________________________

### v1.3.0 (July 15, 2019)
### Changes
- All of Debug's interactions will now only show up when clicking on Sims instead of everything.

______________________________

## v1.2.0 (June 12, 2019)
### New Features
- Exceptions will now be logged for reports that are below the level 'exception', even though they aren't directly passed to the log functions.

### Changes
- Dumped logging mod settings, this also required the unification the continuous and burst log level and log interval settings.
- Updated setting dialogs to work with the new system in Main.

### Fixed Bugs
- Fixed a few problems with debug session files.
- Fixed problems with write failure notifications.
- Changing logging interval values no longer causes problems in writing log files.
- Log group folders are now created as they should have been, this previously prevented the usage of the write groups setting.

______________________________

## v1.1.0 (March 26, 2019)
 
- Log files now have a root element, as XML files are suppose to.
- Extra new line and indentation characters that are added to log files for readability are now commented out.
- Users will now be notified of errors that prevented logging new reports.
- In-game notifications will now appear telling you when an update is available.
- Interactions now exist that can direct you to web pages relevant to this mod, such as the documentation.
- Addition and removal of this mod are can now be facilitated through an installer or uninstaller. These currently are only usable on windows computers.

______________________________
 
## v1.0.0 (July 26, 2018)
 - Initial release