%define	name	plan
%define	version	1.10.1
%define	release	%mkrel 1
%define summary A day planner

Name:		%{name} 
Summary:	%{summary}
Version:	%{version} 
Release:	%{release} 
Source0:	ftp://ftp.fu-berlin.de/unix/X11/apps/plan/%{name}-%{version}.tar.gz
# Additional source for Norwegian translation which is not in the main distribution of plan yet
Source1:	%{name}.lang.norwegian.bz2
# Adds a launch script for plan and Mandriva Linux standards to the configure script
Patch0:		plan-configure-and-launchscript.patch
URL:		http://www.bitrot.de/plan.html
Group:		Office
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
License:	GPL
BuildRequires:	lesstif-devel 
BuildRequires:  ImageMagick 
BuildRequires:  X11-devel 
BuildRequires:  bison
BuildRequires:  flex

%description
plan is a schedule planner based on X/Motif. It displays a month calendar
similar to xcal, but every day box is large enough to show appointments in
small print. By pressing on a day box, the appointments for that day can be
listed and edited. Appointments are entered with the following
information (everything except the date is optional):

 * the date, time, and length (time and days) of the appointment,
 * an optional text message to be printed,
 * an optional script to be executed,
 * early-warn and late-warn triggers that precede the alarm time
 * repetitions: [n-th] weekdays, days-of-the-month, every n days, yearly
 * optional fast command-line appointment entry
 * flexible ways to specify holidays and vacations
 * extensive context help
 * multiuser capability using an IP server program (with access lists),
 * grouping of appointments into files, per-user, private, and others 

%package netplan
Summary:	Netplan server for plan
URL:		http://www.bitrot.de/plan.html
Group:		Office
License:	GPL

%description netplan
netplan enables plan to be multiuser using an IP server.

WARNING: This is very insecure. The best level of authentication
offered by netplan (in this version) is identd. That is quite weak,
so if you're going to use it you should read the manpage and
configure it carefully.

netplan is not required to use plan.

%package tools
Summary:	Various tools for use with plan
URL:		http://www.bitrot.de/plan.html
Group:		Office
License:	GPL

%description tools
This package contains various tools for use with plan:

msschedule2plan - A perl script that converts Microsoft Schedule+
                  exports CSV files to .dayplan files
plan2vcs        - A perl script that converts a netplan file
                  to vcalendar

%prep
%setup -q
cd src
%patch -p0
cd ..

%build
cd ./src
# It has a non-standard configure script - 6 tells it to use Mandriva Linux standards
# The libdir part is a hack to make rpmlint shut up about no-libdir-spec
./configure 6 ;echo "--libdir=%{_libdir}" > /dev/null
# (tv) fix build on x86_64:
perl -pi -e "s,-L/usr/X11R6/lib,-L/usr/X11R6/%_lib," Makefile

# Stupid upstream authors try to force 32-bit compilation on x86-64...
%ifarch x86_64
%make linux64
%else
%make
%endif

bunzip2 -c %SOURCE1 > ../language/plan.lang.norwegian

%install
rm -rf $RPM_BUILD_ROOT
# Install the launchscript in %{_bindir} and the executeable itself in %{_libdir}
install -m755 ./src/plan.bash -D $RPM_BUILD_ROOT%{_bindir}/plan
install -m755 ./src/plan -D $RPM_BUILD_ROOT%{_libdir}/plan/plan

install -m755 ./src/pland -D $RPM_BUILD_ROOT%{_bindir}/pland
install -m755 ./src/netplan -D $RPM_BUILD_ROOT%{_bindir}/netplan
mkdir -p $RPM_BUILD_ROOT%{_libdir}/plan/
install -m755 ./src/notifier $RPM_BUILD_ROOT%{_libdir}/plan/
install -m644 ./language/* $RPM_BUILD_ROOT%{_libdir}/plan/
mkdir -p $RPM_BUILD_ROOT%{_libdir}/plan/holidays/
install -m644 ./holiday/* -D $RPM_BUILD_ROOT%{_libdir}/plan/holidays/
# Norwegian support is not included in the main distribution yet
# %{__bunzip2} --stdout %SOURCE1 > $RPM_BUILD_ROOT%{_libdir}/plan/plan.lang.norwegian
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/ $RPM_BUILD_ROOT%{_mandir}/man4/
install -m644 ./misc/plan.1 $RPM_BUILD_ROOT%{_mandir}/man1/
install -m644 ./misc/plan.4 $RPM_BUILD_ROOT%{_mandir}/man4/
install -m644 ./misc/netplan.1 $RPM_BUILD_ROOT%{_mandir}/man1/
install -m755 ./misc/msschedule2plan  $RPM_BUILD_ROOT%{_bindir}/msschedule2plan
sed -e s,'/usr/local/bin/perl','/usr/bin/perl',g ./misc/plan2vcs > $RPM_BUILD_ROOT%{_bindir}/plan2vcs
chmod 755 $RPM_BUILD_ROOT%{_bindir}/plan2vcs
install -m644 ./misc/*ps $RPM_BUILD_ROOT%{_libdir}/plan/

# Convert the xpm icon to png and 48x48
convert -resize 48x48 ./misc/plan.xpm ./misc/plan-48.png
# Provide a 16x16 icon
convert ./misc/plan-48.png -resize 16x16 ./misc/plan-16.png
# Provice a 32x32 icon
convert ./misc/plan-48.png -resize 32x32 ./misc/plan-32.png
install -m644 ./misc/plan-32.png -D $RPM_BUILD_ROOT%{_iconsdir}/hicolor/32x32/apps/plan.png
install -m644 ./misc/plan-16.png -D $RPM_BUILD_ROOT%{_iconsdir}/hicolor/16x16/apps/plan.png
install -m644 ./misc/plan-48.png -D $RPM_BUILD_ROOT%{_iconsdir}/hicolor/48x48/apps/plan.png

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=Plan
Comment=A graphical day planner
Exec=%{_bindir}/%{name} 
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=Motif;Office;ProjectManagement;
EOF

%post
%{update_menus}
%{update_icon_cache hicolor}

%postun
%{clean_menus}
%{clean_icon_cache hicolor}

%clean 
rm -rf $RPM_BUILD_ROOT 

%files 
%defattr(-,root,root)
%doc HISTORY README
%{_bindir}/plan
%{_bindir}/pland
%{_libdir}/plan/*
%{_mandir}/man1/plan.1*
%{_mandir}/man4/plan.4*
%{_iconsdir}/hicolor/16x16/apps/plan.png
%{_iconsdir}/hicolor/32x32/apps/plan.png
%{_iconsdir}/hicolor/48x48/apps/plan.png
%{_datadir}/applications/mandriva-%{name}.desktop

%files netplan
%defattr(-,root,root)
%{_bindir}/netplan
%{_mandir}/man1/netplan.1*

%files tools
%defattr(-,root,root)
%{_bindir}/msschedule2plan
%{_bindir}/plan2vcs
