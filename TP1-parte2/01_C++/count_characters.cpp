#include <iostream>
#include <fstream>
#include <vector>
#include <thread>
#include <chrono>
#include <string>

using namespace std;

// Function that counts characters in a range of lines
void countCharacters(const vector<string>& lines,
                     size_t start, size_t end,
                     long long &partialResult) {
    long long count = 0;
    for (size_t i = start; i < end; ++i) {
        count += lines[i].size();
    }
    partialResult = count;
}

int main(int argc, char* argv[]) {
    string filePath = argv[1];
    int N = stoi(argv[2]);

    // Read the file into memory
    ifstream file(filePath);
    if (!file.is_open()) {
        cerr << "Error: could not open the file.\n";
        return 1;
    }

    vector<string> lines;
    string line;
    while (getline(file, line)) {
        lines.push_back(line);
    }
    file.close();

    size_t totalLines = lines.size();
    if (N > totalLines) N = totalLines; // no more threads than lines

    vector<thread> threads;
    vector<long long> partialResults(N, 0);

    // Start measuring time
    auto startTime = chrono::high_resolution_clock::now();

    // Divide work among threads
    size_t block = totalLines / N;
    size_t remainder = totalLines % N;

    size_t startLine = 0;
    for (int i = 0; i < N; i++) {
        size_t endLine = startLine + block + (i < remainder ? 1 : 0);
        thread t(countCharacters, cref(lines), startLine, endLine, ref(partialResults[i]));
        threads.push_back(move(t));
        startLine = endLine;
    }

    // Wait for all threads to finish
    for (auto &t : threads) {
        t.join();
    }

    // Sum partial results
    long long totalResult = 0;
    for (long long pr : partialResults) {
        totalResult += pr;
    }

    auto endTime = chrono::high_resolution_clock::now();
chrono::duration<double, std::milli> duration_ms = endTime - startTime; // duración en ms
double totalMilliseconds = duration_ms.count();

double average_one_line_ms = totalMilliseconds / totalLines;        // promedio por línea en ms
double average_half_lines_ms = totalMilliseconds / (totalLines / 2.0); // promedio por L/2 líneas en ms

cout << "Total Result (number of characters): " << totalResult << "\n";
cout << "Total processing time: " << totalMilliseconds << " ms\n";
cout << "Average time per line: " << average_one_line_ms << " ms\n";
cout << "Average time per L/2 lines: " << average_half_lines_ms << " ms\n";




    return 0;
}
