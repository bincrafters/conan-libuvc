from conans import ConanFile, CMake, tools


class LibuvcConan(ConanFile):
    name = "libuvc"
    version = "0.0.6"
    license = "MIT"
    author = "Salvatore DiAngelus sdiangelus@gmail.com"
    url = "https://github.com/SalDiAngelus/conan-libuvc"
    description = "A cross-platform library for USB video devices"
    topics = ("conan", "libuvc", "libusb", "usb", "video")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "jpeg_turbo": [True, False]}
    default_options = {"shared": False, "fPIC": True, "jpeg_turbo": False}
    generators = "cmake_find_package"
    requires = "libusb/1.0.22@bincrafters/stable"

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/libuvc/libuvc.git", "v0.0.6")
        
        tools.replace_in_file("CMakeLists.txt", "pkg_check_modules(LIBUSB libusb-1.0)", "find_package(libusb REQUIRED)")
        tools.replace_in_file("CMakeLists.txt", "${LIBUSB_INCLUDE_DIRS}", "${libusb_INCLUDE_DIRS}/libusb-1.0")
        
        _jpg_find = '''find_package(jpeg QUIET)
if(JPEG_FOUND)
  set(JPEG_LINK_FLAGS ${JPEG_LIBRARIES})
else()
  pkg_check_modules(JPEG QUIET libjpeg)
  if(JPEG_FOUND)
      set(JPEG_INCLUDE_DIR ${JPEG_INCLUDE_DIRS})
      set(JPEG_LINK_FLAGS ${JPEG_LDFLAGS})
  else()
    find_path(JPEG_INCLUDE_DIR jpeglib.h)
    if(JPEG_INCLUDE_DIR)
      set(JPEG_FOUND ON)
      set(JPEG_LINK_FLAGS -ljpeg)
    endif()
  endif()
endif()'''
        _jpg_replace = '''find_package({0} REQUIRED)
set(JPEG_FOUND ON)
set(JPEG_INCLUDE_DIR ${{{0}_INCLUDE_DIRS}})
set(JPEG_LINK_FLAGS ${{{0}_LIBS}})'''
        if self.options.jpeg_turbo:
            tools.replace_in_file("CMakeLists.txt", _jpg_find, _jpg_replace.format('libjpeg-turbo'))
        else:
            tools.replace_in_file("CMakeLists.txt", _jpg_find, _jpg_replace.format('libjpeg'))

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.jpeg_turbo:
            self.requires("libjpeg-turbo/2.0.2@bincrafters/stable")
        else:
            self.requires("libjpeg/9c@bincrafters/stable")

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.enable_udev
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)
        if self.options.shared:
            _cmake_defs = {"CMAKE_BUILD_TARGET" : "Shared" }
        else:
            _cmake_defs = {"CMAKE_BUILD_TARGET" : "Static" }
        cmake.configure(defs = _cmake_defs)
        cmake.build()

    def package(self):
        self.copy("*", dst="include", src="include")
        if self.options.shared:
            self.copy("libuvc.so", dst="lib", keep_path=False)
        else:
            self.copy("libuvc.a", dst="lib", keep_path=False)

