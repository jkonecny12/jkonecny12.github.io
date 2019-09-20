Title: Debugging and testing of Anaconda
Date: 2019-20-09
Category: Anaconda

[Anaconda](https://github.com/rhinstaller/anaconda) is a quite complex project with many dependencies on variety of libraries but also system dependencies like kernel features and storage libraries. Aside of that, which makes situation even worse, are installation mods. There are graphical (GUI), text (TUI) but also mods like fully and partial automatic text or graphical, or non-interactive mod. Users can run the Anaconda application locally too to create an installation media.
Thanks to this complexity it is not an easy task to just do the required changes and run the Anaconda to test it. To test Anaconda appropriately it is required to run it a plenty of times with all the modifications. In addition Anaconda is supported on plenty of platforms and it behaves differently on each platform so to have a **really** good feeling that everything is tested then the test should have been done on all the supported platforms, including IBM Z systems and Power PC. And yes, not even developers are able to handle that so for most of the common changes luckily a simple x64 Virtual Machine is the good enough solution.

To cover these issue, we (Anaconda developers) are investing a quite amount of our time to make this situation better. For example we are working on the Anaconda [modularization effort](https://rhinstaller.wordpress.com/2017/10/09/anaconda-modularisation/). Thanks to this effort developer can is able to connect to modules and play with them. Also thanks to the modularization we have a much greater test coverage then before. We have an automatic installations tests called [kickstart tests](https://github.com/rhinstaller/kickstart-tests). Aside of that we have unit-tests and test if RPM files were created successfully.

In this article I want to give you basic information on why it is so hard to make changes to Anaconda but the main reason is to create a short tutorial about tools which should help with debugging and development of Anaconda. I will describe useful methods to get your changes into the installation environment and how to test it easily with all your required use cases. Because this topic is quite a big I will split it into a few articles.

# Updates image

Probably an every developer who contributed a little bit more complex code to Anaconda development have heard about the updates images. This is beginning of our journey and first part of this blog post series. The updates images are the basic tool used on everyday basis to test changes targeted to Anaconda. By updates image you can replace any file in the installation environment. It is possible to replace for example sshd configuration file in the /etc directory or any source file of Anaconda. Thanks to the fact that Anaconda is almost completely Python language it is easy to just replace source specific source files before Anaconda is launched.

In the core an updates image is just an image containing files created by the cpio and pigz utilities. No magic at all. But why there is a need to create these images. The problem is how the main Anaconda use-case looks like. There is an ISO containing everything used for installation, including anaconda program. This environment is called stage 2, there is also stage 1 but it will be described later in a different post. An updates image is created to rewrite any file in the stage 2 before Anaconda and other tools are started.

To apply updates image you need to add [inst.updates](https://anaconda-installer.readthedocs.io/en/latest/boot-options.html#inst-updates) on the kernel boot parameters or you can add the link to the [kickstart file](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#updates). Both solutions should have the same result. Please follow the links to find out more.

## Manually

You can easily create an updates image from the command line:

```shell
find . | cpio -c -o | pigz -9cv > ../updates.img
```

When this is called all the content in the current directory will be placed into the updates image. File paths relative from this directory will be preserved in the installation environment, e.g. `./etc/ssh/sshd_config` will replace `/etc/ssh/sshd_config` in the installation environment. This solution is an easy way how to create an updates image but it is not that nice to apply changes from Anaconda or other advanced use cases.


## Using `makeupdates` script

Because we are recreating updates image many, many times a day we have created tools to make our life easier. The most important one and the most older one is [makeupdates](https://github.com/rhinstaller/anaconda/blob/master/scripts/makeupdates) script in the Anaconda repository. This script will add every Anaconda file that changed from a point in the git history. The script has additional features like adding RPM package content to the updates image. I’ll now describe the most interesting features you can use with this script. To find out more about the `makeupdates` script please see `--help` parameter.

You can combine any of the parameters described below.

### Basic usage

```shell
./scripts/makeupdates --tag HEAD
```

Add all files which were not committed yet to the updates image.

```shell
./scripts/makeupdates --tag anaconda-29.1.1-1
```
Add all files changed since the commit with the anaconda-29.1.1-1 git tag was created. In other words add all changes to make anaconda version 29.1.1-1 on stage 2 the current anaconda in the git repository.

Readers familiar with the git probably already know that `--tag` parameter accept anything which can be used to specify commit in a git and add all the files changed from that point to the current state. That means you can specify version tag e.g. `anaconda-31.25.2-1` as well as `HEAD~`.

### Add custom RPM

From time to time there is a need to get more than just parts of the Anaconda to the updates image but instead some custom files or libraries. Even for this use case the `makeupdates` script can be used.

```shell
./scripts/makeupdates --add /path/to/my/first.rpm --add /path/to/my/second.rpm
```

This is an easy way how to add a custom RPM file to the installation environment. However, there is a drawback to this solution.

#### RPM scriptlets are not executed in this case.

RPM scriptlets are scripts in the rpm file which are executed when some action occurred (for example installation of the RPM could adjust configuration of the system). Reason why this is happening is that these RPM files are not installed to the updates image but only unpacked. For most cases that is sufficient but for some situations you can get unexpected results of missing files, bad dependencies, bad configuration. This could be fixed by adding more files to the updates image manually, see the section below.

### Add custom files

The `makeupdates` script have a possibility to add or replace almost any content in the installation environment.

```shell
./scripts/makeupdates --keep
```

The `--keep` parameter will prevent the script to remove the updates folder after each call of the `makeupdates`. After running this command you will see the `updates` directory in the root Anaconda directory. You can then place any file in the `updates` directory and call the above command again to create the new updates image with the desired content. Here works the same rule as in manual creation section above, that directory structure created in the `updates` directory will be preserved into the installation environment. This command can be called as many times as needed the `updates` directory won't be erased until the `--keep` parameter is used. Example of this use case is:

```shell
$ ./scripts/makeupdates --keep

$ mkdir -p ./updates/etc/ssh
$ cp /my/custom/config ./updates/etc/ssh/sshd_config

$ ./scripts/makeupdates --keep
```

The above is an example how to change ssh configuration of the booted installation.


## Using wrapper around makeupdates

Aside of the *official* `makeupdates` script in the Anaconda git, there is an option to use [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper script. This script was created mainly to simplify work with different Anaconda versions but can do more than that. This wrapper was designed to avoid writing user custom scripts. In general almost every user who have used `makeupdates` script more than once wrote their own scripts to for example upload resulting updates image for use in VM.

The following steps are required to prepare environment for using `anaconda-updates`.

* Create a configuration file

      The configuration file is part of the anaconda updates git repository, see [link](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/updates.cfg). Copy this configuration file into `~/.config/anaconda-updates/updates.cfg` and fill up the values there. This configuration file will specify where is the project folder, containing projects like Anaconda, Pykickstart, Blivet (only Anaconda is required). It also defines where is the show version script (see below) and how to access a server where the updates image should be uploaded. The last part is really helpful to ease application of the updates image to the test machine, the drawback is that you have to have available server with ssh access.

* Adapt the show version script

      In the git repository there is also a [script](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/scripts/show_version.sh) which is responsible to get information about the current anaconda rpm file. This script have to be updated (or written from a scratch if desired) to be applicable to your environment. See the script and make required changes.


When the steps above are completed you can start using the `anaconda-updates` wrapper. The main benefits are that it is not required to use tags but rather the updates image will be created for the Anaconda rpm version (`--master` paramater), this also works for released fedora (`--fedoraXX` for fedora version). The automatic upload to the server to help faster the development and debugging cycles is also a nice feature. Use of this wrapper script is pretty easy and I'm adding support for a new Fedora when it is released.

# Future improvements

We are planning to promote the `makeupdates` script to a standalone script which will provide much of the current features but with a better user experience. The main change will be to move the functionality of the `makeupdates` script out of the Anaconda source code. We are trying to solve problem that the script usage is not compatible for all version and it could be problematic to start the old Anaconda version (RHEL-6/7) scripts on newer Fedora systems. Instead of having this script in different versions of Anaconda code base we will provide one script and Anaconda code base will provide a configuration file for this script. This will probably deprecate current [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper script because there won't be any need for that. The new script will have the benefit to be easily extended so it can adapt all the current features of the `anaconda-updates`.

Aside of that we also want to provide users default working configuration and separation from the Anaconda code base. That means the script will be usable from the `git clone` call and all the setting will be only an optional. It could be even packaged to Fedora if users would like to have it there. We will try to find the best defaults for users. The separation will give the possibility to just add a custom content without any requirement to clone the Anaconda source code. That will make use of the script much easier for people who want to debug something not related to Anaconda in the installation environment (for example why some RPM can't be installed).


Thanks everyone for your focus and if you have an idea for further improvement please write a comment. They are really valuable to us.
