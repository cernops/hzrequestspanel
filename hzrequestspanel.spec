%global pypi_name hzrequestspanel

%if 0%{?fedora}
%global with_python3 1
%endif

Name:		python-%{pypi_name}
Version:	0.1
Release:	2%{?dist}
Summary:	OpenStack Dashboard panel plugin for Service Now requests

License:	ASL 2.0
URL:		https://gitlab.cern.ch/mferminl/hzrequestspanel
Source0:	%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:	python2-devel
BuildRequires:  python-setuptools

%description
OpenStack Dashboard plugin to create a new panel, under Project dashboard, to manage Requests to Service Now

%package -n     python2-%{pypi_name}
Summary:        OpenStack Dashboard panel plugin for Service Now requests
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires: cci-tools
Requires: openstack-dashboard
Requires: python-django
Requires: python-django-horizon
Requires: python-keystoneclient
Requires: python-cinderclient
Requires: python-novaclient

%description -n python2-%{pypi_name}
OpenStack Dashboard plugin to create a new panel, under Project dashboard, to manage Requests to Service Now

# Python3 package
%if 0%{?with_python3}
%package -n     python3-%{pypi_name}
Summary:        OpenStack Dashboard panel plugin for Service Now requests
%{?python_provide:%python_provide python3-%{pypi_name}}

BuildRequires:  python3-devel

Requires:       cci-tools
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
%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %{__python3} setup.py install --skip-build --root %{buildroot}
popd
%endif

%{__python2} setup.py install --skip-build --root %{buildroot}

# Install enabled file for the plugin
install -p -D -m 640 etc/%{pypi_name}.conf %{buildroot}/etc/openstack-dashboard/%{pypi_name}.conf
install -p -D -m 640 enabled/_1021_project_hzrequests_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py
install -p -D -m 640 enabled/_6868_project_remove_overview_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py

%files -n python2-%{pypi_name}
%license LICENSE
%doc README.md
%{python2_sitelib}/%{pypi_name}*
%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py*
%attr(0644, apache, apache) /etc/openstack-dashboard/%{pypi_name}.conf

# Files for python3
%if 0%{?with_python3}
%files -n python3-%{pypi_name} 
%license LICENSE
%doc doc/source/readme.rst README.rst
%{python3_sitelib}/%{pypi_name}
%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py*
%attr(0644, apache, apache) /etc/openstack-dashboard/%{pypi_name}.conf
%endif

%changelog
* Thu Jan 14 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.1-2
- First RPM
