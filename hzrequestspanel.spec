%global pypi_name hzrequestspanel

%if 0%{?fedora}
%global with_python3 1
%{!?python3_shortver: %global python3_shortver %(%{__python3} -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))')}
%endif

Name:		python-%{pypi_name}
Version:	0.1
Release:	1%{?dist}
Summary:	OpenStack Dashboard panel plugin for Service Now requests

License:	ASL 2.0
URL:		https://gitlab.cern.ch/mferminl/hzrequestspanel
Source0:	%{pypi_name}-%{version}.tar.gz

BuildRequires:	python2-devel

Requires:       cci-tools
Requires:	openstack-dashboard
Requires:	python-django
Requires:	python-django-horizon
Requires:	python-keystoneclient
Requires:	python-cinderclient
Requires:	python-novaclient

%description
OpenStack Dashboard plugin to create a new panel, under Project dashboard, to manage Requests to Service Now

%package -n     python2-%{pypi_name}
Summary:        OpenStack Dashboard panel plugin for Service Now requests
%{?python_provide:%python_provide python2-%{pypi_name}}

%description -n python2-%{pypi_name}
OpenStack Dashboard plugin to create a new panel, under Project dashboard, to manage Requests to Service Now

# Python3 package
%if 0%{?with_python3}
%package -n     python3-%{pypi_name}
Summary:        OpenStack Dashboard panel plugin for Service Now requests
%{?python_provide:%python_provide python3-%{pypi_name}}

BuildRequires:  python3-devel

Requires:	ccitools
Requires:       openstack-dashboard
Requires:       python3-django
Requires:       python3-django-horizon
Requires:       python3-keystoneclient
Requires:       python3-cinderclient
Requires:       python3-novaclient


%description -n python3-%{pypi_name}
OpenStack Dashboard plugin to create a new panel, under Project dashboard, to manage Requests to Service Now
%endif

%prep
%autosetup -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
2to3 --write --nobackups %{py3dir}
%endif

%build
%{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %{__python3} setup.py build
popd
%endif

%install
%{__python2} setup.py install --skip-build --root %{buildroot}

%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %{__python3} setup.py install --skip-build --root %{buildroot}
mv %{buildroot}%{_bindir}/%{pypi_name} %{buildroot}%{_bindir}/python3-%{pypi_name}
popd
%endif

# rename binaries, make compat symlinks
pushd %{buildroot}%{_bindir}
%if 0%{?with_python3}
for i in %{pypi_name}-{3,%{?python3_shortver}}; do
    ln -s  python3-%{pypi_name} $i
done
%endif
popd

# Install enabled file for the plugin
install -p -D -m 640 enabled/_6970_project_hzrequests_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6970_project_hzrequests_panel.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_6970_project_hzrequests_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6970_project_hzrequests_panel.py

%files -n python2-%{pypi_name}
%license LICENSE
%doc README.rst
%{python2_sitelib}/hzrequestspanel*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6970_project_hzrequests_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_6970_project_hzrequests_panel.py*

%files
%{_bindir}/%{pypi_name}*

# Files for python3
%if 0%{?with_python3}
%files -n python3-%{pypi_name}
%license LICENSE
%doc README.rst
%{_bindir}/python3-%{pypi_name}
%{_bindir}/%{pypi_name}*
%{python3_sitelib}/hzrequestspanel*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6970_project_hzrequests_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_6970_project_hzrequests_panel.py*
%endif


%changelog
* Thu Jan 14 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> - 0.1-1
- First RPM
