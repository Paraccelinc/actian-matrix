Description
===========

Test template for Matrix training

Requirements
============
* A Heat provider that supports the following:
  * OS::Heat::ChefSolo
  * OS::Heat::RandomString
  * OS::Heat::ResourceGroup
  * OS::Nova::KeyPair
  * Rackspace::Cloud::Server
* An OpenStack username, password, and tenant id.
* [python-heatclient](https://github.com/openstack/python-heatclient)
`>= v0.2.8`:

```bash
pip install python-heatclient
```

We recommend installing the client within a [Python virtual
environment](http://www.virtualenv.org/).

Example Usage
=============
Here is an example of how to deploy this template using the
[python-heatclient](https://github.com/openstack/python-heatclient):

```
heat --os-username <OS-USERNAME> --os-password <OS-PASSWORD> --os-tenant-id \
  <TENANT-ID> --os-auth-url https://identity.api.rackspacecloud.com/v2.0/ \
  stack-create My-Matrix-Deployment -f matrix.yaml \
  -P iso_url="http://example.com/path/to/installer.iso" \
  -P ip_patch="http://example.com/path/to/sys_check.py"
```

* For UK customers, use `https://lon.identity.api.rackspacecloud.com/v2.0/` as
the `--os-auth-url`.

Optionally, set environmental variables to avoid needing to provide these
values every time a call is made:

```
export OS_USERNAME=<USERNAME>
export OS_PASSWORD=<PASSWORD>
export OS_TENANT_ID=<TENANT-ID>
export OS_AUTH_URL=<AUTH-URL>
```

Parameters
==========
Parameters can be replaced with your own values when standing up a stack. Use
the `-P` flag to specify a custom parameter.

* `iso_url`: (Default: '')
* `ip_patch`: (Default: '')
* `image`: (Default: CentOS 6.5)
* `setup_script`: (Default: https://raw.githubusercontent.com/brint/actian-matrix/master/scripts/config.py)
* `compute_flavor`: Required: Rackspace Cloud Server flavor to use. The size is based on the
amount of RAM for the provisioned server.
 (Default: 60 GB Performance)
* `network_range`: Private Network to use for Matrix Communication (Default: 192.168.224.0/20)
* `compute_hostname`: (Default: Matrix-Compute-%index%)
* `leader_flavor`: Required: Rackspace Cloud Server flavor to use. The size is based on the
amount of RAM for the provisioned server.
 (Default: 8 GB Performance)
* `compute_server_count`: (Default: 1)
* `chef_version`: Version of chef client to use (Default: 11.16.2)
* `child_template`: (Default: https://raw.githubusercontent.com/brint/actian-matrix/master/matrix-compute.yaml)
* `kitchen`: URL for the kitchen to use, fetched using git
 (Default: https://github.com/brint/actian-matrix)

Outputs
=======
Once a stack comes online, use `heat output-list` to see all available outputs.
Use `heat output-show <OUTPUT NAME>` to get the value of a specific output.

* `leader_ip`:
* `paraccel_password`:
* `private_key`: SSH Private Key
* `compute_ips`:
* `root_password`:

For multi-line values, the response will come in an escaped form. To get rid of
the escapes, use `echo -e '<STRING>' > file.txt`. For vim users, a substitution
can be done within a file using `%s/\\n/\r/g`.
