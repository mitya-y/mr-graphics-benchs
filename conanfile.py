from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.build import check_min_cppstd

class MrGraphicsBenchRecipe(ConanFile):
    name = "mr-graphics-benchs"
    version = "1.0.0"
    package_type = "application"

    license = "MIT"
    author = "Kozenko dkitriy 8863314@gmail.com"
    url = "https://github.com/mitya-y/mr-graphics-benchs"
    description = "Benchmarkd for mr-graphics lib"
    topics = ("3D", "Computer Graphics", "Benchmarks")

    settings = "os", "compiler", "build_type", "arch"

    # options = {"shared": [True, False]}
    # default_options = {"shared": False}
    # exports_sources = "CMakeLists.txt", "src/*", "cmake/*", "include/*", "examples/*"

    def requirements(self):
        self.requires("mr-math/1.1.5")
        self.requires("mr-graphics/1.0.0")
        self.requires("mr-utils/1.1.2")
        self.requires("mr-importer/2.9.3")

        self.requires("tracy/0.12.2")

    def build_requirements(self):
        self.tool_requires("cmake/[>3.26]")
        self.tool_requires("ninja/[~1.12]")

        if self.settings.os == "Linux":
            self.tool_requires("mold/[>=2.40]")

    def validate(self):
        check_min_cppstd(self, "23")

    def configure(self):
        if self.settings.os == "Linux":
            self.conf_info.append("tools.build:exelinkflags", "-fuse-ld=mold")
            self.conf_info.append("tools.build:sharedlinkflags", "-fuse-ld=mold")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generator = "Ninja"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generator = "Ninja"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
