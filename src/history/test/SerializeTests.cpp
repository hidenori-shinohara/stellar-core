// Copyright 2018 Stellar Development Foundation and contributors. Licensed
// under the Apache License, Version 2.0. See the COPYING file at the root
// of this distribution or at http://www.apache.org/licenses/LICENSE-2.0

#include "history/HistoryArchive.h"
#include "lib/catch.hpp"

#include <fstream>
#include <string>

using namespace stellar;

TEST_CASE("Serialization round trip", "[history]")
{
    std::vector<std::string> inputFiles = {
        "stellar-history.testnet.6714239.json",
        "stellar-history.livenet.15686975.json",
        "stellar-history.testnet.6714239.networkPassphrase.input.json"};
    std::vector<std::string> outputFiles = {
        "stellar-history.testnet.6714239.json",
        "stellar-history.livenet.15686975.json",
        "stellar-history.testnet.6714239.networkPassphrase.output.json"};
    for (int i = 0; i < inputFiles.size(); i++)
    {
        std::string fnPath = "testdata/";
        std::string inputPath = fnPath + inputFiles[i];
        std::string outputPath = fnPath + outputFiles[i];
        SECTION("Serialize " + inputPath)
        {
            std::ifstream in(inputPath);
            in.exceptions(std::ios::badbit);
            std::string input((std::istreambuf_iterator<char>(in)),
                              std::istreambuf_iterator<char>());

            std::ifstream out(outputPath);
            out.exceptions(std::ios::badbit);
            std::string output((std::istreambuf_iterator<char>(out)),
                               std::istreambuf_iterator<char>());

            HistoryArchiveState has;

            // Test fromString
            has.fromString(input);
            REQUIRE(output == has.toString());

            // Test load
            has.load(inputPath);
            REQUIRE(output == has.toString());
        }
    }
}
