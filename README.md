# 112osu
CMU-112 Term Project: osu!

ALL BEATMAPS TAKEN FROM osu.ppy.sh
ALL SKIN ASSETS TAKEN FROM RyuK's osu! skin page: https://github.com/Mizaruuu/osu-RyuK-s-super-cool-skins/blob/master/Skins.md (specifically "- alfie_fancy_dt" and "- ryan fancy edit")

Description: In essence, my project, 112osu!, is a copy of the real game osu! made by Dean "ppy" Herbert. Specifically, 112osu! allows users to import real community-made osu! 
standard maps from osu.ppy.sh. This allows users to build a catalog of their favorite maps to play at any time. 

How to run: All users need to do for importing is download any osu! map from osu.ppy.sh and put the .osz file in the maps folder. Then, once main.py is run, the map will be imported
and the user will be able to play it. As for controls, the user can use any key/mouse input to pass the starting screen. They are then met by a map selector, which can be cycled through
with the 'Up' and 'Down' arrows. If the music from each map gets to be annoying, the user can press 'p' to pause and unpause the music. Once the user finds a map they want to play, they 
must then press 'Space' to confirm their map choice. Once in the map, the user can press any key to start the map. The keys 'a' and 's', case insensitive, are the default keys for clicking the circles. 
If the user doesn't want to play the map anymore, they can press 'Escape' to return to the map selection screen.

Libraries: Besides 15-112 graphics and pygame, no external modules/libraries/files need to be installed

No shortcut commands exist

Common bugs: Many bugs come from importing, especially with being unable to detect a map's song or background file. Every song/background file is tilted the beatmap's title,
which can be found inside any of the versions inside the beatmap .zip. If the title or extension doesn't match up due to special characters and/or formats, the user must manually
edit the names of the error files so that they can be detected.

