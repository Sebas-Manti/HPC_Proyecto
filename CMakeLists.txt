cmake_minimum_required(VERSION 3.20)
project(hpc_sph CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)
add_library(hpc_sph MODULE
    src/cpp/bindings.cpp
)
target_link_libraries(hpc_sph PRIVATE pybind11::module)
pybind11_extension(hpc_sph)
pybind11_strip(hpc_sph)