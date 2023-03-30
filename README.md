
# TMM (Toucan Mod Manager) - (ALPHA v0.1.1)
### A mod manager for Kerbal Space Program 2.

![image](https://user-images.githubusercontent.com/1657477/228720734-053c42b8-ec57-4f24-b192-e8cfe51f3834.png)

## Description
This current version is the ALPHA release, what you see now is essentially a prototype which we will use to get player feedback. It utilises Python with the customtkinter and tkinter GUI frameworks. Due to limitations of this framework and the current codebase design, we will be abandoning this version and rewriting it in C# armed with the knowledge and feedback gained from this initial release.

Please note that there **WILL** be bugs, we are working on it.

## Disclaimer
***WE ARE NOT AFFILIATED WITH CKAN! You can find their project [here](https://github.com/KSP-CKAN/CKAN) (they also support [KSP2](https://github.com/KSP-CKAN/CKAN/pull/3797)).***
<br>
<br>
Currently the program is flagged by some antivirus solutions as a trojan, this is not the case and it is a false positive (definitely something a hacker would say). This is a well known issue with Pyinstaller and packaged python executables being incorrectly flagged as malware. We submitted this file for analysis to Microsoft and they have deemed it as "Not Malicious" and removed it from their threat database, if this is still flagged as a trojan for you and you are using Microsoft Defender please see [#16](https://github.com/Loki-Lokster/2KAN/issues/16).


## Installation:
1. Download the newest version of `2kan.zip` zip file from our [releases](https://github.com/Loki-Lokster/2KAN/releases) page.
2. Extract the zip (if you have Microsoft Defender you can run the `update_defender_definitions.bat` file as an administrator to ensure you have the latest malware definitions from Microsoft) and run `2KAN.exe`.
3. The application will automatically search common install locations for KSP2. If this does not work you can manually select the location using `Browse`. Ensure that a valid game version has been detected.
4. If this is your first time running the application, a dialog box will appear asking you to install SpaceWarp + BepInEx, select `Yes` as these are the modloaders.


## Contributions:
- Huge thanks to `@calebh210` for all the work and help on this project. 
- Shoutout to `IcyEcho249` and `dragonfyre23` for the name and inspiration for our logo.
- Thanks to Midjourney for the new and improved logo.


## F.A.Q
Q - **How do I remove all traces of mods from my game?**
<br>
A - Simply navigate to your KSP2 main install directory and delete the `BepInEx` folder.


Q - **I can't launch the program at all, I'm getting these weird errors?**
<br>
A - This is most likely because of your operating system, 2KAN has currently only been tested on Windows and due to it using Python and Pyinstaller to package the executable, this may be your issue. You can always download the source code directly from GitHub, install the requirements found in `requirements.txt` and run app.py (you **must** have Python installed for this to work).
