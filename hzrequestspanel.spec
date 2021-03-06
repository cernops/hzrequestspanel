%global cern_version CERN_VERSION_PLACEHOLDER
%global cern_release CERN_RELEASE_PLACEHOLDER

%global pypi_name hzrequestspanel

%if 0%{?fedora}
%global with_python3 1
%endif

Name:		python-%{pypi_name}
Version:    %{cern_version}
Release:    %{cern_release}%{?dist}
Summary:	OpenStack Dashboard panel plugin for Service Now requests

License:	ASL 2.0
URL:		https://gitlab.cern.ch/mferminl/hzrequestspanel
Source0:	python-%{pypi_name}-%{version}.tar.gz

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
%autosetup -n python-%{pypi_name}-%{version}
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

%pretrans
systemctl stop httpd

%install
%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %{__python3} setup.py install --skip-build --root %{buildroot}
popd
%endif

%{__python2} setup.py install --skip-build --root %{buildroot}

# Install enabled file for the plugin
# install -p -D -m 640 etc/%{pypi_name}.conf %{buildroot}/etc/openstack-dashboard/%{pypi_name}.conf
install -p -D -m 640 enabled/_1021_project_hzrequests_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py
install -p -D -m 640 enabled/_6868_project_remove_overview_panel.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py

%posttrans
systemctl start httpd

%files -n python2-%{pypi_name}
%license LICENSE
%doc README.md
%{python2_sitelib}/%{pypi_name}*
%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py*
# %attr(0644, apache, apache) /etc/openstack-dashboard/%{pypi_name}.conf

# Files for python3
%if 0%{?with_python3}
%files -n python3-%{pypi_name} 
%license LICENSE
%doc doc/source/readme.rst README.rst
%{python3_sitelib}/%{pypi_name}*
%{_datadir}/openstack-dashboard/openstack_dashboard/enabled/_1021_project_hzrequests_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_6868_project_remove_overview_panel.py*
# %attr(0644, apache, apache) /etc/openstack-dashboard/%{pypi_name}.conf
%endif

%changelog
* Wed Dec 20 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.4-13
- Add GBAR to the list of experiments

* Mon Nov 13 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.4-9
- Support for volume type quotas in new project request
- Support for multiple e-groups in new project request

* Mon Sep 04 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.4-1
- Support for SnowClientV2

* Fri Jun 30 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.2-1
- Create SNOW ticket directly against target Functional Element

* Wed Jun 14 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.1-1
- Add unit tests, refactor code and release Delete and Create Project forms

* Thu Jun 08 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.0-10
- Added Delete Project Request form

* Wed May 10 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 2.0-1
- Complete refactoring of this code
- Added Create New Project Request form

* Tue May 09 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 1.6-1
- Fix link to Quota History Dashboard (force selecting organization)

* Tue Mar 07 2017 Mateusz Kowalski <mateusz.kowalski@cern.ch> 1.5-1
- Automatically restart httpd when upgrading package

* Wed Dec 07 2016 Daniel Fernandez Rodriguez <danielfr@cern.ch> 1.2-1
- Prefill job URL with snow_ticket
- Query Active Directory to check if user existance

* Fri Nov 04 2016 Mateusz Kowalski <mateusz.kowalski@cern.ch> 1.0-3
- Merge changes from Horizon newton

* Thu Sep 22 2016 Daniel Fernandez Rodriguez <danielfr@cern.ch> 1.0-1
- Change quota update request worknote message
- Add Makefile.koji to project

* Thu Jun 23 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.2-3
- OS-3092 Improve error message for request quota change action

* Wed Jun 15 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.2-2
- Fix RAM data to send (OS-2873) and set proper % when the initial value is 0

* Wed May 04 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.2-1
- OS-2873 Escalate request quota change SNOW ticket

* Wed Mar 23 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.1-5
- Change ng-mouse and ng-change to ng-blur in volume type inputs

* Thu Mar 10 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.1-4
- Fix + char in compute % values
- Align left volume list headers

* Thu Jan 14 2016 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> 0.1-3
- First RPM
