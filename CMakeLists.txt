cmake_minimum_required(VERSION 3.20)
project(hpc_sph CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)
find_package(OpenMP)
add_library(hpc_sph MODULE
    src/cpp/kernels.cpp
    src/cpp/sph_scalar.cpp
    src/cpp/sph_neon.cpp
    src/cpp/bindings.cpp
    src/cpp/sph_neon_omp.cpp
)
target_link_libraries(hpc_sph PRIVATE pybind11::module)
pybind11_extension(hpc_sph)
pybind11_strip(hpc_sph)
target_link_libraries(hpc_sph PRIVATE pybind11::module)
if(OpenMP_CXX_FOUND)
    target_link_libraries(hpc_sph PRIVATE OpenMP::OpenMP_CXX)
    target_include_directories(hpc_sph PRIVATE /opt/homebrew/opt/libomp/include)
endif()

