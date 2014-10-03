installer_iso = File.join(Chef::Config[:file_cache_path], 'padb.iso')
installer_mount = '/mnt'

user node['matrix']['user']
group node['matrix']['group']

node['matrix']['packages'].each do |pkg|
  package pkg
end

remote_file installer_iso do
  source node['matrix']['iso_url']
  not_if { ::File.exist?(installer_iso) }
end

execute "mount installer" do
  command "mount -o loop #{installer_iso} #{installer_mount}"
  not_if { ::File.exist?(File.join(installer_mount, 'install_padb')) }
end
