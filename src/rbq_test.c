#include <stdio.h>
#include <stdlib.h>

#include "RbQueue.h"


static void test1(void) {
    struct rbq *q = rbq_create();

    unsigned long long i;
    for (i = 0; i < 32; i++) {
        rbq_push_tail(q, (void *) i);
        printf("pushed %llu\n", i);
    }

    for (int i = 0; i < 32; i++) {
        void *item = rbq_pop_head(q);
        printf("poped: %llu\n", (unsigned long long) item);
    }

    rbq_destroy(q);
}

static void test2(void) {
    struct rbq *q = rbq_create();
    unsigned long long i;
    for (i = 0; i < 5; i++) {
        rbq_push_tail(q, (void *) i);
        printf("pushed %llu\n", i);
    }

    for (i = 0; i < 4; i++) {
        void *item = rbq_pop_head(q);
        printf("poped: %llu\n", (unsigned long long) item);
    }

    for (i = 0; i < 32; i++) {
        rbq_push_tail(q, (void *) i + 5);
        printf("pushed %llu\n", i + 5);
    }

    for (int i = 0; i < 32; i++) {
        void *item = rbq_pop_head(q);
        printf("poped: %llu\n", (unsigned long long) item);
    }

    rbq_destroy(q);
}

static void test_append(void) {
    struct rbq *p = rbq_create();
    struct rbq *q = rbq_create();

    for (long long i = 0; i < 5; i++) {
        rbq_push_tail(p, (void *) i);
    }

    for (long long i = 0; i < 6; i++) {
        rbq_push_tail(q, (void *) i);
    }

    for (int i = 0; i < 4; i++) {
        rbq_pop_head(q);
    }

    for (long long i = 0; i < 4; i++) {
        rbq_push_tail(q, (void *) i);
    }

    rbq_append(q, p);
    printf("q avail: %llu, used: %llu\n", rbq_avail(q), rbq_used(q));
    printf("p avail: %llu, used: %llu\n", rbq_avail(p), rbq_used(p));

    rbq_append(p, q);
    printf("q avail: %llu, used: %llu\n", rbq_avail(q), rbq_used(q));
    printf("p avail: %llu, used: %llu\n", rbq_avail(p), rbq_used(p));

    for (long long i = 20; i < 30; i++) {
        rbq_push_tail(p, (void *) i);
    }

    rbq_append(q, p);
    printf("q avail: %llu, used: %llu\n", rbq_avail(q), rbq_used(q));
    printf("p avail: %llu, used: %llu\n", rbq_avail(p), rbq_used(p));


    printf("queue size of q: %llu\n", rbq_used(q));
    for (int i = 0; i < 21; i++) {
        void *item = rbq_pop_head(q);
        printf("popped %lld\n", (long long) item);
    }

    rbq_destroy(q);
    rbq_destroy(p);

}

static void test_stack(void) {
    struct rbq *q = rbq_create();

#define SIZE 32

    unsigned long long i;
    for (i = 1; i < SIZE + 1; i++) {
        rbq_push_tail(q, (void *) i);
        printf("pushed %llu\n", i);
    }

    struct rbq *p = rbq_create();
    rbq_append_n(p, q, 16);

    for (int i = 1; i < 17; i++) {
        void *item = rbq_pop_tail(p);
        printf("popped from p: %llu\n", (unsigned long long) item);
    }

    for (int i = 1; i < 17; i++) {
        void *item = rbq_pop_tail(q);
        printf("popped from q: %llu\n", (unsigned long long) item);
    }

    rbq_destroy(q);
    rbq_destroy(p);
}

int main(int argc, char *argv[]) {
    // test1();
    // test2();

    // test_append();

    test_stack();

    return 0;
}
