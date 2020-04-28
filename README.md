# Touchdesigner-Multi-Layer-Timeline

# Usage

### Shortcuts
- Alt+Scroll Wheel to zoom in/out
- Scroll-wheel or Shift+scroll-wheel can either scroll horizontally or vertically based on user settings

# Release History

## 0.73
### - Project Management
- Message box has been added to ask the user to save when they close the project or load a new one
- Auto-Save on exit removed
- Save backups is disabled temporarily
- This no longer uses TDJson and now uses a much simpler parameter reader/writer system. 

### - UI
- New camera system using range sliders.
- Zoom towards camera by holding alt+mousewheel.
- Various "Invert Scroll" parameters added to camera
- Removed camera settings from user preferences. 
- New Range Bar has been added. 
- Made more timecode readouts visible sooner at various timeline lengths.

## 0.7
## - Project Management

- New "Project" Page in the user settings allows you to select from any number of timelines in your project.
- Now supports saving and loading multiple timelines within a project.
- Supports external saving and loading of timeline projects.
- Timelines are stored as TDJson in storage for efficient load and unload
- Projects are saved to txt file as TDJson in a user designated path.
- Timeline projects are saved automatically as the toe file is saved.
- Timeline projects are backed up to a backup folder located next to the project.

- Dropdown Menu provides a list of all available timelines in your project

## - Cue Building

- New "Add Cue" button has been added on the setting page.
- Copy and Paste Multiple Cues.
- Full undo / redo support for deleting and adding cues.

## - UI

### - Cue Scheduling
- Full view of a 1 sec- 24 hour timeline
- Time icons along timeline provide clear visual of time position
- Time icon increments adjust as the camera zooms into the timeline

 ### - Snapping
 - Snap cues to other cues 
 - Snap cues to playhead
 - Snap cues or playhead to various levels of time increments based on zoom level
 
### - Timing
- Master timer sends all custom parameter data and timeline info
- Transport control via scrub bar and transport buttons
- Countdown and Countup to end of timeline

### - Interface
- Custom parameters offer an easy way to build a UI, or just use it as is.
- Ability to adjust look of layers, cues, and playhead
- Seperate pages for User Settings, Camera, and Project

### - Selection
-Multiselect
-Box select (Thanks Lucas!)

### - Callbacks
- Implimented a callback system via Alpha Moon Base's Callback Manager. 
