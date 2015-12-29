ops_tools
=========

Installs tools useful for ops analysis and problem diagnosis.

Requirements
------------

None.

Role Variables
--------------

`_ops_tools.tools` contains a list of tools to install. By default, the following packages will be installed:

- sysstat for `iostat`

- iotop

- sysdig

If sysdig is part of the tools list, the corresponding Draios repository is automatically added.

Dependencies
------------

None.

Example Playbook
----------------

```
    - hosts: servers
      vars:
        OPS_TOOLS:
          tools:
            - sysstat
            - iotop
            - sysdig
      roles:
        - { role: ops_tools, tags: [ 'ops_tools' ], _ops_tools: "{{ OPS_TOOLS }}" }
```

License
-------

See LICENSE file.

Author Information
------------------

Initially created by Lukas Pustina [@drivebytesting](https://twitter.com/drivebytesting).

