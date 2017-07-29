Introduction
=======================

selinux.tips is a book providing a detailed overview of the SELinux framework,
it's uses, and how it is implemented.  Hopefully it should provide some insight
into the need for strong access controls.

First off I'd like to give a bit of background information on what SELinux is
and how it accomplishes it's design goals by creating a short FAQ that will
hopefully answer any initial questions.

What is SELinux?
----------------

In short, SELinux is a customizable and flexible framework for implementing
mandatory access control models.  The Linux kernel provides several core
mandatory access control implementations each with their own security goals and
varying levels of granularity.  SELinux aims to be the most flexible by giving
the security policy author control over the most fine-grained aspects of the
security model where other implementations do not.

There are 3 main components that make up the SELinux framework.  These are the
security server, the userspace tools, and the policy.

The security server is a Linux Security Module that enforces a security policy
built by the userspace tools.  It also provides an interface for userspace
tools to talk to, in order to make them "SELinux aware" [citation needed:
SELinux awareness in programs].  These components will be explored in detail
further on after covering the fundamental concepts introduced here.

What is Mandatory Access Control?
---------------------------------

Mandatory access control is a method for governing access control decisions
using a centralized security policy.  This policy can constrain the various
interactions that can happen between entities (for example: preventing a
program from reading another programs private data).

Entities can be either subjects (the entity requesting permissions) or objects
(the entity permissions were requested on).  On an operating system a subject
would typically be a process, with an example of an object being a file.
However, this can be expanded upon by other software that wishes to use
mandatory access controls to make authorization decisions.[citation needed:
XACE, SEPostgres, systemd, dbus]  Though, in practice the distinction between
subjects and objects isn't so easy to make. It's possible for a process to
request permissions on another process, and likewise for objects, it's possible
for a file to request permissions to associate itself with a
filesystem.[citation needed: SELinux file and filesystem security classes].

Mandatory access controls usually sit on top of, or extend, discretionary
access controls.  An example of a discretionary access control model being
POSIX permissions.  The mandatory access controls extend those permissions by
allowing for additional security checks over the files on which the permissions
are set, but cannot allow anything that the POSIX permissions didn't already
grant.

The main difference between the two access control models here is that
authorization decisions are centralized (Mandatory Access control) in one and
decentralized in the other (Discretionary Access Control).

What is Discretionary Access Control?
-------------------------------------

Discretionary access control is a security model that uses ownership (or
identity, usually in combination with groups) to compute authorization
decisions.  The most common example of this is the previously mentioned POSIX
permissions model that is used on Linux.  When a process requests to read a
file, the authorization is granted if the identity of the process (the user or
group it is running as) has ownership and the read permission bit on the
specified file.

A user also has the ability to assign ownership of an object they own to someone
else at their own discretion, thus passing on any permissions.  This is the
discretionary element of this access control model.  Due to this, discretionary
access control models are insufficient for restricting information flow and
locking down permissions at a fine-grained level.

Why is there a need for Mandatory Access Controls?
--------------------------------------------------

We've now covered what mandatory access control is, but not why there is a need
for it.  This is covered in the great paper "The Inevitability of Failure: The
Flawed Assumption of Security in Modern Computing Environments."
[bib entry: todo] However, we will touch on some specific examples that
illustrate the need for mandatory access controls using a Linux server as our
example platform.

Using a security policy we can restrict privileged services (running as root)
to prevent them interacting with each other services or reading any secret
data.  An example of this could be preventing Apache HTTPd from reading
/etc/shadow or users home directories.  Or simply tampering with another
services data files, such as MySQL.  In SELinux this is a model known as
"type-enforcement" [citation needed: SELinux security models] that allows a
policy author to assign types to processes and files, then restricting the
interactions that can happen between them.  Since the behavior of mandatory
access control systems is to deny first, comparisons could be drawn between
this and a rule-based whitelist.

Secondly, we can also use mandatory access controls to address confidentiality
and compartmentalization.  It is common for users to be working at
several confidentiality levels and preventing information leaks is a number one
priority.  By using what is known as Multi-Level Security we can use security
levels to restrict the directions that information can flow.  An example of
Multi-Level Security is the Bell-LaPadula model, which uses security levels to
enforce what it calls "read down, write up."  This prevents a user with a
clearance of e.g., Classified leaking information to a lower clearance level of
Unclassified.  In contrast, the user can only write information to a higher clearance
level or a clearance level equivalent to their own.

On an MLS system, this would prevent information exfiltration through an
untrusted channel (for example: removable media at a lower clearance level) or
reading any information at a higher clearance level than the users own.

How does SELinux work?
----------------------

How is SELinux different from AppArmor?
---------------------------------------
