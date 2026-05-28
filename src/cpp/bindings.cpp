#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

void step(float*, float*, float*, float*, int, float, float, float, float, float, float);

namespace py = pybind11;

PYBIND11_MODULE(hpc_sph, m) {
    m.doc() = "HPC SPH module — bindings placeholder";
    m.def("step", 
        [](py::array_t<float> pos_x, py::array_t<float>pos_y, py::array_t<float> vel_x, py::array_t<float> vel_y,
            int N, float mass, float h, float dt, float mu, float k, float rho0) {
    
        float* p_x = pos_x.mutable_data();
        float* p_y = pos_y.mutable_data();
        float* vx = vel_x.mutable_data();
        float* vy = vel_y.mutable_data();
    
        step(p_x, p_y, vx, vy, N, mass, h, dt, mu, k, rho0);
    });
}

