#include <stdint.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>
#include <sqlite3.h>

#define PROG "bench"

static void error_sqlite(void *ctx, int err, const char *msg)
{
    (void)ctx;
    fprintf(stderr, PROG ": [sqlite] %s (%d)\n", msg, err);
    fflush(stderr);
}

static void panic(void)
{
    abort();
}

static double gettime()
{
    struct timespec tp;
    clock_gettime(CLOCK_MONOTONIC, &tp);
    return tp.tv_sec * 1e9 + tp.tv_nsec;
}

int main(void)
{

    sqlite3 *db;
    sqlite3_stmt *stmt;

    if (sqlite3_config(SQLITE_CONFIG_LOG, error_sqlite, NULL))
        panic();

    if (sqlite3_open(":memory:", &db))
        panic();

    if (sqlite3_exec(
            db,
            "CREATE TABLE IF NOT EXISTS data "
            "(key INTEGER PRIMARY KEY, value REAL);",
            NULL, NULL, NULL))
        panic();

    if (sqlite3_exec(db, "BEGIN;", NULL, NULL, NULL))
        panic();

    if (sqlite3_prepare_v2(
            db,
            "INSERT OR REPLACE INTO data (key, value) VALUES (?, ?);",
            -1, &stmt, NULL))
        panic();

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int64_t> dis(0, 2147483647);

    std::cout << dis(gen) << std::endl;
    for (int64_t n = 1; n < (1 << 25); n *= 2) {
#if 0
        std::map<int64_t, double> m;
#else
        std::unordered_map<int64_t, double> m;
#endif
        double t = gettime();
        for (int i = 0; i < n; ++i) {
            int64_t key = dis(gen);
            int64_t value = 1;
#if 0
            if (sqlite3_bind_int64(stmt, 1, key))
                panic();

            if (sqlite3_bind_int64(stmt, 2, value))
                panic();

            if (sqlite3_step(stmt) != SQLITE_DONE)
                panic();

            if (sqlite3_reset(stmt))
                panic();
#else
            m[key] = value;
//            m.erase(key);
#endif

        };
        double dt = (gettime() - t) / n;
        std::cout << n << "\t" << dt << std::endl;
    }

    if (sqlite3_finalize(stmt))
        panic();

    if (sqlite3_exec(db, "END; VACUUM;", NULL, NULL, NULL))
        panic();

    if (sqlite3_close(db))
        panic();

    return 0;
}
