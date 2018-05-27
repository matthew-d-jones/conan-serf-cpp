#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class LibnameConan(ConanFile):
    name = "serf-cpp"
    version = "b87eadf"
    description = "C++ implementation of serf client (http://www.serfdom.io)"
    url = "https://github.com/matthew-d-jones/conan-serf-cpp"
    homepage = "https://github.com/CJLove/serf-cpp"

    # Indicates License type of the packaged library
    license = "Apache v2.0"

    # Packages the license for the conanfile.py
    exports = ["LICENSE"]

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    requires = (
        "msgpack/1.4.2@matthew-d-jones/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        self.run("git clone " + self.homepage + ".git")
        self.run("cd " + self.name + " && git checkout " + self.version + " && cd ..")
        os.rename(self.name, self.source_subfolder)

        # Use our wrapper CMakeLists file so msgpack dependency is found
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeLists_original.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SERF_CPP_BUILD_EXAMPLE"] = False
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
