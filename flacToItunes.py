#!/usr/local/bin/python3

# Copyright 2019 Ole Kliemann
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import mutagen
import sys
import tempfile
import subprocess
import os

metadataMapping = {
    'artist': 'artist',
    'album': 'album',
    'title': 'name',
    'albumartist': 'album artist',
    'tracknumber': 'track number',
    'date': 'year',
    'comment': 'comment',
    'genre': 'genre',
    'tracktotal': 'track count',
    'description': 'description',
    'discnmuber': 'disc number'
  }

def mkScriptHead(filename):
  return [
      'set thisFile to POSIX file \"' + filename + '\" as alias',
      'tell application \"iTunes\"',
      'set plist to make new user playlist',
      'set thisTrack to add thisFile to plist',
      'delete plist'
    ]

def mkScriptTail():
  return ['end tell']

def mkMetadataAssignment(field, value):
  return 'set ' + field + ' of thisTrack to \"' + value + '\"'

def mkScriptMetadata(metadata):
  result = []
  for key in metadata:
    if key in metadataMapping:
      result.append(mkMetadataAssignment(metadataMapping[key], metadata[key][0]))
  return result

def mkScriptSetArtwork(filename_artwork):
  if filename_artwork:
    return [
        'set data of artwork 1 of thisTrack to thisArtwork'
      ]
  else:
    return []

def mkScriptReadArtwork(filename_artwork):
  if filename_artwork:
    return [
        'set thisArtwork to (read (POSIX file \"' + filename_artwork + '\") as data)'
      ]
  else:
    return []

def mkScript(filename, metadata, filename_artwork):
  return mkScriptReadArtwork(filename_artwork) + \
         mkScriptHead(filename) + \
         mkScriptMetadata(metadata) + \
         mkScriptSetArtwork(filename_artwork) + \
         mkScriptTail()

def mkOsascriptCommandline(script):
  print(script)
  return [ 'osascript' ] + [ x for y in script for x in [ '-e', y ] ]

def getMetadata(filename):
  return mutagen.File(filename)

def addFile(path):
  filename = os.path.basename(path)
  with tempfile.TemporaryDirectory() as tmpdir:
    filename_wave = os.path.join(tmpdir, os.path.splitext(filename)[0] + '.wav')
    subprocess.run(
        ['flac', '-d', '-o', filename_wave, path],
        check=True
      )

    filename_alac = os.path.join(tmpdir, os.path.splitext(filename)[0] + '.m4a')
    subprocess.run(
        ['afconvert', '-d', 'alac', filename_wave, filename_alac],
        check=True
      )

    metadata = getMetadata(path)

    filename_artwork = ''
    if metadata.pictures and metadata.pictures[0].mime == 'image/jpeg':
      filename_artwork = os.path.join(tmpdir, 'artwork.jpg')
      with open(filename_artwork, 'wb') as file_artwork:
        file_artwork.write(metadata.pictures[0].data)

    script = mkScript(filename_alac, metadata, filename_artwork)
    script_commandline = mkOsascriptCommandline(script)
    subprocess.run(script_commandline, check=True)
    print('added file: ' + filename)
    print(str(metadata))

for path in sys.argv[1:]:
  addFile(path)
