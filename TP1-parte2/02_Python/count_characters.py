import threading
import time
import sys

def count_characters(lines, start, end, partial_results, index):
    """Counts the number of characters in a subset of lines"""
    count = 0
    for i in range(start, end):
        count += len(lines[i].rstrip('\r\n'))  # quitar saltos de línea
    partial_results[index] = count


def main(file_path, n_threads):
    # Read file into memory
    with open(file_path, "r") as f:
        lines = f.readlines()

    total_lines = len(lines)
    if n_threads > total_lines:
        n_threads = total_lines  # no more threads than lines

    partial_results = [0] * n_threads
    threads = []

    # Start measuring time
    start_time = time.time()

    # Divide work among threads
    block = total_lines // n_threads
    remainder = total_lines % n_threads

    start_line = 0
    for i in range(n_threads):
        end_line = start_line + block + (1 if i < remainder else 0)
        t = threading.Thread(target=count_characters,
                             args=(lines, start_line, end_line, partial_results, i))
        threads.append(t)
        t.start()
        start_line = end_line

    # Wait for all threads
    for t in threads:
        t.join()

    # Sum results
    total_result = sum(partial_results)

    # End of timing and compute durations in milliseconds
    end_time = time.time()
    duration_sec = end_time - start_time           # duration total in seconds
    total_milliseconds = duration_sec * 1000      # convert to milliseconds

    average_one_line_ms = total_milliseconds / total_lines           # average per line
    average_half_lines_ms = total_milliseconds / (total_lines / 2.0) # average per L/2 lines

    # Print results
    print(f"Total Result (number of characters): {total_result}")
    print(f"Total processing time: {total_milliseconds:.3f} ms")
    print(f"Average time per line: {average_one_line_ms:.3f} ms")
    print(f"Average time per L/2 lines: {average_half_lines_ms:.3f} ms")

if __name__ == "__main__":
    file_path = sys.argv[1]
    n_threads = int(sys.argv[2])
    main(file_path, n_threads)