name 'matrix'
maintainer 'Brint O\'Hearn'
maintainer_email 'brint.ohearn@rackspace.com'
license 'Apache 2.0'
description 'Installs/Configures Matrix'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version '0.1.0'

depends 'python'

%w(centos redhat).each do |os|
  supports os
end
