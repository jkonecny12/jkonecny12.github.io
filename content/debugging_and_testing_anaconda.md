Title: Debugging and testing of Anaconda
Date: 2017-16-09
Category: Anaconda

Anaconda is a quite complex project with many dependencies on variety of libraries but also system dependencies like kernel and storage libraries. Aside of that, which makes situation even worse, are installation mods. There are graphical (GUI), text (TUI) but also mods like fully and partial automatic text or graphical, or non-interactive mod. We also need to add that Anaconda can be run locally to create an installation media.
Thanks to this complexity it is not an easy task to just do the required changes and run the Anaconda. It is required to run Anaconda plenty of times to just test it properly with all the mods and another problem is that you need a VM to test most of the use cases.

To address this issue, we (Anaconda developers) are investing a quite amount of our time to make this easier and automate things. For example we are working on Anaconda modularization effort. You are able to connect to modules and play with them.

In this article I want to give you basic information on why it is so hard to make changes to Anaconda but also create short tutorial how to do Anaconda development properly. I will describe useful methods to get your changes into the installation environment and how to test it easily with all your required use cases. Because this topic is quite a big I will split it to a few articles.

# Updates image

If you were around Anaconda development you probably heard about updates images. They are the basic tool used on everyday basis to test changes in the Anaconda. By updates image you can replace any file in the installation environment. You can replace for example sshd configuration file in the /etc directory.

To apply updates image you need to add [inst.updates](https://anaconda-installer.readthedocs.io/en/latest/boot-options.html#inst-updates) on the kernel boot parameters or you can add the link to the [kickstart file](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#updates). Both solutions should have the same result. Please follow the links above to find out more.

Updates image is just an image created by the cpio and pigz utilities. No magic at all. There is a few options to create the updates image.

## Manually

You can easily create updates image from command line:

```
find . | cpio -c -o | pigz -9cv > ../updates.img
```

When this is called all the content in the current directory will be placed into the updates image. File paths in this directory will be preserved in the installation environment, e.g. `./etc/ssh/ssh_config` will replace `/etc/ssh/ssh_config` in the installation environment. This solution is an easy way how to create updates image but it is not that nice to add changed files from Anaconda.


## Creating updates image by makeupdates script

Because we are recreating updates image many, many times a day we have tools to make our life easier. The most important one is [makeupdates](https://github.com/rhinstaller/anaconda/blob/master/scripts/makeupdates) script in the Anaconda repository. This script will add all the changed files from some point and also additional features like adding RPM package content to the updates image. I’ll now show the most interesting features you can do with this script.

### Basic usage

```
./scripts/makeupdates --tag HEAD
```

Add all files which were not committed yet to the updates image.

```
./scripts/makeupdates --tag anaconda-29.1.1-1
```
Add all files changed since the anaconda-29.1.1-1 git tag was created.

Readers familiar with the git already know that -t parameter accept anything which can be used to specify commit in a git and add all the files changed from that point to the actual state. That means you can specify version tag e.g. `anaconda-31.25.2-1` or `HEAD~`.

### Add custom RPM

From time to time there is a need to get more than just parts of the Anaconda to the updates image. Even for this reason you can still use the updates image.

```
./scripts/makeupdates --tag HEAD --add /path/to/my/first.rpm --add /path/to/my/second.rpm
```

This is a cool way how to add a custom RPM file to the installation environment. However, there are drawbacks to this solution.

1) RPM scriptlets are not launched in this case. 

RPM scriptlets are scripts in the rpm file which are run when some action happens (for example installation of the RPM). Reason why this is happening is that these RPM files are not installed to the updates image but only unpacked. For most cases that is totally fine but for some you can get unexpected results of missing files etc.

2) Easy to also add Anaconda parts to the updates image.

You have to run the script with the `-t` parameter which will add all changed files (based on the value) to the updates image. Plenty of cases like this are then breaking installation in some point because you are loading invalid files into the installation environment. This is caused by the unfortunate design of the makeupdates script.

### Add custom files

By using the `makeupdates` script there is a possibility to add a basically any content. This way it's possible to add or replace any file in the installation environment.

```
./scripts/makeupdates --tag HEAD --keep
```

The `--keep` parameter will prevent the script to remove the folder after use. After running this command you will see the `updates` directory in the root Anaconda folder. You can then create any directory or any file in the `updates` directory and then run the above command again to create new updates image with the desired content. This can be done as many times as needed the `updates` directory won't be erased until the `--keep` parameter is used. Example of this use case is:

```
$ ./scripts/makeupdates --tag HEAD --keep

$ mkdir -p ./updates/etc/ssh
$ cp /my/custom/config ./updates/etc/ssh/sshd_config

$ ./scripts/makeupdates --tag HEAD --keep
```

This is an example how to change ssh configuration of the booted installation.


For more use-cases please see `--help` parameter of the `makeupdates` script.

## Using wrapper around makeupdates

Aside of the official `makeupdates` script in the Anaconda git, there is a possibility to use [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper created to make easier to work with different Anaconda versions. This wrapper was created to avoid writing more custom scripts to load current version of Anaconda you are using which was written by almost everyone who used `makeupdates` script.

There are steps required to be able to start using `anaconda-updates`.

1) Create a configuration file

The configuration file is in the git repository of the anaconda updates, see [link](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/updates.cfg). Copy this configuration file into `~/.config/anaconda-updates/updates.cfg` and fill up the values there. This configuration file will specify where is your Anaconda folder, where is the show version script (see below) and also access information to the server where the updates image will be uploaded. The last part is really helpful to ease application of the updates image, the drawback is that you have to have server.

2) Adapt the show version script

In the git repository there is also a [script](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/scripts/show_version.sh) which is responsible to get information about the current anaconda rpm file version. This script have to be updated (or written from a scratch) to be applicable to your environment. See the script and make required changes.

When the steps above are completed then you can benefit using this wrapper. The main two benefits are that it is not required to use tags but rather the updates image will be created for the Anaconda rpm version (`--master` paramater), this also works for released fedora (`--fedoraXX` for fedora version). Another benefit is the automatic upload to the server to help faster the development and debugging cycles.

# Future improvements

We are planning to promote the `makeupdates` script to a standalone script which will provide you much of the current benefit but with a much better user experience. The main change will be to move the functionality of the `makeupdates` script out of the Anaconda source code. We are trying to solve problem that the script usage is not compatible for all version and it's even hard to start the old Anaconda version (RHEL-6/7) scripts on newer Fedora systems. Instead of having this script in different versions of Anaconda code base we will provide one script and Anaconda code base will provide configuration file for this script. This will probably replace current [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper script because there won't be any need for that, the new script will have the benefit to be easily extended so it can adapt all the current benefits of the `anaconda-updates`.

Aside of that we also want to provide users default working configuration and separation from the Anaconda code base. That means that the script will be usable from the `git clone` and all the setting will be only optional. We will try to find the best defaults for users. The separation will give the possibility to just add a custom content without any requirement from the Anaconda source code. That will make use of the script much easier for people who want to debug something not related to Anaconda in the Anaconda environment (for example why some RPM can't be installed).
