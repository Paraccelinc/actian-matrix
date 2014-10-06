installer_iso = File.join(Chef::Config[:file_cache_path], 'padb.iso')
installer_mount = node['matrix']['installer_mount']

unless File.exist?('/home/paraccel/install_padb')
  directory installer_mount do
    owner 'root'
    group 'root'
    mode '0700'
    action :create
    not_if { File.exist?(installer_mount) }
  end

  yum_package 'glibc' do
    arch 'i686'
  end

  node['matrix']['packages'].each do |pkg|
    package pkg
  end

  remote_file installer_iso do
    source node['matrix']['iso_url']
    not_if { ::File.exist?(installer_iso) }
  end

  execute 'mount installer' do
    command "mount -o loop #{installer_iso} #{installer_mount}"
    not_if { ::File.exist?(File.join(installer_mount, 'install_padb')) }
  end
end

# Phase 1 Install
# 1 - Complete setup
# 2 - Unmount iso, delete

# Patch files
include_recipe 'matrix::patch'

# Phase 2 Install
# 1 - Apply kernel params (sysctl -p /etc/sysctl.conf)
execute 'sysctl -p /etc/sysctl.conf'

# 2 - Create RAMdisk (create directory, mount -a, chown)
directory node['matrix']['ramdisk']

execute 'mount -a ; chown -R paraccel:paraccel /mnt/ramdisk'

# 3 - start daemontools
# 4 - Run phase 2 setup as paraccel user
