#include "kernels.h"

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
