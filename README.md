# Eigendoxx Pre-Commit Hook

<p align="center">
<img src="https://github.com/nuket/Eigendoxx/blob/main/eigendoxx-logo.png?raw=true" alt="Eigendoxx's logo"/>
</p>

Self-doxxing happens when you forget to strip GPS data from photos checked into
GitHub and other public-facing git repositories.

`git` and other tools do not check whether you're about to reveal private
information this way.

I've been caught by this on some of my private repos, and I thought I had
reasonably good digital hygiene.

Here's a `pre-commit` script you can use to ensure that all GPS data is scrubbed
prior to publication.

Note that this only works well for repos started from scratch.

For repos that already contain objects, you would have to walk the
entire repo and all of its checkins and strip and rewrite its entirety. This may
be impractical.

This hook uses the [exiftool](https://github.com/exiftool/exiftool) program
to do its work.

## Prerequisites

* A copy of [`exiftool`](https://github.com/exiftool/exiftool) installed somewhere on your PATH (or via Docker)
* The [`pre-commit`](https://pre-commit.com/) tool installed via `pip`

## Quickstart

Add the following to your `.pre-commit-config.yaml` file's `repos` list:

```
repos:
- repo: https://github.com/nuket/Eigendoxx
  rev: main
  hooks:
  - id: gps-metadata-check
  - id: gps-metadata-remove
```

Once installed, it will check staged files for GPS data that you may or
may not want to check in.

```
max@tools:~/eigendoxx-test$ pre-commit
[INFO] Initializing environment for https://github.com/nuket/Eigendoxx.
check GPS location metadata..............................................Failed
- hook id: gps-metadata-check
- exit code: 48

GPS data was seen in the images.
Strip it with: exiftool -P -gps:all= E5-2.JPEG E5-1.JPG E5-3.jpg E5-4.jpeg
```

## Manual Running

```
max@tools:~/eigendoxx$ ./eigendoxx --help

Scans the specified files for GPS data and removes it if desired.

Usage: ./eigendoxx [--pre-commit-check | --check | --pre-commit-remove | --fix] <*.jpg>
       ./eigendoxx [--check-all | --fix-all]

    --pre-commit-check,  --check    Checks  GPS metadata   in specified files + globs
    --pre-commit-remove, --fix      Removes GPS metadata from specified files + globs

    --check-all                     Checks  GPS metadata   in all files in current + subfolders
    --fix-all                       Removes GPS metadata from all files in current + subfolders

```

## The Problem

GPS metadata is a **major issue** if you're checking in a picture taken at home
or another private location:

```
$ exiftool E5-1.JPG

[...]
GPS Altitude                    : 918 m Above Sea Level
GPS Altitude Ref                : Above Sea Level
GPS Date Stamp                  : 2022:09:14
GPS Date/Time                   : 2022:09:14 14:48:53Z
GPS Img Direction               : 101
GPS Img Direction Ref           : Magnetic North
GPS Latitude                    : 47 deg 22' 56.29" N
GPS Latitude Ref                : North
GPS Longitude                   : 10 deg 17' 24.48" E
GPS Longitude Ref               : East
GPS Position                    : 47 deg 22' 56.29" N, 10 deg 17' 24.48" E
GPS Time Stamp                  : 14:48:53
[...]
```

I've included a few sample photos for testing with in-the-wild GPS data.

## The Solution

Let's say you have the following `git status`:

```
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   E5-1.JPG
        new file:   E5-2.JPEG
```

The hook will check the files and disallow the commit if any GPS data
is found.

You can either activate the `gps-metadata-remove` target in `.pre-commit-config.yaml`
or run `eigendoxx --fix <file names>` or `eigendoxx --fix-all` via the command line
to strip out the GPS tags.

## The Confirmation

If you `diff` the `exiftool` pre- and post-run image files, you'll see all of
the GPS tags stripped out.

```
$ diff i1.txt i2.txt
40,41c40,41
< File Access Date/Time           : 2023:01:15 13:04:11+01:00
< File Inode Change Date/Time     : 2023:01:15 11:19:02+01:00
---
> File Access Date/Time           : 2023:01:15 13:04:19+01:00
> File Inode Change Date/Time     : 2023:01:15 13:04:17+01:00
53,64d52
< GPS Altitude                    : 918 m Above Sea Level
< GPS Altitude Ref                : Above Sea Level
< GPS Date Stamp                  : 2022:09:14
< GPS Date/Time                   : 2022:09:14 14:48:53Z
< GPS Img Direction               : 101
< GPS Img Direction Ref           : Magnetic North
< GPS Latitude                    : 47 deg 22' 56.29" N
< GPS Latitude Ref                : North
< GPS Longitude                   : 10 deg 17' 24.48" E
< GPS Longitude Ref               : East
< GPS Position                    : 47 deg 22' 56.29" N, 10 deg 17' 24.48" E
< GPS Time Stamp                  : 14:48:53
```

None of the GPS tags make it to the scrubbed file.

# License

```
Eigendoxx Pre-Commit Hook
Copyright (c) 2023 Max Vilimpoc (https://vilimpoc.org)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```