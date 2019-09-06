Title: Debugging and testing of Anaconda
Date: 2017-10-9
Category: Anaconda

Anaconda is quite complex project with many dependencies on variety of libraries but also system dependencies like kernel and storage libraries. Another thing which makes situation even worse are installation mods. There are graphical (GUI), text (TUI) but also mods like fully and partial automatic text or graphical, or non-interactive mod. And I have missed that Anaconda can be run locally to create bootable ISO image. 
Thanks to this complexity it is not that easy to just do the required changes and run the Anaconda. One problem is that it is required to run Anaconda plenty of times to just test it properly with all the mods and the second problem is that you need VM to test most of the use cases.

To address this we (Anaconda developers) are investing quite some time to make this easier. For example, recently we made huge progress with kickstart tests but that will be explained later. Another thing which should makes things much better is Anaconda modularization effort. Modularized Anaconda will be able to run modules separately in testing virtual dbus environment.

In this article I want to give you basic information on why it is so hard to make changes to Anaconda but also create short tutorial how to do Anaconda development properly. I will describe useful methods to get your changes into the installation environment and how to test it easily with all your required use cases.

# Updates image

If you were around Anaconda development you probably heard about updates images. They are common base for every testing or debugging. By updates image you can replace any file in the installation environment. You can replace for example sshd configuration file in the /etc directory.

To apply updates image you need to add inst.updates(add link) on the grub kernel boot command line or you can add the link to the kickstart file(add link). Both solutions should have the same result. Please follow the links above to find out more.

Updates image is just an image created by the cpio and pigz utilities.

## Manually

You can easily create updates image from command line:

```
find . | cpio -c -o | pigz -9cv > ../updates.img
```

When this is called all the content in the actual directory will be placed into the updates image. File paths in this directory will be preserved in the installation environment. This solution is easy to create updates image but it is not that nice to add changed files for Anaconda.


## Creating updates image by makeupdates script

Because we are recreating updates image many, many times a day we have tools to make our life easier. The most important one is makeupdates script in the Anaconda repository(add link). This script will add all the changed files from some point and also additional features like adding RPM package content to the updates image. I’ll now show the most interesting features you can do with this script.

Basic usage:

```
./scripts/makeupdates -t HEAD
```

Add all files which were not committed yet to the updates image.

```
./scripts/makeupdates -t anaconda-29.1.1-1
```

Add all files changed since the anaconda-29.1.1-1 git tag was created.

As readers familiar with the git already know that -t parameter accept anything which can be used to specify commit in a git and add all the files changed from that point to the actual state.

