EXTRACTORS
Author: A.J. Ristino
Original: 11/3/2025
Rebuild: 3/13/2026

PURPOSE:
This was a component of a project undertaken by myself, Lucas Vinet, Enjin Wang, 
and Tyler Bar-Ness. We fully produced and localized a 5-minute long visual novel
titled THE LAST HOUSE into four languages: JA, ES, CN, and DE. The scripts in this
folder are how I (A.J.) was able to extract all of the translation text from the 
attached .rpy templates—which are essentially script items the .rpy framework uses
in order to insert translations into a completed game download.

The contents of this folder were our bread and butter, and without these 
implementations, the entire project would've fallen flat. This is, for all intents
and purposes, the opening link of an automated pipeline we built to complete the
project and complete the final game release.

CONTAINED SCRIPTS:

extract_script.py — works with script.rpy, is formatted to work SPECIFICALLY WITH script.py
Inputs: console command: python3 extract_script.py
Outputs: a txt file of extracted script items attached to a numerical reference (for reinsertion)

extract_settings.py — works with options.rpy, screens.rpy, and common.rpy, SPECIFICALLY
Inputs: console command: python3 extract_settings.py
Outputs: one txt file each of extracted strings for screens, options, and common items 

HOW TO USE:
> Open VS code
> In the top bar -> File -> Open Folder (make sure it's this one)
> In the top bar -> Terminal -> New Terminal
> Go into the terminal and make sure your folder is EXTRACTORS
> If you have python installed, type python3 extract_script.py to extract script.rpy
> Use python3 extract_settings.py to extract options.rpy, screens.rpy, and script.rpy
