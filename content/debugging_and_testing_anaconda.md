Title: Debugging and testing of Anaconda
Date: 2017-10-9
Category: Anaconda

Anaconda is a quite complex project with many dependencies on variety of libraries but also system dependencies like kernel and storage libraries. Aside of that, which makes situation even worse, are installation mods. There are graphical (GUI), text (TUI) but also mods like fully and partial automatic text or graphical, or non-interactive mod. We also need to add that Anaconda can be run locally to create an installation media.
Thanks to this complexity it is not an easy task to just do the required changes and run the Anaconda. It is required to run Anaconda plenty of times to just test it properly with all the mods and another problem is that you need a VM to test most of the use cases.

To address this we, (Anaconda developers) are investing a quite amount of our time to make this easier and automate things. For example we are working on Anaconda modularization effort. You are able to connect to modules and play with them.

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
./scripts/makeupdates -t HEAD
```

Add all files which were not committed yet to the updates image.

```
./scripts/makeupdates -t anaconda-29.1.1-1
```
Add all files changed since the anaconda-29.1.1-1 git tag was created.

Readers familiar with the git already know that -t parameter accept anything which can be used to specify commit in a git and add all the files changed from that point to the actual state. That means you can specify version tag e.g. `anaconda-31.25.2-1` or `HEAD~`.

### Add RPMs

<Describe more options from make updates>

## Using wrapper around makeupdates

<Describe anaconda-updates.>

# Future improvements

<What are our plans with the updates image.>
