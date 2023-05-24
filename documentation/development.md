The original code is from gtumbler by Gabriele N. Tornetta (See [AUTHORS](AUTHORS)).
(<https://launchpad.net/gtumbler/1.0/1.0/+download/gtumbler_1.0-0ubuntu1.tar.gz>).
converted via
(See <https://dgleich.wordpress.com/2011/01/22/convert-bazaar-to-git/>):
```
# sudo apt install bzr
# sudo apt install bzr-fastexport
sudo dnf install bzr
```
- won't work with fastexport (not solved by 'python -m pip install fastimport'
  According to <https://askubuntu.com/a/1318151>,
  [breezy](https://www.breezy-vcs.org/) bundles fastexport, so:
```
sudo dnf remove bzr
python3 -m virtualenv ~/.virtualenvs/breezy
~/.virtualenvs/breezy/bin/pip install breezy fastimport
BZR=~/.virtualenvs/breezy/bin/brz
```

Clone the bazaar repo (URL is computed automatically!) and init a bare git repo:

```
$BZR branch lp:gtumbler
mkdir gtumbler.git
cd gtumbler.git
git init --bare
# alias bzrexp="$BZR fast-export"
SRC_REPO=~/Downloads/git/~phoenix1987/gtumbler
$BZR fast-export --export-marks=../gtumbler.bzr $SRC_REPO/master \
   | git fast-import --export-marks=../marks.git
```

results:
```
14:27:14 Calculating the revisions to include ...
14:27:14 Starting export of 4 revisions ...
14:27:14 WARNING: not creating tag '12.07' pointing to non-existent revision b'phoenix1987@gmail.com-20120709174546-22zs97volyxdlc5z'
14:27:14 WARNING: not creating tag '12.07.2' pointing to non-existent revision b'phoenix1987@gmail.com-20120712094116-des8fq0y3jhvprb1'
14:27:14 Exported 4 revisions in 0:00:00
Unpacking objects: 100% (92/92), 111.60 KiB | 7.97 MiB/s, done.
. . .
```


```
$BZR fast-export --marks=../gtumbler.bzr --git-branch=0.1 \
   $SRC_REPO/0.1 | git fast-import \
   --import-marks=../marks.git --export-marks=../marks.git
```
# ^ fails. See documentation/development/gtumbler-trying-to-convert-0.1-branch.txt

```
git remote add origin https://github.com/Hierosoft/gtumbler.git
git push --all # push all branches
```

Required packages:
- gi
  - requires PyGObject and possibly pycairo modules (<https://stackoverflow.com/a/71369926/4541104>)
  - requires `sudo apt install libcairo2-dev libxt-dev libgirepository1.0-dev` (<https://stackoverflow.com/a/71369926/4541104>)
  - Arch: `paru -S gobject-introspection` (<https://stackoverflow.com/a/74017551/4541104>)
  - `pip install gobject` (<https://stackoverflow.com/a/74017551/4541104>)

Issues:
- is Python 2
File "/home/owner/Downloads/git/~phoenix1987/gtumbler/gtumbler/GtumblerWindow.py", line 209
    print p
    ^^^^^^^
- mixes tabs and spaces in GtumblerWindow.py (Python 2 tolerates it)
