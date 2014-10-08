installer_iso = File.join(Chef::Config[:file_cache_path], 'padb.iso')
installer_mount = node['matrix']['installer_mount']

phase1 = '/root/.p1'
phase2 = '/root/.p2'

unless File.exist?(phase1)
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

  # Phase 1 Install
  # 1 - Complete setup
  include_recipe 'python'

  %w(setuptools pexpect argh).each do |pkg|
    python_pip pkg do
      action :upgrade
    end
  end

  setup_file = File.join(Chef::Config[:file_cache_path], 'setup.py')

  remote_file setup_file do
    owner 'root'
    group 'root'
    mode '0700'
    source node['matrix']['setup_script']
  end

  execute 'Perform phase 1 of Matrix install' do
    command <<-EOH
      python #{setup_file} phase1 \
      --installer #{File.join(installer_mount, 'install_padb')} \
      --leader-ip #{node['matrix']['leader_ip']} \
      --compute-nodes #{node['matrix']['compute_nodes'].join(',')} \
      --root-password #{node['matrix']['root_password']} \
      --leader-count #{node['matrix']['leader_count']}
    EOH
  end
  # 2 - Unmount iso, delete
  execute "umount #{installer_mount}"
  file 'installer_mount' do
    action :delete
  end
  execute "touch #{phase1}"
end

unless File.exist?(phase2)
  # Patch files
  include_recipe 'matrix::patch'

  # Phase 2 Install
  # 1 - Apply kernel params (sysctl -p /etc/sysctl.conf)
  execute 'sysctl -p /etc/sysctl.conf || true'

  # 2 - Create RAMdisk
  execute 'mount -a ; chown -R paraccel:paraccel /mnt/ramdisk'

  # 3 - start daemontools
  service 'padb-daemontools' do
    provider Chef::Provider::Service::Upstart
    action :start
  end

  execute 'Perform phase 2 of Matrix install' do
    command <<-EOH
      python #{setup_file} phase2 \
      --password #{node['matrix']['paraccel_password']}
    EOH
  end
  # 4 - Run phase 2 setup as paraccel user
  execute "touch #{phase2}"
end
