installer_iso = File.join(Chef::Config[:file_cache_path], 'padb.iso')

remote_file installer_iso do
  source node['matrix']['iso_url']
  not_if { ::File.exist?(installer_iso) }
end

mount installer_iso do
  mount_point '/mnt'
  options 'loop'
  action :mount
end
