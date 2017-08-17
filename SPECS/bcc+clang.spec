#lua jit not available for some architectures
%ifarch ppc64 aarch64 ppc64le
%{!?with_lua: %global with_lua 0}
%else
%{!?with_lua: %global with_lua 1}
%endif
%define debug_package %{nil}
%define llvmver 3.7.1

Name:          bcc
Version:       @REVISION@
Release:       @GIT_REV_COUNT@
Summary:       BPF Compiler Collection (BCC)

Group:         Development/Languages
License:       ASL 2.0
URL:           https://github.com/iovisor/bcc
Source0:       https://github.com/iovisor/bcc/archive/v%{version}.tar.gz
Source1:       http://llvm.org/releases/%{llvmver}/llvm-%{llvmver}.src.tar.xz
Source2:       http://llvm.org/releases/%{llvmver}/cfe-%{llvmver}.src.tar.xz

ExclusiveArch: x86_64 ppc64 aarch64 ppc64le
BuildRequires: bison, cmake >= 2.8.7, flex, gcc, gcc-c++, libxml2-devel, python2-devel, elfutils-libelf-devel-static
%if %{with_lua}
BuildRequires: luajit luajit-devel
%endif

%if %{with_lua}
%global lua_include `pkg-config --variable=includedir luajit`
%global lua_libs `pkg-config --variable=libdir luajit`/lib`pkg-config --variable=libname luajit`.so
%global lua_config -DLUAJIT_INCLUDE_DIR=%{lua_include} -DLUAJIT_LIBRARIES=%{lua_libs}
%endif

%description
Python bindings for BPF Compiler Collection (BCC). Control a BPF program from
userspace.

%prep
%setup -q -T -b 1 -n llvm-%{llvmver}.src
mkdir tools/clang
tar -xvvJf %{SOURCE1} -C tools/clang --strip 1
%setup -q -D -n bcc

%build
export LD_LIBRARY_PATH="%{_builddir}/usr/lib64"
export PATH="%{_builddir}/usr/bin":$PATH

# build llvm
pushd %{_builddir}/llvm-%{llvmver}.src
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DLLVM_TARGETS_TO_BUILD="X86;BPF" -DCMAKE_INSTALL_PREFIX=/usr %{?lua_config}
make %{?_smp_mflags}
make install DESTDIR="%{_builddir}"
popd

mkdir build
pushd build
cmake .. -DREVISION_LAST=%{version} -DREVISION=%{version} -DCMAKE_INSTALL_PREFIX=/usr
make %{?_smp_mflags}
popd

%install
pushd build
make install/strip DESTDIR=%{buildroot}


%package -n libbcc
Summary: Shared Library for BPF Compiler Collection (BCC)
Requires: elfutils-libelf
%if %{with_lua}
Requires: bcc-lua = %{version}-%{release}
%endif
%description -n libbcc
Shared Library for BPF Compiler Collection (BCC)

%package -n libbcc-examples
Summary: Examples for BPF Compiler Collection (BCC)
Requires: libbcc
%description -n libbcc-examples
Examples for BPF Compiler Collection (BCC)

%package -n python-bcc
Summary: Python bindings for BPF Compiler Collection (BCC)
Requires: libbcc
%description -n python-bcc
Python bindings for BPF Compiler Collection (BCC)

%if %{with_lua}
%package -n bcc-lua
Summary: Standalone tool to run BCC tracers written in Lua
Requires: libbcc = %{version}-%{release}
%description -n bcc-lua
Standalone tool to run BCC tracers written in Lua
%endif

%package -n bcc-tools
Summary: Command line tools for BPF Compiler Collection (BCC)
Requires: python-bcc
%description -n bcc-tools
Command line tools for BPF Compiler Collection (BCC)

%files -n python-bcc
%{python_sitelib}/bcc*

%files -n libbcc
/usr/lib64/*
/usr/include/bcc/*

%files -n libbcc-examples
/usr/share/bcc/examples/*
%exclude /usr/share/bcc/examples/*.pyc
%exclude /usr/share/bcc/examples/*.pyo
%exclude /usr/share/bcc/examples/*/*.pyc
%exclude /usr/share/bcc/examples/*/*.pyo
%exclude /usr/share/bcc/examples/*/*/*.pyc
%exclude /usr/share/bcc/examples/*/*/*.pyo

%if %{with_lua}
%files -n bcc-lua
/usr/bin/bcc-lua
%endif

%files -n bcc-tools
/usr/share/bcc/tools/*
/usr/share/bcc/man/*

%changelog
* Wed Aug 16 2017 TD Mackey <tdmackey@booleanhaiku.com> - 0.3.0-1
- Add bcc-lua package
- Revise spec to addres rpmlint issues

* Fri Jul 03 2015 Brenden Blanco <bblanco@plumgrid.com> - 0.1.1-2
- Initial RPM Release
