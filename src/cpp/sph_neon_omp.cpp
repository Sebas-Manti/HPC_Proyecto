#include <omp.h>
#include <arm_neon.h>
#include <cmath>
#include "kernels.h"


void compute_density_neon_omp(const float* pos_x, const float* pos_y, int N, float mass, float h, float* rho) {
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < N; i++) {
        float32x4_t vix = vdupq_n_f32(pos_x[i]);
        float32x4_t viy = vdupq_n_f32(pos_y[i]);
        float32x4_t acc = vdupq_n_f32(0.0f);
        
        int j = 0;
        for (; j + 4 <= N; j += 4) {
            float32x4_t vjx = vld1q_f32(&pos_x[j]);
            float32x4_t vjy = vld1q_f32(&pos_y[j]);

            float32x4_t dx = vsubq_f32(vix, vjx);
            float32x4_t dy = vsubq_f32(viy, vjy);

            float32x4_t r2 = vmulq_f32(dx, dx);
            r2 = vmlaq_f32(r2, dy, dy);
            float32x4_t r = vsqrtq_f32(r2);

            float32x4_t vh = vdupq_n_f32(h);
            float32x4_t h2 = vdupq_n_f32(h*h);
            uint32x4_t mask = vcleq_f32(r, vh);
            float32x4_t h2_r2 = vsubq_f32(h2, r2);
            float32x4_t w_val = vmulq_f32(h2_r2, h2_r2);
            w_val = vmulq_f32(w_val, h2_r2);
            w_val = vmulq_f32(w_val, vdupq_n_f32(4.0f / (3.14159265f * pow(h,8))));
            w_val = vbslq_f32(mask, w_val, vdupq_n_f32(0.0f));
            acc = vaddq_f32(acc, w_val);
        }
        rho[i] = vaddvq_f32(acc) * mass;
        for (; j < N; j++) {
            float dx = pos_x[i] - pos_x[j];
            float dy = pos_y[i] - pos_y[j];
            float r = sqrt(dx*dx + dy*dy);
            rho[i] += mass * W(r, h);
        }
    }
}

void compute_forces(
    const float* pos_x, const float* pos_y,
    const float* vel_x, const float* vel_y,
    const float* rho,
    int N, float mass, float h,
    float mu, float k, float rho0,
    float* force_x, float* force_y
);

void step_neon_omp(
    float* pos_x, float* pos_y,
    float* vel_x, float* vel_y,
    int N, float mass, float h,
    float dt, float mu, float k, float rho0
) {
    float rho[N];
    float force_x[N];
    float force_y[N];

    compute_density_neon_omp(pos_x, pos_y, N, mass,h, rho);
    compute_forces(pos_x, pos_y, vel_x, vel_y, rho, N, mass, h, mu, k, rho0, force_x, force_y);

    for(int i = 0; i < N ;i++){
        vel_x[i] = vel_x[i] + dt * force_x[i]/rho[i];
        vel_y[i] = vel_y[i] + dt * force_y[i]/rho[i];
        pos_x[i] = pos_x[i] + dt * vel_x[i];
        pos_y[i] = pos_y[i] + dt * vel_y[i];
    }

    for(int i=0;i<N;i++){
        if (pos_x[i] < 0.0f){
            pos_x[i] = 0.0f;
            vel_x[i] = -vel_x[i];
        }
        if (pos_x[i] > 1.0f){
            pos_x[i] = 1.0f;
            vel_x[i] = -vel_x[i];
        }

        if (pos_y[i] < 0.0f){
            pos_y[i] = 0.0f;
            vel_y[i] = -vel_y[i];
        }
        if (pos_y[i] > 1.0f){
            pos_y[i] = 1.0f;
            vel_y[i] = -vel_y[i];
        }
    }
}