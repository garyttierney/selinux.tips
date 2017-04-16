SELinux Policy Language
=======================

Kernel Policy Language
----------------------

Reference Policy
~~~~~~~~~~~~~~~~

This provides a more expressive language to the policy author which usually
requires only minimal interaction with the kernel policy language.  This is
what is shipped by major distrbutions today (Fedora, Hardened Gentoo, Debian)
and is a major improvement in user experience, but sacrifices semantics of the
policy language for M4 macros.  A recent addition to SELinux userspace (in 2.4)
made it possible to replace the M4 policy abstraction with a Common
Intermediate Language which a High-Level Language could compile down to.

.. _common-intermediate-language:

Common Intermediate Language
----------------------------

Exploring the features of CIL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you compare the featureset of CIL to the abstractions used in Reference Policy, you can
that there is almost feature-parity.  For each abstraction in the reference policy, CIL has
a language construct to match it.  Here we'll look at the most prominent features and compare
them to their reference policy equivalents.

Namespaces
``````````

In CIL there is a way to namespace policy, by placing it in a `block`.  Anything declared in
a block can be accessed by it's fully qualified name such as `block_name.symbol_name`.  
Beyond a method for organizing policy, blocks also provide multiple-inheritance, much like in {cpp}.

.. code-block:: lisp
    
    (block abstract_block
    	(type subj)
    	(blockabstract abstract_block) <1>
    )
    
    (block abstract_block_b
    	(block files
    		(type obj)
    	)
    )
    
    (block concrete_block
    	(blockinherit abstract_block) <2>
    	(blockinherit abstract_block_b)
    )

<1> `blockabstract` declares a namespace as abstract, and able to be inherited from.
<2> `blockinherit` copies the namespace in its argument into the current namespace.

This one little feature gives us a great way to create reusable blocks of policy.  Not only
that, but any tool capable of parsing CIL can quickly visualize the tree of all namespaces in the
policy to give a policy analyst a quick overview of what's going on.

Although reference policy does not provide a similar mechanism for namespacing policy,
it does provide a way to create reusable blocks of policy via templates:

.. code-block:: spt
    
    ######################################
    ## <summary>
    ##  The template to define a domain to which sshd dyntransition.
    ## </summary>
    ## <param name="domain">
    ##  <summary>
    ##  The prefix of the dyntransition domain
    ##  </summary>
    ## </param>
    #
    template(`ssh_dyntransition_domain_template',`
    	gen_require(`
    		attribute ssh_dyntransition_domain;
    	')
    
    	type $1, ssh_dyntransition_domain;
    	domain_type($1)
    	role system_r types $1;
    	
    	optional_policy(`
    		ssh_dyntransition_to($1)
    	')
    ')

Templates in reference policy work just like abstract blocks in CIL, but lack
the semantics and structure of a CIL namespace.

Class Mappings
```````````````

By default the kernel policy language provides no way to group common access
vectors (classes and their permissions).  So Reference Policy compensates
for this by defining support macros for common sets of permissions.  These can
be found in policy/support/ in the base policy of any Reference Policy fork.

.. code-block:: spt
    
    :name: ./policy/support/obj_class_perms.spt
    #
    # Regular file (file)
    #
    define(`getattr_file_perms',`{ getattr }')
    define(`setattr_file_perms',`{ setattr }')
    define(`read_inherited_file_perms',`{ getattr read ioctl lock }')
    define(`read_file_perms',`{ open read_inherited_file_perms }')
    define(`mmap_file_perms',`{ getattr open read execute ioctl }')
    define(`exec_file_perms',`{ getattr open read execute ioctl execute_no_trans }')
    define(`append_inherited_file_perms',`{ getattr append }')
    define(`append_file_perms',`{ open lock ioctl append_inherited_file_perms }')
    define(`write_inherited_file_perms',`{ getattr write append lock ioctl }')
    define(`write_file_perms',`{ open write_inherited_file_perms }')
    define(`rw_inherited_file_perms',`{ getattr read write append ioctl lock }')
    define(`rw_file_perms',`{ open rw_inherited_file_perms }')
    define(`create_file_perms',`{ getattr create open }')
    define(`rename_file_perms',`{ getattr rename }')
    define(`delete_file_perms',`{ getattr unlink }')
    define(`manage_file_perms',`{ create open getattr setattr read write append rename link unlink ioctl lock }')
    define(`relabelfrom_file_perms',`{ getattr relabelfrom }')
    define(`relabelto_file_perms',`{ getattr relabelto }')
    define(`relabel_file_perms',`{ getattr relabelfrom relabelto }')

Macros
``````

Expanded attribute support
``````````````````````````

Object labeling improvements
````````````````````````````

CIL gets rid of the need to maintain separate type enforcement and file contexts files,
in addition to supporting port context declarations within policy modules.  Previously we'd
have to declare file context specifications separately in a `.fc` file and port context
specifications would be generated when building the base policy or added later by an
administrator using `semanage`.


High-Level Language Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The High Level Language Infrastructure gave a new way for SELinux tool
developers to create policy abstractions.  Instead of m4, policy could compile
to CIL which retains all the semantics of the source policy (including macros,
templates, etc., which is not the case in the reference policy, instead requiring
policy sources and a custom Makefile available to use macros).

To date there are no working examples of a HLL compiler which targets CIL, though
it was demonstrated by Tresys Technology in their `lolpolicy <http://selinuxproject.org/~jmorris/lss2010_slides/lolpolicy.pptx>`_.

The diagram below details how module policy packages (.pp files) fit into the High
Level Language Infrastructure, as well as how CIL and any other HLL's fit
into the toolchain.

.. graphviz::
    
    digraph HLL {
      node [shape="box"];
    
      subgraph cluster_kernelpolicy {
        label="Kernel Policy Language";
        module_pp [style="rounded", label="module.pp"];
        module_makefile [label="/usr/share/selinux/devel/Makefile"]
    
        module_src [style="rounded", label="module.fc, module.te"];
        module_mod [style="rounded", label="module.mod"];
    
        module_src -> {module_makefile, checkmodule};
    
        module_makefile->module_pp;
        checkmodule->module_mod;
    
        module_mod -> semodule_package;
        semodule_package->module_pp;
      }
    
      module_hll [style="rounded", label="module.my_hll_ext"];
      module_pp -> semodule;
      module_hll -> semodule;
    
      pp_2_cil [label="/usr/libexec/selinux/hll/pp"];
      my_hll_ext_2_cil [label="/usr/libexec/selinux/hll/my_hll_ext"]
    
      semodule [label="semodule / libsemanage", xlabel="semodule will recompile the entire policy store \n to CIL when importing a new module and \n rebuild a binary policy as well \n as file_contexts "];
      semodule -> {pp_2_cil, my_hll_ext_2_cil};
      semodule -> secilc [label="semodule can import CIL modules\n and link them with other modules directly"];
      secilc [label="CIL compiler"];
      {pp_2_cil, my_hll_ext_2_cil} -> secilc;
    
      binary_policy [style="rounded", label="policy.30"];
      file_contexts [style="rounded", label="file_contexts"];
    
      secilc -> {binary_policy, file_contexts};
    }


