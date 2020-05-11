# TD-MTL

# Description:

A general purpose multi-layer timeline system, TD-MTL's main goal is to provide the TouchDesigner community with a timeline system for all types of work. With the general purpose concept in mind, the system can be customized in many ways. Whether you want to time out OSC cues, video media compositing, or external tox presets, our system can assist you.

# Installation: 
Within the release folder you will find a self contained tox file. Bring that into your project and make it an external tox. You don't want this to be saved within your project because whenever you save it can take a while. 
To test it out, check the examples folder for media bins and video compositing systems. (coming soon)


# Usage:
Because this tool is meant to be open to a variety of projects, it's not 100% ready to go out of the box. The timeline itself just outputs timing and cue information. To make it functional out of the box, you can look at the "Examples" folder which includes video players and media bins.

TD-MTL provides a variety of cue types, such as "Media", "Tox", "TCP/IP", and more. A user can also build custom cue types that can store other data to assist in triggering all types of cues. With this openness in mind, we may not provide systems to fire all these types of cues. Out examples are meant to assist in the development of customized solutions.

See the wiki for how to build a custom Timeline System.

### Some useful pages from the wiki- 
[Keyboard Shortcuts](https://github.com/franklin113/Touchdesigner-Multi-Layer-Timeline/wiki/Keyboard-Shortcuts)

# Contributing:
The most useful types of contributions would be sharing your custom media bins and players for our examples folder. If you find a cool way to use it in your project, any demos or examples would be awesome.

Any bug reports, issue tracking, feature requests, and documentation assistance would also be fantastic. 

# Credits:
Tim Franklin

Brian Alexander

# License:
TDOO



# Old documentation below, will get put into a wiki.


# Usage

## Shortcuts

### Camera Shortcuts
- Alt+Scroll-wheel to zoom in/out
- Scroll-wheel or Shift+scroll-wheel can either scroll horizontally or vertically based on user settings

### Timeline Editing Shortcuts
While Dragging A Cue --
- Ctrl+Alt - snaps to playhead
- Ctrl - snaps to certain time increments

With A Cue Selected --
- Delete - deletes the selected cues
- Ctrl+c - copies the selected cues and pastes them, starting at the playhead.
- Ctrl+z - Undo After deleting or adding a cue
# Release History

## 0.74 
### - Snapping
- Selected cues can now be snapped to the front or back of other cues

### - Timing
- A new timing system has been put in place by Brian Alexander. 
- Preload pulse can be received prior to every cue
- A master parellel timer can be accessed for playback and triggering

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
