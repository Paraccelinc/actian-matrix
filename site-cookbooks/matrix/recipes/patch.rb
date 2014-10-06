# Applies patch for sys_check.py where nodes are not in the same /24

if node['matrix']['ip_patch']
  file '/home/paraccel/scripts/sys_check.py' do
    action :delete
  end

  remote_file '/home/paraccel/scripts/sys_check.py' do
    owner 'paraccel'
    group 'paraccel'
    mode '0755'
    source node['matrix']['ip_patch']
  end
end
