dnl require autoconf 2.60 (AS_ECHO/AS_ECHO_N)
AC_PREREQ([2.60])
define(_CLIENT_VERSION_MAJOR, 0)
define(_CLIENT_VERSION_MINOR, 12)
define(_CLIENT_VERSION_REVISION, 99)
define(_CLIENT_VERSION_BUILD, 0)
define(_CLIENT_VERSION_IS_RELEASE, false)
define(_COPYRIGHT_YEAR, 2015)
AC_INIT([Bitcoin Core],[_CLIENT_VERSION_MAJOR._CLIENT_VERSION_MINOR._CLIENT_VERSION_REVISION],[https://github.com/bitcoin/bitcoin/issues],[bitcoin])
AC_CONFIG_SRCDIR([src/main.cpp])
AC_CONFIG_HEADERS([src/config/bitcoin-config.h])
AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([build-aux/m4])

AC_CANONICAL_HOST

AH_TOP([#ifndef BITCOIN_CONFIG_H])
AH_TOP([#define BITCOIN_CONFIG_H])
AH_BOTTOM([#endif //BITCOIN_CONFIG_H])

dnl faketime breaks configure and is only needed for make. Disable it here.
unset FAKETIME

dnl Automake init set-up and checks
AM_INIT_AUTOMAKE([no-define subdir-objects foreign])

dnl faketime messes with timestamps and causes configure to be re-run.
dnl --disable-maintainer-mode can be used to bypass this.
AM_MAINTAINER_MODE([enable])

dnl make the compilation flags quiet unless V=1 is used
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

dnl Compiler checks (here before libtool).
if test "x${CXXFLAGS+set}" = "xset"; then
  CXXFLAGS_overridden=yes
else
  CXXFLAGS_overridden=no
fi
AC_PROG_CXX
m4_ifdef([AC_PROG_OBJCXX],[AC_PROG_OBJCXX])

dnl By default, libtool for mingw refuses to link static libs into a dll for
dnl fear of mixing pic/non-pic objects, and import/export complications. Since
dnl we have those under control, re-enable that functionality.
case $host in
  *mingw*)
     lt_cv_deplibs_check_method="pass_all"
  ;;
esac
dnl Libtool init checks.
LT_INIT([pic-only])

dnl Check/return PATH for base programs.
AC_PATH_TOOL(AR, ar)
AC_PATH_TOOL(RANLIB, ranlib)
AC_PATH_TOOL(STRIP, strip)
AC_PATH_TOOL(GCOV, gcov)
AC_PATH_PROG(LCOV, lcov)
AC_PATH_PROG(JAVA, java)
AC_PATH_PROG(PYTHON, python)
AC_PATH_PROG(GENHTML, genhtml)
AC_PATH_PROG([GIT], [git])
AC_PATH_PROG(CCACHE,ccache)
AC_PATH_PROG(XGETTEXT,xgettext)
AC_PATH_PROG(HEXDUMP,hexdump)

dnl pkg-config check.
PKG_PROG_PKG_CONFIG

AC_ARG_ENABLE(tests,
    AS_HELP_STRING([--disable-tests],[do not compile tests (default is to compile)]),
    [use_tests=$enableval],
    [use_tests=yes])

AC_ARG_ENABLE(bench,
    AS_HELP_STRING([--disable-bench],[do not compile benchmarks (default is to compile)]),
    [use_bench=$enableval],
    [use_bench=yes])

AC_ARG_WITH([comparison-tool],
    AS_HELP_STRING([--with-comparison-tool],[path to java comparison tool (requires --enable-tests)]),
    [use_comparison_tool=$withval],
    [use_comparison_tool=no])

AC_ARG_ENABLE([comparison-tool-reorg-tests],
    AS_HELP_STRING([--enable-comparison-tool-reorg-tests],[enable expensive reorg tests in the comparison tool (default no)]),
    [use_comparison_tool_reorg_tests=$enableval],
    [use_comparison_tool_reorg_tests=no])

AC_ARG_ENABLE([extended-rpc-tests],
    AS_HELP_STRING([--enable-extended-rpc-tests],[enable expensive RPC tests when using lcov (default no)]),
    [use_extended_rpc_tests=$enableval],
    [use_extended_rpc_tests=no])

AC_ARG_ENABLE([hardening],
  [AS_HELP_STRING([--disable-hardening],
  [do not attempt to harden the resulting executables (default is to harden)])],
  [use_hardening=$enableval],
  [use_hardening=yes])

AC_ARG_ENABLE([reduce-exports],
  [AS_HELP_STRING([--enable-reduce-exports],
  [attempt to reduce exported symbols in the resulting executables (default is no)])],
  [use_reduce_exports=$enableval],
  [use_reduce_exports=no])

AC_ARG_ENABLE([ccache],
  [AS_HELP_STRING([--disable-ccache],
  [do not use ccache for building (default is to use if found)])],
  [use_ccache=$enableval],
  [use_ccache=auto])

AC_ARG_ENABLE([lcov],
  [AS_HELP_STRING([--enable-lcov],
  [enable lcov testing (default is no)])],
  [use_lcov=yes],
  [use_lcov=no])

AC_ARG_ENABLE([glibc-back-compat],
  [AS_HELP_STRING([--enable-glibc-back-compat],
  [enable backwards compatibility with glibc])],
  [use_glibc_compat=$enableval],
  [use_glibc_compat=no])

AC_ARG_WITH([protoc-bindir],[AS_HELP_STRING([--with-protoc-bindir=BIN_DIR],[specify protoc bin path])], [protoc_bin_path=$withval], [])

# Enable debug
AC_ARG_ENABLE([debug],
    [AS_HELP_STRING([--enable-debug],
                    [use debug compiler flags and macros (default is no)])],
    [enable_debug=$enableval],
    [enable_debug=no])

if test "x$enable_debug" = xyes; then
    CPPFLAGS="$CPPFLAGS -DDEBUG -DDEBUG_LOCKORDER"
    if test "x$GCC" = xyes; then
        CFLAGS="$CFLAGS -g3 -O0"
    fi

    if test "x$GXX" = xyes; then
        CXXFLAGS="$CXXFLAGS -g3 -O0"
    fi
fi

## TODO: Remove these hard-coded paths and flags. They are here for the sake of
##       compatibility with the legacy buildsystem.
##
if test "x$CXXFLAGS_overridden" = "xno"; then
  CXXFLAGS="$CXXFLAGS -Wall -Wextra -Wformat -Wformat-security -Wno-unused-parameter -Wno-self-assign"
fi
CPPFLAGS="$CPPFLAGS -DHAVE_BUILD_INFO -D__STDC_FORMAT_MACROS"

AC_ARG_WITH([utils],
  [AS_HELP_STRING([--with-utils],
  [build bitcoin-cli bitcoin-tx (default=yes)])],
  [build_bitcoin_utils=$withval],
  [build_bitcoin_utils=yes])

AC_ARG_WITH([libs],
  [AS_HELP_STRING([--with-libs],
  [build libraries (default=yes)])],
  [build_bitcoin_libs=$withval],
  [build_bitcoin_libs=yes])

AC_ARG_WITH([daemon],
  [AS_HELP_STRING([--with-daemon],
  [build bitcoind daemon (default=yes)])],
  [build_bitcoind=$withval],
  [build_bitcoind=yes])

AC_LANG_PUSH([C++])

use_pkgconfig=yes
case $host in
  *darwin*)
     TARGET_OS=darwin
     LEVELDB_TARGET_FLAGS="TARGET_OS=Darwin"
     if  test x$cross_compiling != xyes; then
       BUILD_OS=darwin
       AC_CHECK_PROG([PORT],port, port)
       if test x$PORT = xport; then
         dnl add default macports paths
         CPPFLAGS="$CPPFLAGS -isystem /opt/local/include"
         LIBS="$LIBS -L/opt/local/lib"
         if test -d /opt/local/include/db48; then
           CPPFLAGS="$CPPFLAGS -I/opt/local/include/db48"
           LIBS="$LIBS -L/opt/local/lib/db48"
         fi
       fi

       AC_CHECK_PROG([BREW],brew, brew)
       if test x$BREW = xbrew; then
         dnl These Homebrew packages may be keg-only, meaning that they won't be found
         dnl in expected paths because they may conflict with system files. Ask
         dnl Homebrew where each one is located, then adjust paths accordingly.
         dnl It's safe to add these paths even if the functionality is disabled by
         dnl the user (--without-wallet or --without-gui for example).

         openssl_prefix=`$BREW --prefix openssl 2>/dev/null`
         if test x$openssl_prefix != x; then
           PKG_CONFIG_PATH="$openssl_prefix/lib/pkgconfig:$PKG_CONFIG_PATH"
           export PKG_CONFIG_PATH
         fi
       fi
     else
       case $build_os in
         *darwin*)
           BUILD_OS=darwin
           ;;
         *)
           AC_PATH_TOOL([INSTALLNAMETOOL], [install_name_tool], install_name_tool)
           AC_PATH_TOOL([OTOOL], [otool], otool)
           AC_PATH_PROGS([GENISOIMAGE], [genisoimage mkisofs],genisoimage)

           dnl libtool will try to strip the static lib, which is a problem for
           dnl cross-builds because strip attempts to call a hard-coded ld,
           dnl which may not exist in the path. Stripping the .a is not
           dnl necessary, so just disable it.
           old_striplib=
           ;;
       esac
     fi

     AX_CHECK_LINK_FLAG([[-Wl,-headerpad_max_install_names]], [LDFLAGS="$LDFLAGS -Wl,-headerpad_max_install_names"])
     CPPFLAGS="$CPPFLAGS -DMAC_OSX"
     OBJCXXFLAGS="$CXXFLAGS"
     ;;
   *linux*)
     TARGET_OS=linux
     ;;
   *)
     ;;
esac

if test x$use_comparison_tool != xno; then
  AC_SUBST(JAVA_COMPARISON_TOOL, $use_comparison_tool)
fi

if test x$use_comparison_tool_reorg_tests != xno; then
  if test x$use_comparison_tool = x; then
    AC_MSG_ERROR("comparison tool reorg tests but comparison tool was not specified")
  fi
  AC_SUBST(COMPARISON_TOOL_REORG_TESTS, 1)
else
  AC_SUBST(COMPARISON_TOOL_REORG_TESTS, 0)
fi

if test x$use_extended_rpc_tests != xno; then
  AC_SUBST(EXTENDED_RPC_TESTS, -extended)
fi

if test x$use_lcov = xyes; then
  if test x$LCOV = x; then
    AC_MSG_ERROR("lcov testing requested but lcov not found")
  fi
  if test x$GCOV = x; then
    AC_MSG_ERROR("lcov testing requested but gcov not found")
  fi
  if test x$JAVA = x; then
    AC_MSG_ERROR("lcov testing requested but java not found")
  fi
  if test x$PYTHON = x; then
    AC_MSG_ERROR("lcov testing requested but python not found")
  fi
  if test x$GENHTML = x; then
    AC_MSG_ERROR("lcov testing requested but genhtml not found")
  fi
  if test x$use_comparison_tool = x; then
    AC_MSG_ERROR("lcov testing requested but comparison tool was not specified")
  fi
  LCOV="$LCOV --gcov-tool=$GCOV"
  AX_CHECK_COMPILE_FLAG([--coverage],[CXXFLAGS="$CXXFLAGS --coverage"],
    [AC_MSG_ERROR("lcov testing requested but --coverage flag does not work")])
fi

dnl Check for endianness
AC_C_BIGENDIAN

dnl Check for pthread compile/link requirements
AX_PTHREAD

# The following macro will add the necessary defines to bitcoin-config.h, but
# they also need to be passed down to any subprojects. Pull the results out of
# the cache and add them to CPPFLAGS.
AC_SYS_LARGEFILE
# detect POSIX or GNU variant of strerror_r
AC_FUNC_STRERROR_R

if test x$ac_cv_sys_file_offset_bits != x &&
   test x$ac_cv_sys_file_offset_bits != xno &&
   test x$ac_cv_sys_file_offset_bits != xunknown; then
  CPPFLAGS="$CPPFLAGS -D_FILE_OFFSET_BITS=$ac_cv_sys_file_offset_bits"
fi

if test x$ac_cv_sys_large_files != x &&
   test x$ac_cv_sys_large_files != xno &&
   test x$ac_cv_sys_large_files != xunknown; then
  CPPFLAGS="$CPPFLAGS -D_LARGE_FILES=$ac_cv_sys_large_files"
fi

AX_CHECK_LINK_FLAG([[-Wl,--large-address-aware]], [LDFLAGS="$LDFLAGS -Wl,--large-address-aware"])

AX_GCC_FUNC_ATTRIBUTE([visibility])
AX_GCC_FUNC_ATTRIBUTE([dllexport])
AX_GCC_FUNC_ATTRIBUTE([dllimport])

if test x$use_glibc_compat != xno; then

  #__fdelt_chk's params and return type have changed from long unsigned int to long int.
  # See which one is present here.
  AC_MSG_CHECKING(__fdelt_chk type)
  AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#ifdef _FORTIFY_SOURCE
                    #undef _FORTIFY_SOURCE
                  #endif
                  #define _FORTIFY_SOURCE 2
                  #include <sys/select.h>
     extern "C" long unsigned int __fdelt_warn(long unsigned int);]],[[]])],
    [ fdelt_type="long unsigned int"],
    [ fdelt_type="long int"])
  AC_MSG_RESULT($fdelt_type)
  AC_DEFINE_UNQUOTED(FDELT_TYPE, $fdelt_type,[parameter and return value type for __fdelt_chk])

fi

if test x$TARGET_OS != xwindows; then
  # All windows code is PIC, forcing it on just adds useless compile warnings
  AX_CHECK_COMPILE_FLAG([-fPIC],[PIC_FLAGS="-fPIC"])
fi

if test x$use_hardening != xno; then
  AX_CHECK_COMPILE_FLAG([-Wstack-protector],[HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -Wstack-protector"])
  AX_CHECK_COMPILE_FLAG([-fstack-protector-all],[HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -fstack-protector-all"])

  AX_CHECK_PREPROC_FLAG([-D_FORTIFY_SOURCE=2],[
    AX_CHECK_PREPROC_FLAG([-U_FORTIFY_SOURCE],[
      HARDENED_CPPFLAGS="$HARDENED_CPPFLAGS -U_FORTIFY_SOURCE"
    ])
    HARDENED_CPPFLAGS="$HARDENED_CPPFLAGS -D_FORTIFY_SOURCE=2"
  ])

  AX_CHECK_LINK_FLAG([[-Wl,--dynamicbase]], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--dynamicbase"])
  AX_CHECK_LINK_FLAG([[-Wl,--nxcompat]], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--nxcompat"])
  AX_CHECK_LINK_FLAG([[-Wl,-z,relro]], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,-z,relro"])
  AX_CHECK_LINK_FLAG([[-Wl,-z,now]], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,-z,now"])

  if test x$TARGET_OS != xwindows; then
    AX_CHECK_COMPILE_FLAG([-fPIE],[PIE_FLAGS="-fPIE"])
    AX_CHECK_LINK_FLAG([[-pie]], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -pie"])
  fi

  case $host in
    *mingw*)
       AC_CHECK_LIB([ssp],      [main],, AC_MSG_ERROR(lib missing))
    ;;
  esac
fi

dnl this flag screws up non-darwin gcc even when the check fails. special-case it.
if test x$TARGET_OS = xdarwin; then
  AX_CHECK_LINK_FLAG([[-Wl,-dead_strip]], [LDFLAGS="$LDFLAGS -Wl,-dead_strip"])
fi

AC_CHECK_HEADERS([endian.h sys/endian.h byteswap.h stdio.h stdlib.h unistd.h strings.h sys/types.h sys/stat.h sys/select.h sys/prctl.h])
AC_SEARCH_LIBS([getaddrinfo_a], [anl], [AC_DEFINE(HAVE_GETADDRINFO_A, 1, [Define this symbol if you have getaddrinfo_a])])
AC_SEARCH_LIBS([inet_pton], [nsl resolv], [AC_DEFINE(HAVE_INET_PTON, 1, [Define this symbol if you have inet_pton])])

AC_CHECK_DECLS([strnlen])

AC_CHECK_DECLS([le16toh, le32toh, le64toh, htole16, htole32, htole64, be16toh, be32toh, be64toh, htobe16, htobe32, htobe64],,,
		[#if HAVE_ENDIAN_H
                 #include <endian.h>
                 #elif HAVE_SYS_ENDIAN_H
                 #include <sys/endian.h>
                 #endif])

AC_CHECK_DECLS([bswap_16, bswap_32, bswap_64],,,
		[#if HAVE_BYTESWAP_H
                 #include <byteswap.h>
                 #endif])

dnl Check for MSG_NOSIGNAL
AC_MSG_CHECKING(for MSG_NOSIGNAL)
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <sys/socket.h>]],
 [[ int f = MSG_NOSIGNAL; ]])],
 [ AC_MSG_RESULT(yes); AC_DEFINE(HAVE_MSG_NOSIGNAL, 1,[Define this symbol if you have MSG_NOSIGNAL]) ],
 [ AC_MSG_RESULT(no)]
)

AC_SEARCH_LIBS([clock_gettime],[rt])

AC_MSG_CHECKING([for visibility attribute])
AC_LINK_IFELSE([AC_LANG_SOURCE([
  int foo_def( void ) __attribute__((visibility("default")));
  int main(){}
  ])],
  [
    AC_DEFINE(HAVE_VISIBILITY_ATTRIBUTE,1,[Define if the visibility attribute is supported.])
    AC_MSG_RESULT(yes)
  ],
  [
    AC_MSG_RESULT(no)
    if test x$use_reduce_exports = xyes; then
      AC_MSG_ERROR([Cannot find a working visibility attribute. Use --disable-reduce-exports.])
    fi
  ]
)

if test x$use_reduce_exports = xyes; then
  AX_CHECK_COMPILE_FLAG([-fvisibility=hidden],[RE_CXXFLAGS="-fvisibility=hidden"],
  [AC_MSG_ERROR([Cannot set default symbol visibility. Use --disable-reduce-exports.])])
fi

LEVELDB_CPPFLAGS=
LIBLEVELDB=
LIBMEMENV=
AM_CONDITIONAL([EMBEDDED_LEVELDB],[true])
AC_SUBST(LEVELDB_CPPFLAGS)
AC_SUBST(LIBLEVELDB)
AC_SUBST(LIBMEMENV)

if test x$build_bitcoin_utils$build_bitcoind$bitcoin_enable_qt$use_tests = xnononono; then
    use_boost=no
else
    use_boost=yes
fi

if test x$use_boost = xyes; then

dnl Check for boost libs
AX_BOOST_BASE
AX_BOOST_SYSTEM
AX_BOOST_FILESYSTEM
AX_BOOST_PROGRAM_OPTIONS
AX_BOOST_THREAD
AX_BOOST_CHRONO


if test x$use_reduce_exports = xyes; then
  AC_MSG_CHECKING([for working boost reduced exports])
  TEMP_CPPFLAGS="$CPPFLAGS"
  CPPFLAGS="$BOOST_CPPFLAGS $CPPFLAGS"
  AC_PREPROC_IFELSE([AC_LANG_PROGRAM([[
      @%:@include <boost/version.hpp>
    ]], [[
      #if BOOST_VERSION >= 104900
      // Everything is okay
      #else
      #  error Boost version is too old
      #endif
    ]])],[
      AC_MSG_RESULT(yes)
    ],[
    AC_MSG_ERROR([boost versions < 1.49 are known to be broken with reduced exports. Use --disable-reduce-exports.])
  ])
  CPPFLAGS="$TEMP_CPPFLAGS"
fi
fi

if test x$use_reduce_exports = xyes; then
    CXXFLAGS="$CXXFLAGS $RE_CXXFLAGS"
    AX_CHECK_LINK_FLAG([[-Wl,--exclude-libs,ALL]], [RELDFLAGS="-Wl,--exclude-libs,ALL"])
fi

if test x$use_tests = xyes; then

  if test x$HEXDUMP = x; then
    AC_MSG_ERROR(hexdump is required for tests)
  fi


  if test x$use_boost = xyes; then

  AX_BOOST_UNIT_TEST_FRAMEWORK

  dnl Determine if -DBOOST_TEST_DYN_LINK is needed
  AC_MSG_CHECKING([for dynamic linked boost test])
  TEMP_LIBS="$LIBS"
  LIBS="$LIBS $BOOST_LDFLAGS $BOOST_UNIT_TEST_FRAMEWORK_LIB"
  TEMP_CPPFLAGS="$CPPFLAGS"
  CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
  AC_LINK_IFELSE([AC_LANG_SOURCE([
       #define BOOST_TEST_DYN_LINK
       #define BOOST_TEST_MAIN
        #include <boost/test/unit_test.hpp>

       ])],
    [AC_MSG_RESULT(yes)]
    [TESTDEFS="$TESTDEFS -DBOOST_TEST_DYN_LINK"],
    [AC_MSG_RESULT(no)])
  LIBS="$TEMP_LIBS"
  CPPFLAGS="$TEMP_CPPFLAGS"

  fi
fi

if test x$use_boost = xyes; then

BOOST_LIBS="$BOOST_LDFLAGS $BOOST_SYSTEM_LIB $BOOST_FILESYSTEM_LIB $BOOST_PROGRAM_OPTIONS_LIB $BOOST_THREAD_LIB $BOOST_CHRONO_LIB"

dnl Boost >= 1.50 uses sleep_for rather than the now-deprecated sleep, however
dnl it was broken from 1.50 to 1.52 when backed by nanosleep. Use sleep_for if
dnl a working version is available, else fall back to sleep. sleep was removed
dnl after 1.56.
dnl If neither is available, abort.
TEMP_LIBS="$LIBS"
LIBS="$BOOST_LIBS $LIBS"
TEMP_CPPFLAGS="$CPPFLAGS"
CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
AC_LINK_IFELSE([AC_LANG_PROGRAM([[
  #include <boost/thread/thread.hpp>
  #include <boost/version.hpp>
  ]],[[
  #if BOOST_VERSION >= 105000 && (!defined(BOOST_HAS_NANOSLEEP) || BOOST_VERSION >= 105200)
      boost::this_thread::sleep_for(boost::chrono::milliseconds(0));
  #else
   choke me
  #endif
  ]])],
  [boost_sleep=yes;
     AC_DEFINE(HAVE_WORKING_BOOST_SLEEP_FOR, 1, [Define this symbol if boost sleep_for works])],
  [boost_sleep=no])
LIBS="$TEMP_LIBS"
CPPFLAGS="$TEMP_CPPFLAGS"

if test x$boost_sleep != xyes; then
TEMP_LIBS="$LIBS"
LIBS="$BOOST_LIBS $LIBS"
TEMP_CPPFLAGS="$CPPFLAGS"
CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
AC_LINK_IFELSE([AC_LANG_PROGRAM([[
  #include <boost/version.hpp>
  #include <boost/thread.hpp>
  #include <boost/date_time/posix_time/posix_time_types.hpp>
  ]],[[
  #if BOOST_VERSION <= 105600
      boost::this_thread::sleep(boost::posix_time::milliseconds(0));
  #else
   choke me
  #endif
  ]])],
  [boost_sleep=yes; AC_DEFINE(HAVE_WORKING_BOOST_SLEEP, 1, [Define this symbol if boost sleep works])],
  [boost_sleep=no])
LIBS="$TEMP_LIBS"
CPPFLAGS="$TEMP_CPPFLAGS"
fi

if test x$boost_sleep != xyes; then
  AC_MSG_ERROR(No working boost sleep implementation found.)
fi

fi

if test x$use_pkgconfig = xyes; then

  if test x"$PKG_CONFIG" = "x"; then
    AC_MSG_ERROR(pkg-config not found.)
  fi

  : #NOP
  m4_ifdef(
    [PKG_CHECK_MODULES],
    [
      PKG_CHECK_MODULES([SSL], [libssl],, [AC_MSG_ERROR(openssl  not found.)])
      PKG_CHECK_MODULES([CRYPTO], [libcrypto],,[AC_MSG_ERROR(libcrypto  not found.)])
      if test x$build_bitcoin_utils$build_bitcoind$bitcoin_enable_qt$use_tests != xnononono; then
        PKG_CHECK_MODULES([EVENT], [libevent],, [AC_MSG_ERROR(libevent not found.)])
        if test x$TARGET_OS != xwindows; then
          PKG_CHECK_MODULES([EVENT_PTHREADS], [libevent_pthreads],, [AC_MSG_ERROR(libevent_pthreads not found.)])
        fi
      fi
    ]
  )
else
  AC_CHECK_HEADER([openssl/crypto.h],,AC_MSG_ERROR(libcrypto headers missing))
  AC_CHECK_LIB([crypto],      [main],CRYPTO_LIBS=-lcrypto, AC_MSG_ERROR(libcrypto missing))

  AC_CHECK_HEADER([openssl/ssl.h],, AC_MSG_ERROR(libssl headers missing),)
  AC_CHECK_LIB([ssl],         [main],SSL_LIBS=-lssl, AC_MSG_ERROR(libssl missing))

  if test x$build_bitcoin_utils$build_bitcoind$bitcoin_enable_qt$use_tests != xnononono; then
    AC_CHECK_HEADER([event2/event.h],, AC_MSG_ERROR(libevent headers missing),)
    AC_CHECK_LIB([event],[main],EVENT_LIBS=-levent,AC_MSG_ERROR(libevent missing))
    if test x$TARGET_OS != xwindows; then
      AC_CHECK_LIB([event_pthreads],[main],EVENT_PTHREADS_LIBS=-levent_pthreads,AC_MSG_ERROR(libevent_pthreads missing))
    fi
  fi

fi

CXXFLAGS_TEMP="$CXXFLAGS"
LIBS_TEMP="$LIBS"
CXXFLAGS="$CXXFLAGS $SSL_CFLAGS $CRYPTO_CFLAGS"
LIBS="$LIBS $SSL_LIBS $CRYPTO_LIBS"
AC_CHECK_HEADER([openssl/ec.h],, AC_MSG_ERROR(OpenSSL ec header missing),)
CXXFLAGS="$CXXFLAGS_TEMP"
LIBS="$LIBS_TEMP"

AC_MSG_CHECKING([whether to build bitcoind])
AM_CONDITIONAL([BUILD_BITCOIND], [test x$build_bitcoind = xyes])
AC_MSG_RESULT($build_bitcoind)

AC_MSG_CHECKING([whether to build utils (bitcoin-cli bitcoin-tx)])
AM_CONDITIONAL([BUILD_BITCOIN_UTILS], [test x$build_bitcoin_utils = xyes])
AC_MSG_RESULT($build_bitcoin_utils)

AC_MSG_CHECKING([whether to build libraries])
AM_CONDITIONAL([BUILD_BITCOIN_LIBS], [test x$build_bitcoin_libs = xyes])
if test x$build_bitcoin_libs = xyes; then
  AC_DEFINE(HAVE_CONSENSUS_LIB, 1, [Define this symbol if the consensus lib has been built])
  AC_CONFIG_FILES([libbitcoinconsensus.pc:libbitcoinconsensus.pc.in])
fi
AC_MSG_RESULT($build_bitcoin_libs)

AC_LANG_POP

if test "x$use_ccache" != "xno"; then
  AC_MSG_CHECKING(if ccache should be used)
  if test x$CCACHE = x; then
    if test "x$use_ccache" = "xyes"; then
      AC_MSG_ERROR([ccache not found.]);
    else
      use_ccache=no
    fi
  else
    use_ccache=yes
    CC="$ac_cv_path_CCACHE $CC"
    CXX="$ac_cv_path_CCACHE $CXX"
  fi
  AC_MSG_RESULT($use_ccache)
fi
if test "x$use_ccache" = "xyes"; then
    AX_CHECK_PREPROC_FLAG([-Qunused-arguments],[CPPFLAGS="-Qunused-arguments $CPPFLAGS"])
fi

AC_MSG_CHECKING([whether to build test_bitcoin])
if test x$use_tests = xyes; then
  AC_MSG_RESULT([yes])
  BUILD_TEST="test"
else
  AC_MSG_RESULT([no])
fi

AC_MSG_CHECKING([whether to reduce exports])
if test x$use_reduce_exports = xyes; then
  AC_MSG_RESULT([yes])
else
  AC_MSG_RESULT([no])
fi

if test x$build_bitcoin_utils$build_bitcoin_libs$build_bitcoind$use_tests = xnonononono; then
  AC_MSG_ERROR([No targets! Please specify at least one of: --with-utils --with-libs --with-daemon or --enable-tests])
fi

AM_CONDITIONAL([TARGET_DARWIN], [test x$TARGET_OS = xdarwin])
AM_CONDITIONAL([BUILD_DARWIN], [test x$BUILD_OS = xdarwin])
AM_CONDITIONAL([ENABLE_TESTS],[test x$use_tests = xyes])
AM_CONDITIONAL([ENABLE_BENCH],[test x$use_bench = xyes])
AM_CONDITIONAL([USE_LCOV],[test x$use_lcov = xyes])
AM_CONDITIONAL([USE_COMPARISON_TOOL],[test x$use_comparison_tool != xno])
AM_CONDITIONAL([USE_COMPARISON_TOOL_REORG_TESTS],[test x$use_comparison_tool_reorg_test != xno])
AM_CONDITIONAL([GLIBC_BACK_COMPAT],[test x$use_glibc_compat = xyes])

AC_DEFINE(CLIENT_VERSION_MAJOR, _CLIENT_VERSION_MAJOR, [Major version])
AC_DEFINE(CLIENT_VERSION_MINOR, _CLIENT_VERSION_MINOR, [Minor version])
AC_DEFINE(CLIENT_VERSION_REVISION, _CLIENT_VERSION_REVISION, [Build revision])
AC_DEFINE(CLIENT_VERSION_BUILD, _CLIENT_VERSION_BUILD, [Version Build])
AC_DEFINE(CLIENT_VERSION_IS_RELEASE, _CLIENT_VERSION_IS_RELEASE, [Version is release])
AC_DEFINE(COPYRIGHT_YEAR, _COPYRIGHT_YEAR, [Version is release])
AC_SUBST(CLIENT_VERSION_MAJOR, _CLIENT_VERSION_MAJOR)
AC_SUBST(CLIENT_VERSION_MINOR, _CLIENT_VERSION_MINOR)
AC_SUBST(CLIENT_VERSION_REVISION, _CLIENT_VERSION_REVISION)
AC_SUBST(CLIENT_VERSION_BUILD, _CLIENT_VERSION_BUILD)
AC_SUBST(CLIENT_VERSION_IS_RELEASE, _CLIENT_VERSION_IS_RELEASE)
AC_SUBST(COPYRIGHT_YEAR, _COPYRIGHT_YEAR)

AC_SUBST(RELDFLAGS)
AC_SUBST(HARDENED_CXXFLAGS)
AC_SUBST(HARDENED_CPPFLAGS)
AC_SUBST(HARDENED_LDFLAGS)
AC_SUBST(PIC_FLAGS)
AC_SUBST(PIE_FLAGS)
AC_SUBST(LIBTOOL_APP_LDFLAGS)
AC_SUBST(BOOST_LIBS)
AC_SUBST(TESTDEFS)
AC_SUBST(LEVELDB_TARGET_FLAGS)
AC_SUBST(BUILD_TEST)
AC_CONFIG_FILES([Makefile src/Makefile src/test/buildenv.py])
AC_CONFIG_FILES([qa/pull-tester/run-bitcoind-for-test.sh],[chmod +x qa/pull-tester/run-bitcoind-for-test.sh])
AC_CONFIG_FILES([qa/pull-tester/tests_config.py],[chmod +x qa/pull-tester/tests_config.py])

dnl boost's m4 checks do something really nasty: they export these vars. As a
dnl result, they leak into secp256k1's configure and crazy things happen.
dnl Until this is fixed upstream and we've synced, we'll just un-export them.
CPPFLAGS_TEMP="$CPPFLAGS"
unset CPPFLAGS
CPPFLAGS="$CPPFLAGS_TEMP"

LDFLAGS_TEMP="$LDFLAGS"
unset LDFLAGS
LDFLAGS="$LDFLAGS_TEMP"

LIBS_TEMP="$LIBS"
unset LIBS
LIBS="$LIBS_TEMP"

PKGCONFIG_PATH_TEMP="$PKG_CONFIG_PATH"
unset PKG_CONFIG_PATH
PKG_CONFIG_PATH="$PKGCONFIG_PATH_TEMP"

PKGCONFIG_LIBDIR_TEMP="$PKG_CONFIG_LIBDIR"
unset PKG_CONFIG_LIBDIR
PKG_CONFIG_LIBDIR="$PKGCONFIG_LIBDIR_TEMP"

ac_configure_args="${ac_configure_args} --disable-shared --with-pic --with-bignum=no --enable-module-recovery"
AC_CONFIG_SUBDIRS([src/secp256k1 src/univalue])

AC_OUTPUT

dnl Taken from https://wiki.debian.org/RpathIssue
case $host in
   *-*-linux-gnu)
     AC_MSG_RESULT([Fixing libtool for -rpath problems.])
     sed < libtool > libtool-2 \
     's/^hardcode_libdir_flag_spec.*$'/'hardcode_libdir_flag_spec=" -D__LIBTOOL_IS_A_FOOL__ "/'
     mv libtool-2 libtool
     chmod 755 libtool
   ;;
esac
