Title: Space requirement check in Anaconda reworked for Fedora 23
Date: 2017-10-9
Category: Anaconda

Before the release of [Fedora 23](https://fedoramagazine.org/fedora-23-released/) I was working on a bug which have caused Anaconda to fail the installation because of RPM transaction check error.
This brought me to the investigation of the required space check. It eventually lead to complete rework of the space requirement check in Anaconda. I would like to explain why this was needed and how is it working now.

#### The problem of the old space check
The old solution was really minimalistic. It read installed size of all required packages from [DNF](http://dnf.baseurl.org/) Python interface and then added 35 percent as a 'bonus'.
Why 35 percent? It is hard to tell. The number seems to be the result of some old empiric testing - too old to know for sure.
And why to use 'bonus' at all? Because the value obtained from DNF is only a portion of space which is really needed for the installation. DNF computes installed package size as a sum of all file sizes in a package.
It looks somewhat reasonable but it is still far from the real space requirement. Here are several reasons why this isn't correct:

#### Filesystem metadata
Every filesystem has its own metadata. It takes some space which can't be used for your data - in our case packages. I was surprised how much volume metadata can take. I won't dive into the testing suite here[^1] but basically I was creating formatting on testing partition of given space and got usable space by 'df -h'. Of course this won't be 100 percent accurate because the metadata changing depends on a size of the partition
and also on files which are there. However, it is a good way to get a basic idea about how much usable space we get after the formatting is done.
I have run the tests on **EXT2**,**3**,**4**, **XFS**, **BTRFS**, **JFS**, **ReiserFS** and **VFAT** formats which are presumably the most often used formats on Linux nowadays.
Therefor starting with Fedora 23 when user creates new storage device in Anaconda, the space check is testing the size of a new device reduced by highest value from the tests above.
For example when user creates 10GB device and the format takes 10% for metadata the space check will work with 9GB size.

#### Required space computation

As wrote above, the old computation was done by taking sum of the installed size of all packages from DNF and adding another 35 percent to this value. I wanted to use the same computation as the [RPM](http://www.rpm.org/) transaction check. Unfortunately the RPM check cannot be used without downloading the package and the installation environment does not have this privilege. Therefore, Anaconda had to take different approach. The RPM transaction check takes file size but aligns this file to the size of the fragment. The RPM database gets bigger for every file because of the header file. The new space requirement computation is trying to use fragment size and adding some space for every file to grow with RPM database. Additionally Anaconda's fragment size is not set to the exact value.
The usual default value of fragment size is 4KB so the same value was used by Anaconda. As per the RPM database grow the 2KB was chosen by testing.
As a possible future improvement the fragment size could be taken from [Blivet](https://github.com/rhinstaller/blivet) and use this to improve the fragment alignment.

#### How it is working in Anaconda now

The Anaconda now takes from DNF install size which was used before but instead of 35 percent it takes also number of all files from all packages and for every file it adds 6KB to this value. It than adds 10% as bonus to have some reserve. The whole computation is as follows:

`DS * (1 - FM) >= IS + (NF * 6KB) * 10%`

* `DS` - Device size
* `FM` - Format metadata percentage
* `IS` - Packages installed size
* `NF` - Number of installed files

Therefore, new version of this computation should be more precise as explained before. This solution should prevent problems in any future installations caused by lack of space. Drawback of this new method is that it needs more space then it is necessary for installation. As mentioned before, without downloading the packages it's hard to create something more precise[^2].


[^1]: I'm thinking of blog post dedicated to test results of filesystem format medatadata.
[^2]: I want to add *--nospacecheck* parameter to add possibility to start the installation even when there isn't enough space.
