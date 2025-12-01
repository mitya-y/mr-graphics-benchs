cmake_minimum_required(VERSION 3.27)

project(mr-g-bench)

add_executable(${CMAKE_PROJECT_NAME} "")

target_sources(${CMAKE_PROJECT_NAME} PRIVATE
  main.cpp
  render_options/render_options.cpp
)

set(MR_PROJECT_DIR ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "Project working directory")
set(MR_RES_DIR     bin                       CACHE STRING "Project asset directory")

target_compile_definitions(
  ${CMAKE_PROJECT_NAME} PUBLIC
  MR_PROJECT_DIR="${CMAKE_CURRENT_LIST_DIR}"
  MR_RES_DIR="${MR_RES_FULL_DIR}"
)

file(
  DOWNLOAD
  https://github.com/cpm-cmake/CPM.cmake/releases/download/v0.40.2/CPM.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/cmake/CPM.cmake
  EXPECTED_HASH SHA256=c8cdc32c03816538ce22781ed72964dc864b2a34a310d3b7104812a5ca2d835d
)
include(${CMAKE_CURRENT_BINARY_DIR}/cmake/CPM.cmake)

CPMAddPackage("gh:Cvelth/vkfw#main")
CPMAddPackage("gh:bemanproject/inplace_vector#b81a3c7")
CPMAddPackage("gh:GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator@3.3.0")
CPMAddPackage("gh:charles-lunarg/vk-bootstrap@1.4.321")

find_package(Vulkan)
find_package(mr-math REQUIRED)
find_package(mr-utils REQUIRED)
find_package(mr-importer REQUIRED)
find_package(mr-graphics REQUIRED)
find_package(Tracy REQUIRED)

if (${vkfw_ADDED})
  add_library(libvkfw INTERFACE "")
  target_link_libraries(libvkfw INTERFACE glfw)
  target_include_directories(libvkfw INTERFACE ${vkfw_SOURCE_DIR}/include)
endif()

if (${vk-bootstrap_ADDED})
  add_library(vk-bootstrap-lib INTERFACE "")
  target_link_libraries(vk-bootstrap-lib INTERFACE vk-bootstrap::vk-bootstrap)
  target_include_directories(vk-bootstrap-lib INTERFACE ${vk-bootstrap_SOURCE_DIR}/src)
endif()


target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE mr-math::mr-math)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE mr-graphics::mr-graphics)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE mr-utils::mr-utils)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE mr-importer::mr-importer)

target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE Vulkan::Vulkan)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE libvkfw)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE beman.inplace_vector)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE Tracy::TracyClient)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE GPUOpen::VulkanMemoryAllocator)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE vk-bootstrap-lib)

