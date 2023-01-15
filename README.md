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

For repos that already contain objects, there would need to be a way to walk the
entire repo and all of its checkins and strip and rewrite its entirety. This may
be impractical.

This hook uses the [exiftool](https://github.com/exiftool/exiftool) program to
do its work.

## Quickstart

In your project:

```
cd .git/hooks
mkdir exiftool
curl -o exiftool/exiftool https://raw.githubusercontent.com/exiftool/exiftool/master/exiftool
curl -s https://raw.githubusercontent.com/nuket/Eigendoxx/main/pre-commit >> pre-commit
```

This appends the checks to any existing `pre-commit` file.

### Parameter: autofix

You can now run:

```
DOXX=autofix git commit
```

to strip the GPS data from incoming image files in your git repo.

Note, the script will only modify files when explicitly told to do so by setting `DOXX=autofix`.

_Be careful_, as it will modify images _in-place_ (and this is _before the file
is in revision control_).

### Parameter: ok

If you need to check in image files that contain GPS data, you can run:

```
DOXX=ok git commit
```

## The Problem

GPS metadata is a **major issue** if you're checking in a picture taken at home
or another private location:

```
$ perl exiftool/exiftool E5-1.JPG

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

The `pre-commit` hook will report the following and disallow the commit:

```
$ git commit

Checking E5-1.JPG for GPS tags.

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

Checking E5-2.JPEG for GPS tags.

GPS Altitude                    : 1861.9 m Above Sea Level
GPS Altitude Ref                : Above Sea Level
GPS Date Stamp                  : 2022:09:17
GPS Date/Time                   : 2022:09:17 08:57:05Z
GPS Img Direction               : 85
GPS Img Direction Ref           : Magnetic North
GPS Latitude                    : 47 deg 11' 17.81" N
GPS Latitude Ref                : North
GPS Longitude                   : 10 deg 31' 12.65" E
GPS Longitude Ref               : East
GPS Position                    : 47 deg 11' 17.81" N, 10 deg 31' 12.65" E
GPS Time Stamp                  : 08:57:05

GPS tags found in incoming JPEG files.

To autofix the files, run:

    DOXX=autofix git commit

To force the commit, run:

    DOXX=ok git commit

To strip the JPEG files by hand:

    perl exiftool/exiftool -ext jpg -ext jpeg -overwrite_original -P -gps:all= E5-1.JPG E5-2.JPEG
```

Removing GPS metadata from committed files:

```
$ perl exiftool/exiftool -ext jpg -ext jpeg -overwrite_original -P -gps:all= E5-1.JPG E5-2.JPEG
    2 image files updated
```

Then, `git add` and `git commit` the files again, and everything is good.

There's also to option to remove all GPS metadata from all image files in all
subfolders, but you may not wish to do this preemptively:

```
$ perl exiftool/exiftool -ext jpg -ext jpeg -overwrite_original -P -r -i exiftool -gps:all= .
    1 directories scanned
    4 image files updated
```

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

None of the GPS tags made it to the scrubbed file.

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