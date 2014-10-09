yum_package 'glibc' do
  arch 'i686'
end

node['matrix']['packages'].each do |pkg|
  package pkg
end
