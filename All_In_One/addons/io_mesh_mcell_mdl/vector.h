#ifndef VECTOR_H
#define VECTOR_H

/* Header file for 3D vector routines */

/* Size constants */
/* EPS_C is the fractional difference between two values that is considered meaningful */
#define EPS_C 1e-12

struct vector2 {
	double u;
	double v;
};

struct vector3 {
	double x;
	double y;
	double z;
};

void mult_matrix(double (*m1)[4], double (*m2)[4], double (*om)[4], short unsigned int l, short unsigned int m, short unsigned int n);
void normalize(struct vector3 *v);
void init_matrix(double (*im)[4]);
void scale_matrix(double (*im)[4], double (*om)[4], struct vector3 *scale);
void translate_matrix(double (*im)[4], double (*om)[4], struct vector3 *translate);
void rotate_matrix(double (*im)[4], double (*om)[4], struct vector3 *axis, double angle);
void tform_matrix(struct vector3 *scale, struct vector3 *translate, struct vector3 *axis, double angle, double (*om)[4]);
void vectorize(struct vector3 *p1, struct vector3 *p2, struct vector3 *v);
double vect_length(struct vector3 *v);
double dot_prod(struct vector3 *v1, struct vector3 *v2);
void cross_prod(struct vector3 *v1, struct vector3 *v2, struct vector3 *v3);
void vect_sum(struct vector3 *v1, struct vector3 *v2, struct vector3 *v3);
void scalar_prod(struct vector3 *v1, double a, struct vector3 *result);

int distinguishable(double a,double b,double eps);
int distinguishable_vec3(struct vector3 *a,struct vector3 *b,double eps);
int distinguishable_vec2(struct vector2 *a,struct vector2 *b,double eps);

double distance_vec3(struct vector3 *a, struct vector3 *b);
double distance_vec2(struct vector2 *a, struct vector2 *b);

int parallel_segments(struct vector3 *A, struct vector3 *B, struct vector3 *R, struct vector3 *S);

int point_in_triangle(struct vector3 *p, struct vector3 *a, struct vector3 *b, struct vector3 *c);
int same_side(struct vector3 *p1, struct vector3 *p2, struct vector3 *a, struct vector3 *b);

int intersect_point_segment(struct vector3 *P, struct vector3 *A, struct vector3 *B);
int intersect_two_segments(struct vector2 *A, struct vector2 *B, struct vector2 *C, struct vector2 *D, double *r_param, double *s_param);
int intersect_ray_segment(struct vector2 *A, struct vector2 *B, struct vector2 *C, struct vector2 *D, struct vector2 *P);

double cross2D(struct vector2 *a, struct vector2 *b);
void vectorize2D(struct vector2 *p1, struct vector2 *p2, struct vector2 *p3);
int point_in_triangle_2D(struct vector2 *p, struct vector2 *a, struct vector2 *b, struct vector2 *c);
#endif
