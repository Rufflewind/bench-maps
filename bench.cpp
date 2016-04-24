#define _POSIX_C_SOURCE 199309L
#include <assert.h>
#include <stdint.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#ifdef USE_CHRONO
#include <chrono>
#endif
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>

#ifdef USE_CHRONO
/* std::chrono::steady_clock resolution on Linux is quite bad (microseconds) */
auto now()
{
    return std::chrono::steady_clock::now();
}

template<class T>
double duration_since(T t0)
{
    return std::chrono::duration<double, std::chrono::seconds::period>(
        std::chrono::steady_clock::now() - t0).count();
}
#else
double now()
{
    struct timespec tp;
    clock_gettime(CLOCK_MONOTONIC, &tp);
    return tp.tv_sec + tp.tv_nsec * 1e-9;
}

double duration_since(double t0)
{
    return now() - t0;
}
#endif

template<class Map, class Int, class RNG>
void bench(Int max, size_t repeats, size_t count, RNG &rng)
{
    std::uniform_int_distribution<Int> uniform(0, max - 1);
    uint8_t sum = 0;

    Map m;

    std::cout <<
        "{ \"insert\":\n"
        "[ [\"iter\", \"size\", \"time\"]\n";
    for (size_t k = 0; k != count; ++k) {
        const auto t0 = now();
        for (size_t r = 0; r != repeats; ++r) {
            const Int k = uniform(rng);
            m.emplace(k, k - 1);
        }
        const auto t = duration_since(t0);
        std::cout << ", [" << ((k + 1) * repeats)
                  << ", " << m.size()
                  << ", " << t
                  << "]\n";
    }

    std::cout <<
        "]\n"
        ", \"lookup\":\n"
        "[ [\"iter\", \"misses\", \"time\"]\n";
    for (size_t k = 0; k != count; ++k) {
        size_t misses = 0;
        const auto t0 = now();
        for (size_t r = 0; r < repeats; ++r) {
            const Int k = uniform(rng);
            const auto it = m.find(k);
            if (it == m.end()) {
                ++misses;
            } else {
                sum += (uint8_t)it->second;
            }
        }
        const auto t = duration_since(t0);
        std::cout << ", [" << ((k + 1) * repeats)
                  << ", " << misses
                  << ", " << t
                  << "]\n";
    }

    std::cout <<
        "]\n"
        ", \"rng\":\n"
        "[ [\"time\"]\n";
    for (size_t k = 0; k != count; ++k) {
        const auto t0 = now();
        for (size_t r = 0; r < repeats; ++r) {
            const Int k = uniform(rng);
            sum += k;
        }
        const auto t = duration_since(t0);
        std::cout << ", [" << t
                  << "]\n";
    }

    std::cout <<
        "]\n"
        "}\n"
        "// ignore this: " << (int)sum << "\n";
}

int main(int argc, char **argv)
{
    typedef int64_t Int;
    std::random_device rdev;
    std::mt19937 rng(rdev());

    assert(argc == 4);
    Int max = atoi(argv[1]);
    size_t repeats = atoi(argv[2]);
    size_t count = atoi(argv[3]);

    std::cout << "{ \"_lang\": \"cpp\", \"map\":\n";
    bench<std::map<Int, Int>, Int>(max, repeats, count, rng);

    std::cout << ", \"unordered_map\":\n";
    bench<std::unordered_map<Int, Int>, Int>(max, repeats, count, rng);
    std::cout << "}\n";

    return 0;
}
