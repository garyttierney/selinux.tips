SELinux Userspace
=================

There are a number of reasons for userspace SELinux support, including services
that are SELinux-aware (PAM or Xorg for instance), and administration of SELinux
systems.  Some of these packages are optional, while some, such as ``libselinux``,
are required for a system running SELinux to function correctly.

libselinux
----------

``libselinux`` is the userspace library used by programs which are SELinux
aware in order to communicate with the SELinux subsystem over the selinuxfs.
This allows those programs to lookup security labels for objects, compute
access checks of their own, or set the context to be used for newly created
objects, among other things.

checkpolicy/checkmodule
-----------------------

``checkpolicy`` and ``checkmodule`` are compilers for the kernel policy
language, supporting monolithic and modular policies respectively.

secilc
------

``secilc`` is a monolithic policy compiler for policies written in the
:ref:`common-intermediate-language`.

policycoreutils
---------------

policycoreutils-python
~~~~~~~~~~~~~~~~~~~~~~

setools
-------
