from sage.all import *
from sage.repl.load import load
import time
import numpy
import json
import os
from scipy.stats import ttest_ind
import sys
from tqdm import tqdm

# NOTE: Edit this to change the number of iterations
ITERATIONS = 100
# The file to store benchmark results
RESULTS_FILE = "bench_results_glyph.json"
# Significance level for the t-test
ALPHA = 0.05
# Message to sign and verify (for benchmarking)
MESSAGE = b"benchmark"
# Higher resolution timer
CLOCK = time.perf_counter

prev_name = __name__
__name__ = None
load("GLYPH/glyph.sage", globals())
__name__ = prev_name

def bench_keygen():
    """
    Benchmark the keygen method.
    """
    rlwe = GLYPH()
    start = CLOCK()
    rlwe.keygen()
    end = CLOCK()
    return end - start

def bench_sign():
    """
    Benchmark the sign method.
    """
    rlwe = GLYPH()
    _, privkey = rlwe.keygen()
    start = CLOCK()
    rlwe.sign(MESSAGE, privkey)
    end = CLOCK()
    return end - start

def bench_verify():
    """
    Benchmark the verify method.
    """
    rlwe = GLYPH()
    pubkey, privkey = rlwe.keygen()
    signature = rlwe.sign(MESSAGE, privkey)
    start = CLOCK()
    rlwe.verify(MESSAGE, signature, pubkey)
    end = CLOCK()
    return end - start

def remove_outliers(timings):
    """
    Removes outliers from a list of timings using the interquartile range method.
    """
    if not timings:
        return []

    Q1 = numpy.percentile(timings, 25)
    Q3 = numpy.percentile(timings, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return [t for t in timings if lower_bound <= t <= upper_bound]

def get_stats(timings):
    """
    Calculates statistics for a list of timings.
    """
    if not timings:
        return {}

    return {
        "mean": numpy.mean(timings),
        "median": numpy.median(timings),
        "std_dev": numpy.std(timings),
        "min": min(timings),
        "max": max(timings),
        "timings": timings,  # Store raw timings for t-test
    }

def load_baseline():
    """
    Loads the baseline results from the JSON file.
    """
    if not os.path.exists(RESULTS_FILE):
        return {}
    with open(RESULTS_FILE, "r") as f:
        return json.load(f)


def save_results(results):
    """
    Saves the results to the JSON file.
    """
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)


def run_and_analyze_benchmark(name, bench_func):
    """
    Runs a benchmark, analyzes the results, and compares to the baseline.
    """
    print(f"--- {name} ---")

    # Run benchmark and remove outliers
    raw_timings = [(bench_func() * 1000) for _ in tqdm(range(ITERATIONS), desc=name)]
    timings = remove_outliers(raw_timings)

    outliers = len(raw_timings) - len(timings)
    if outliers > 0:
        print(f"Removed {outliers} outliers.")

    # Get new stats
    stats = get_stats(timings)
    if not stats:
        print("No timings to report after outlier removal.")
        return None

    print(f"Mean:       {stats['mean']:.6f} ms")
    print(f"Median:     {stats['median']:.6f} ms")
    print(f"Std Dev:    {stats['std_dev']:.6f} ms")

    # Compare to baseline
    baseline_data = load_baseline().get(name, {})
    if baseline_data and "timings" in baseline_data:
        baseline_timings = baseline_data["timings"]

        # Perform the t-test
        _t_stat, p_value = ttest_ind(
                timings, 
                baseline_timings,
                # Perform Welch's t-test (do not assume equal population variance).
                equal_var=False
        )

        mean_change = (stats["mean"] - baseline_data["mean"]) / baseline_data["mean"]

        if p_value < ALPHA:
            if mean_change > 0:
                print(
                    f"Statistically significant REGRESSION detected ({mean_change:+.2%}, p={p_value:.3f})"
                )
            else:
                print(
                    f"Statistically significant IMPROVEMENT detected ({mean_change:+.2%}, p={p_value:.3f})"
                )
        else:
            print(
                f"No significant change detected ({mean_change:+.2%}, p={p_value:.3f})"
            )

    print("")
    return stats


if __name__ == "__main__":
    print()
    print(f"--- GLYPH Benchmarks (running {ITERATIONS} iterations) ---\n")

    new_results = {}

    benchmarks = {
        "Key Generation": bench_keygen,
        "Signing": bench_sign,
        "Verification": bench_verify,
    }

    for name, func in benchmarks.items():
        result = run_and_analyze_benchmark(name, func)
        if result:
            new_results[name] = result

    if new_results:
        save_results(new_results)
        print(f"Results saved to {RESULTS_FILE}")
