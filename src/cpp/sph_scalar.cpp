#include <vector>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <algorithm>

float W(float r, float h) {

    if (r >= 0.0f && r <=h) {
        return (4.0f / (3.14159265358979f * pow(h,8))) * pow((pow(h,2) - pow(r,2)),3);
    }
    else {
        return 0.0f;
    }
}

void grad_W(float rx, float ry, float h, float& out_x, float& out_y) {

    float r = sqrt(pow(rx,2) + pow(ry,2));
    float factor = -(945.0f / (32.0f*3.14159265358979f*pow(h,9))) * pow((pow(h,2) - pow(r,2)),2);

    if (r >= 0.0f && r <= h) {
        out_x = factor * rx;
        out_y = factor * ry;
    }

    else {
        out_x = 0.0f; 
        out_y = 0.0f;
    }
}

float lap_W(float r, float h) {

    if (r >= 0.0f && r <=h) {
        return -(945.0f / (32.0f*3.14159265358979f*pow(h,9))) * (pow(h,2) - pow(r,2)) * (3*pow(h,2) - 7*pow(r,2));
    }
    else {
        return 0.0f;
    }
}

void compute_density(
    const float* pos_x,
    const float* pos_y,
    int N,
    float mass,
    float h,
    float* rho
) {
    for (int i = 0; i < N; i++) {
        rho[i] = 0.0f;
        for (int j = 0; j < N; j++) {
            
            float dx = pos_x[i] - pos_x[j];
            float dy = pos_y[i] - pos_y[j];
            float r = sqrt(dx*dx + dy*dy);
            
            rho[i] += mass * W(r,h);
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
) {

    float g = -9.8;
    for(int i =0; i<N; i++){
        force_x[i] = 0;
        force_y[i] = rho[i] * (-9.8);
        for (int j =0; j<N; j++){
            if(i==j){
                continue;
            }
            else{
                float dx = pos_x[i]-pos_x[j];
                float dy = pos_y[i]-pos_y[j];
                float r = sqrt(dx*dx + dy*dy);
                if(r>0.0f && r<2.0f*h){
                    float p_i = k * (rho[i] - rho0);
                    float p_j = k * (rho[j] - rho0);
                    float gx, gy;
                    grad_W(dx, dy, h, gx, gy);
                    float F_press_x = -mass * (p_i + p_j) / (2.0f * rho[j]) * gx;
                    float F_press_y = -mass * (p_i + p_j) / (2.0f * rho[j]) * gy;
                    float F_visc_x = mu * mass * (vel_x[j] - vel_x[i]) / rho[j] * lap_W(r, h);
                    float F_visc_y = mu * mass * (vel_y[j] - vel_y[i]) / rho[j] * lap_W(r, h);
                    force_x[i] = force_x[i] + F_press_x + F_visc_x;
                    force_y[i] = force_y[i] + F_press_y + F_visc_y;
                }
            }
        }
    }
}


void step(
    float* pos_x, float* pos_y,
    float* vel_x, float* vel_y,
    int N, float mass, float h,
    float dt, float mu, float k, float rho0
) {
    float rho[N];
    float force_x[N];
    float force_y[N];

    compute_density(pos_x, pos_y, N, mass,h, rho);
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