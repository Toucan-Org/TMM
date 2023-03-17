#### TODO LIST:
Here are just a few things i can think of that need to be fixed/added for now:

- ~~Compact modlist mode (make the height of the mods in modlist smaller and less verbose)~~
- Time played log (can track this in the config or some other log file i guess)
- ~~The installation method could probably do with a rework, I'm currently just downloading the mod as a zip, extracting it into the main KSP2 directory and this seems to work so far. Uninstalling is more of an issue because then I need to keep track of all the files and dirs that were extracted there in the first place. Currently i just search the BepInEx and SpaceWarp plugin folders for the mod name (this can be unreliable).~~
- A way to toggle mods (although once you download a mod its stored in cache for quicker installation second time around, so this isnt a high priority for now)
- The way the GUI classes interact with each other feels a bit sloppy. I think a better method would be creating some kind of messaging system that allows different GUI functions to trigger elements or functions from another class. Any ideas?
- Config file is also a bit of a mess at the moment. Sometimes saves sometimes doesn't.
- Some of the functions could definitely be renamed or broken into more useful subroutines.
- Add a warning to an installed mod if the version you're about to install does not match the current games version.
- An option to select "Update All" in Installed Mods instead of one by one.
- ~~An internal function that once a day or whenever the program boots up, reaches out to our github page to see if there's been a new release and if so then notify the user that a new version is available.~~
- Add a filter panel (spacedock API already has some filtering options but its just as easy to do it within python, either way works).
- A way to resize the modlist panel and control panel separation.
- A new logo or at least updated.
- Move print statements to a logger (longterm once things are more stable, for now we're gonna need all the print statements we can use lol)
- Also need to work on how to package the exe, Auto py to exe does work but need to do some tweaking as some things break with it.



# 2KAN (WIP)
### A mod manager for Kerbal Space Program 2.

#### Installation:
1. Download the `2kan.exe` file from our newest release page.
2. Run the application, it will automatically search common install locations for KSP2. If this does not work you can manually select the location using `Browse`. Ensure that a valid game version has been detected.
3. If this is your first time running the application, search for BepInEx + SpaceWarp and install this before installing any other mods.


#### Contributions:
- Huge thanks to `@calebh210` for all the 
- Shoutout to `IcyEcho249` for the name 2KAN and inspiration for our logo.