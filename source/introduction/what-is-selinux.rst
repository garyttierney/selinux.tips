What is SELinux?
================

To understand how SELinux can improve software security and reduce attack surface
in Linux distributions, it's first required to understand what SELinux really
is and what it can do.  When most people think of SELinux, they think of the
policy deployed by Red Hat on Fedora and Enterprise Linux operating systems.

However, SELinux is really much more than that.  At the very core SELinux is
a framework for building mandatory access control models, and a very flexible
framework at that.

Red Hat have put this framework to use to build a policy model which suits most
of their customers, while in contrast the Android Open Source Project has used
the framework to build a model for their specialized embedded Linux platform.

These two particular implementations still resolve around the same core framework
concepts but apply them in different ways.  The most common concept that people
are familiar with (and illustrated by Máirín Duffy in the SELinux coloring
book) is type-enforcement, though this just scratches the surface.  There are
many building blocks that SELinux provides for us to create a security model,
which we'll go into below.


The core concepts of SELinux
----------------------------

Despite how flexible SELinux is, the core concepts are quite simple to
understand.  Understanding how these concepts come together on a Linux
distribution can be difficult at times, but the concepts themselves are quite
easy to grok.

Subjects and objects
~~~~~~~~~~~~~~~~~~~~

In the access control world we refer to entities as subjects and objects.  A
subject is an active entity, which performs operations on objects and interacts
with other subjects.  An object is a passive entity, which doesn't act on its
own and is usually a static file or operating system resource.  Both subjects
and objects have security classes which define their type, and the list of
permissions which are checked for operations or interactions on them.

In SELinux, the operations and interactions which subjects can perform on
objects and other subjects are defined by constraints and rules on security
attributes and classes written in the policy.

Security classes and permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As noted above, each subject or object in SELinux has a security class
and a list of associated permissions.  The SELinux LSM registers hooks
for security checks, most commonly on syscalls, and maps the current task
and object that the security check was for to a set of security attributes,
including a security class and set of permissions.  This makes the SELinux LSM an
**object manager** for entities associated with those security classes.  However,
userspace programs can also define their own security classes to be used in SELinux
policy and use the security server to compute access checks on entities managed by
the program.

When SELinux has resolved the security attributes of the two entities it asks
the security server if there is any rules allowing access to the permissions
requested between the two sets of security attributes and returns the result
back to the kernel function requesting the security check, optionally logging
the check with the audit subsystem in the process.

.. code-block:: txt
    :caption: A declaration of a security class named ipc and its set of permissions.
    
    common ipc
    {
            create
            destroy
            getattr
            setattr
            read
            write
            associate
            unix_read
            unix_write
    }


.. _security-attributes:

Security attributes
~~~~~~~~~~~~~~~~~~~

In order to meet the requirements of many different policy models, SELinux
defines a number of security attributes which can be associated with entities.
These attributes together create a **security label** (or context) which is
what we see associated with files and processes via ``ls -Z`` and ``ps -Z``
respectively.

.. code-block:: txt 
    :caption: Output of ps -Z with annotated security attributes
    
    
    unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 11837 pts/17 00:00:00 bash
         ^            ^            ^            ^
        user        role         type      mls level
    

These security attributes on their own don't mean much until they are used in
policy, however each attribute has a number of different mechanisms which can
be applied to it to create access-control models.

User
````

Not to be confused with Linux users, the user attribute is the glue between
SELinux users declared in policy and Linux logins.  Userspace configuration files
map login names to SELinux users, and the userspace selinux library uses
these to resolve security attributes for Linux logins.

An example of this is ``pam_selinux``, which uses the login name of the user
to find a default set of security attributes to use for security label of the users
session.

Role
````

The role attribute allows policy authors to implement Role-Based Access Control
by associating roles with SELinux users and restricting what roles a user can
transition between.  Each of these roles can be constrained in policy,
and associated/unassociated with a user dynamically to add or reduce the total
set of permissions a user has.

Type
````

Much like the relationship between users and roles, types are associated with
roles, further complementing Role-Based Access Control by restricting the types
that a role can be allowed to perform operations on.

Unlike users and roles however, operations between two types can be constrained
using a rich policy language feature known as **type-enforcement**.

.. code-block:: c
    :caption: Type-enforcement rules allowing access to permissions on the capability and file security classes.
    
    allow init_t self : capability { mac_admin };
    allow init_t bin_t : file { exec };

Multi-Level Security Range
``````````````````````````

The Multi-Level Security Level attribute is different from the previous attributes
mentioned, in that it is a range containing several nested attributes.  The range
consists of *low* and *high* components, each containing a **sensitivity** level
and optionally **categories**.

The sensitivity attribute is often used to define a clearance level to maintain
confidentiality in information flow.  Policy authors can write constraints that
have the ability to compare the low and high sensitivity levels of source and
target entities and act accordingly.  The Multi-Level Security model in SELinux
was built with the Bell–LaPadula model in mind, however, can be extended
very easily by the policy author.

The category attribute is used for a simpler implementation of Multi-Level
Security known as Multi-Category Security.  By associating a set of categories
with an entity, a policy author can prevent an entity that isn't associated
with the same categories from interacting with it.  This has been used in both
Red Hat and Android policy models for isolation/compartmentalization of
virtual machines (sVirt) and sandboxing of user applications respectively.

Confining entities
~~~~~~~~~~~~~~~~~~

Type-enforcement rules
``````````````````````

The foundation of access control in SELinux is the previously mentioned
type-enforcement rules.  A simple way to identify the permissions a user has
would be to look at all type-enforcement rules that have a source type
associated with one of the users roles.  By whitelisting what an entity can do,
it is very to reason about what operations are allowed on the system.

Constrain expressions
``````````````````````

Constrain expressions are much more powerful than type-enforcement rules and allow
the policy author to write arbitrary expressions with predicates that operate
on all of an entities security attributes.

.. code-block:: c
    :caption: A constrain expression which compares the user and type attributes of the source and target entities in a security check for several permissions on the process security class
    
    constrain process { transition dyntransition noatsecure siginh rlimitinh }
    (
    	u1 == u2
    	or ( t1 == can_change_process_identity and t2 == process_user_target )
           	or ( t1 == cron_source_domain and ( t2 == cron_job_domain or u2 == system_u ) )
    	or ( t1 == can_system_change and u2 == system_u )
    	or ( t1 == process_uncond_exempt )
    );

Transitions
```````````

Transitions are used in SELinux policy to allow entities to transition roles,
types, sensitivity levels, or categories whenever a new program is executed or new
object is created.  This is the basis of privilege separation, by transitioning
to a new, and possibly limited, set of security attributes when running a
program or creating a new object.

The most common security attributes used in transitions are types, in order to
transition to a domain with a different set of type-enforcement rules.  Since
it could be desirable to change the type depending on how a program was
executed (e.g., a service executed by init vs a user) transitions allow the
policy author to determine the target type based on the types of the program
requesting the transition and the file which was executed.

::
    
    type_transition init_t service_exec_t:process service_t;
    type_transition user_t service_exec_t:process user_service_t;
                      ^             ^         ^          ^
                  source type  target type    |   new type after transition
                                              |
                                        security class


However, as mentioned type transitions are also applicable to when new objects are
created and can be used to determine the type of a newly created object, additionally
with a specified filename.

::
    
    type_transition init_t service_dir_t:file service_file_t;
    type_transition init_t service_dir_t:file service_priv_file_t "private_file";

These transitions above determine the type of a newly created file object with a parent
directory that has a label type of ``service_dir_t``.  The "private_file" addition in
the second rule is a filename which is checked during transition.  If the name of the
file being created matches this, then ``service_priv_file_t`` will be used instead of
``service_file_t``.

Common misconceptions
---------------------

What is SELinux not?
--------------------

To summarize, SELinux is a framework for building mandatory access control
policies using a number of different security attributes.  Quite often people
ask "How do the grsecurity patches compare with SELinux?" and the answer is:
most of the features provided by grsecurity don't.  Grsecurity is primarily
concerned with kernel safety, while SELinux is concerned with restricting
information flow and the permissions users and programs have.  The grsecurity
patches can be used to complement SELinux for assurance that the in-kernel
security server hasn't been exploited.

The exception is the Role-Based Access Control model that grsecurity provides which
could be compared to SELinux policy to some extent. Their implementation does
not use the LSM framework and hooks into kernel code directly, giving some more
flexibilty of what permissions can be checked, with the drawback of a simpler
policy language.
