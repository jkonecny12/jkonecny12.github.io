Title: Debugging and testing of Anaconda
Date: 2019-20-09
Category: Anaconda

[Anaconda](https://github.com/rhinstaller/anaconda) is quite a complex project with a variety of dependencies on system tools and libraries. Additionally, there are installation mods (graphical, text and non-interactive) and these can be controlled manually, partially (default configuration preset) or fully automatic. Users can also run the Anaconda application locally too to create installation media.
Thanks to this complexity it is not an easy task to just do the required changes and run Anaconda to test it. To test Anaconda properly it is required to run it many times with all the modifications. In addition Anaconda is supported on a variety of platforms and it behaves differently on each. To have a **really** good feeling that everything is tested then the test should have been done on all the supported platforms, including IBM Z systems and Power PC. And yes, not even developers are able to handle that. For most of the common changes, luckily a simple x64 Virtual Machine is a good enough solution.

To cover these issues, we (Anaconda developers) are investing quite a lot of our time to make this situation better. For example we are working on the Anaconda [modularization effort](https://rhinstaller.wordpress.com/2017/10/09/anaconda-modularisation/). Thanks to this effort, developers can connect to modules and play with them. Also thanks to modularization, we have much greater test coverage than before. We have automatic installation tests called [kickstart tests](https://github.com/rhinstaller/kickstart-tests). Aside from that, we have unit tests, and we test if RPM files were created successfully.

In this article I want to create a short tutorial about tools which should help with debugging and development of Anaconda. I will describe useful methods to get your changes into the installation environment and how to test them easily with all your required use cases. Because this topic is quite big I will split it into a few articles.

# Updates image

Probably every developer who has contributed complex code to Anaconda development has heard about updates images. This is the beginning of our journey and the first part of this blog post series. Updates images are a basic tool used on an everyday basis to test changes targeted to Anaconda. With an updates image, you can replace any file in the installation environment. It is possible to replace for example sshd configuration file in the /etc directory or any source file of Anaconda. Because Anaconda is written almost entirely Python, it is easy to just replace specific source files before Anaconda is launched.

At its core, an updates image is just an image containing files created by the cpio and pigz utilities. There is no magic at all. But why is there even a need to create these images? The reason is how the main Anaconda use-case looks like. There is an ISO containing everything used for installation, including Anaconda. This environment is called stage 2. There is also stage 1, but it will be described later in a different post. An updates image is created to rewrite any file in stage 2 before Anaconda and other tools are started.

To apply an updates image, you need to add [inst.updates](https://anaconda-installer.readthedocs.io/en/latest/boot-options.html#inst-updates) on the kernel boot parameters or you can add the link to the [kickstart file](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#updates). Both solutions should have the same result. Please follow the links to find out more.

## Manually

You can easily create an updates image from the command line:

```shell
find . | cpio -c -o | pigz -9cv > ../updates.img
```

When this is called all the content in the current directory will be placed into the updates image. File paths relative from this directory will be preserved in the installation environment, e.g. `./etc/ssh/sshd_config` will replace `/etc/ssh/sshd_config` in the installation environment. This solution is an easy way to create an updates image, but it is not very nice to apply changes from Anaconda or other advanced use cases.


## Using `makeupdates` script

Because we are recreating updates images many, many times a day we have created tools to make our lives easier. The most important and oldest method is the [makeupdates](https://github.com/rhinstaller/anaconda/blob/master/scripts/makeupdates) script in the Anaconda repository. This script will add every Anaconda file that changed from a point in the git history. The script has additional features like adding RPM package content to the updates image. I’ll now describe the most interesting features you can use with this script. To find out more about the `makeupdates` script please see the `--help` parameter.

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

Readers familiar with git probably already know that the `--tag` parameter accepts anything which can be used to specify a git commit and add all the files changed from that point to the current state. That means you can specify version tag e.g. `anaconda-31.25.2-1` as well as `HEAD~`.

### Add custom RPM

From time to time there is a need to add more than just parts of Anaconda to an updates image, for example, custom files or libraries. Even for this use case the `makeupdates` script can be used.

```shell
./scripts/makeupdates --add /path/to/my/first.rpm --add /path/to/my/second.rpm
```

This is an easy way to add a custom RPM file to the installation environment. However, there is a drawback to this solution.

#### RPM scriptlets are not executed in this case.

RPM scriptlets are scripts in the rpm file which are executed when some action occurred (for example installation of the RPM could adjust configuration of the system). The reason why this is happening is that these RPM files are not installed to the updates image but only unpacked. For most cases that is sufficient, but for some situations you can get unexpected results such as missing files, bad dependencies, bad configuration. This could be fixed by adding more files to the updates image manually, see the section below.

### Add custom files

The `makeupdates` script has a possibility to add or replace almost any content in the installation environment.

```shell
./scripts/makeupdates --keep
```

The `--keep` parameter will prevent the script from removing the updates folder after each call. After running this command you will see the `updates` directory in the root Anaconda directory. You can then place any file in the `updates` directory and call the above command again to create the new updates image with the desired content. Here, the same rule applies as in the manual creation section, that directory structure created in the `updates` directory will be preserved in the installation environment. This command can be called as many times as needed. The `updates` directory won't be erased until the `--keep` parameter is used. Example of this use case is:

```shell
$ ./scripts/makeupdates --keep

$ mkdir -p ./updates/etc/ssh
$ cp /my/custom/config ./updates/etc/ssh/sshd_config

$ ./scripts/makeupdates --keep
```

The above is an example how to change ssh configuration of the booted installation.


## Using wrapper around makeupdates

Aside from *official* `makeupdates` script in the Anaconda git repository, there is an option to use [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper script. This script was created mainly to simplify work with different Anaconda versions but can do more than that. This wrapper was designed to avoid writing custom user scripts. In general almost every user who has used the `makeupdates` script has also written their own scripts to, for example, upload resulting updates image for use in VM.

The following steps are required to prepare an environment for using `anaconda-updates`.

##### Create a configuration file

The configuration file is part of the anaconda updates git repository, see [link](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/updates.cfg). Copy this configuration file into `~/.config/anaconda-updates/updates.cfg` and fill in the values there. This configuration file will specify where is the project folder, containing projects like Anaconda, Pykickstart, and Blivet. Only Anaconda is required, however. It also defines where is the show version script (see below) and how to access a server where the updates image should be uploaded. The last part is really helpful to ease application of the updates image to the test machine, the drawback is that you have to have available server with ssh access.

##### Adapt the show version script

In the git repository there is also a [script](https://github.com/rhinstaller/devel-tools/blob/master/anaconda_updates/scripts/show_version.sh) which is responsible for retrieving information about the current anaconda rpm file. This script has to be updated (or written from scratch if desired) to be applicable to your environment. See the script and make required changes.


When the steps above are completed you can start using the `anaconda-updates` wrapper. The main benefits are that it is not required to use tags but rather the updates image will be created for the Anaconda rpm version (`--master` paramater). This also works for Fedora releases (`--fedoraXX` for fedora version). The automatic upload to a server is also a nice feature, since it helps to speed up the development and debugging cycles. Use of this wrapper script is pretty easy and I'm adding support for a new Fedora when it is released.

# Future improvements

We are planning to promote the `makeupdates` script to a standalone script which will provide much of the current features but with a better user experience. The main change will be to move the functionality of the `makeupdates` script out of the Anaconda source code. We are trying to solve the problem that the script usage is not compatible for all versions and it could be problematic to start an old Anaconda version (RHEL-6/7) scripts on newer Fedora systems. Instead of having this script in different versions of Anaconda code base we will provide one script and the Anaconda code base will provide a configuration file for this script. This will probably deprecate the current [anaconda-updates](https://github.com/rhinstaller/devel-tools/tree/master/anaconda_updates) wrapper script because there won't be any need for that. The new script will have the benefit to be easily extended so it can adapt all the current features of the `anaconda-updates`.

Aside from that we also want to provide users with a default working configuration and separation from the Anaconda code base. That means the script will be usable immediately with no required configuration. It could be even packaged to Fedora if users would like to have it there. We will try to find the best defaults for users. The separation will give the possibility to just add a custom content without any requirement to clone the Anaconda source code. That will make use of the script much easier for people who want to debug something not related to Anaconda in the installation environment (for example why some RPM can't be installed).


Thanks everyone for your focus and if you have an idea for further improvement please write a comment. They are really valuable to us.
