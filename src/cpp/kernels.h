#pragma once
#include <cmath>

float W(float r, float h);
void grad_W(float rx, float ry, float h, float& out_x, float& out_y);
float lap_W(float r, float h);