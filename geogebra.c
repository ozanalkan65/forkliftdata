#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define SIMULATIONS 10000
#define LENGTH 1.5  // Forklift uzunluğu
#define MAX_DISTANCE 12.5
#define OUTPUT_FILE "segments_for_geogebra.txt"

void get_forklift_positions(float x1, float y1, float angle1, float x2, float y2, float angle2, float *A, float *B, float *C, float *D) {
    A[0] = x1 + LENGTH * cos(angle1);
    A[1] = y1 + LENGTH * sin(angle1);

    B[0] = x1 - LENGTH * cos(angle1);
    B[1] = y1 - LENGTH * sin(angle1);

    C[0] = x2 + LENGTH * cos(angle2);
    C[1] = y2 + LENGTH * sin(angle2);

    D[0] = x2 - LENGTH * cos(angle2);
    D[1] = y2 - LENGTH * sin(angle2);
}

int main() {
    srand(time(NULL));

    FILE *outputFile = fopen(OUTPUT_FILE, "w");
    if (outputFile == NULL) {
        printf("Dosya açılamadı!\n");
        return 1;
    }

    for (int i = 0; i < SIMULATIONS; i++) {
        float angle1 = (rand() / (float)RAND_MAX) * M_PI * 2;
        float angle2 = (rand() / (float)RAND_MAX) * M_PI * 2;
        float dist1 = (rand() / (float)RAND_MAX) * MAX_DISTANCE;
        float dist2 = (rand() / (float)RAND_MAX) * MAX_DISTANCE;

        float A_center[2] = { dist1 * cos(angle1), dist1 * sin(angle1) };
        float B_center[2] = { dist2 * cos(angle2), dist2 * sin(angle2) };

        float A[2], B[2], C[2], D[2];
        get_forklift_positions(A_center[0], A_center[1], angle1, B_center[0], B_center[1], angle2, A, B, C, D);

        fprintf(outputFile, "Segment[(%.2f, %.2f), (%.2f, %.2f)]\n", A[0], A[1], B[0], B[1]);  // Forklift1
        fprintf(outputFile, "Segment[(%.2f, %.2f), (%.2f, %.2f)]\n", C[0], C[1], D[0], D[1]);  // Forklift2
    }

    fclose(outputFile);
    printf("GeoGebra formatinda '%s' dosyasina yazildi.\n", OUTPUT_FILE);

    return 0;
}
