# Installation

You will need to install `mutagen`:

```
pip install mutagen
```

# Usage

```
flacToItunes.py filenames...
```

Converts the specified FLAC files to ALAC using `flac` and `afconvert`.
Adds them to iTunes, set metadata in iTunes according to metadata found
in FLAC file. Finally, if the FLAC metadata contained a JPEG, adds this
as artwork for the track in iTunes.

If some metadata field remains empty in iTunes, you may have to provide
a mapping from the name of the FLAC metadata tag to whatever name iTunes
uses for that field. You can do that by extending the `metadataMapping`
dictionary found at the beginning of the python script.
