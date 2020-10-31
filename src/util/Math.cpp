// Copyright 2014 Stellar Development Foundation and contributors. Licensed
// under the Apache License, Version 2.0. See the COPYING file at the root
// of this distribution or at http://www.apache.org/licenses/LICENSE-2.0

#include "Math.h"
#include "util/GlobalChecks.h"
#include <Tracy.hpp>
#include <algorithm>
#include <cmath>
#include <numeric>
#include <set>
#include <unordered_map>

namespace stellar
{

std::default_random_engine gRandomEngine;
std::uniform_real_distribution<double> uniformFractionDistribution(0.0, 1.0);

double
rand_fraction()
{
    return uniformFractionDistribution(gRandomEngine);
}

bool
rand_flip()
{
    return (gRandomEngine() & 1);
}

double
closest_cluster(double p, std::set<double> const& centers)
{
    auto bestCenter = std::numeric_limits<double>::max();
    auto currDist = std::numeric_limits<double>::max();
    for (auto const& c : centers)
    {
        auto newDist = std::fabs(c - p);
        if (newDist < currDist)
        {
            bestCenter = c;
            currDist = newDist;
        }
        else
        {
            break;
        }
    }

    return bestCenter;
}

std::set<double>
k_means(std::vector<double> const& points, uint32_t k)
{
    ZoneScoped;

    if (k == 0)
    {
        throw std::runtime_error("k_means: k must be positive");
    }

    if (points.size() < k)
    {
        return std::set<double>(points.begin(), points.end());
    }

    std::vector<double> a(points);
    std::sort(a.begin(), a.end());
    int n = a.size();

    const double MAXIMUM_DOUBLE = std::numeric_limits<double>::max();

    // https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5148156/
    // The dp array corresponds to the D array in the article.
    // bestMeans and bestIndices help us extract the best j chosen in the end.
    std::vector<std::vector<double>> dp(n + 1), bestMeans(n + 1),
        bestIndices(n + 1);

    for (int i = 0; i <= n; i++)
    {
        dp[i].resize(k + 1);
        bestMeans[i].resize(k + 1);
        bestIndices[i].resize(k + 1);
    }

    for (int i = 0; i < n; i++)
    {
        // If k = 0, then the best distance is "infinity."
        dp[i + 1][0] = MAXIMUM_DOUBLE;
        for (int kk = 1; kk <= k; kk++)
        {
            double bestDist = std::numeric_limits<double>::max();
            double bestMean(0), sum(0), sumSquares(0);
            int bestIndex = -1;
            for (int j = i; j >= 0; j--)
            {
                sum += a[j];
                sumSquares += a[j] * a[j];
                if (dp[j][kk - 1] < MAXIMUM_DOUBLE)
                {
                    int m = i - j + 1;
                    double currentDist =
                        dp[j][kk - 1] + sumSquares - sum * sum / m;
                    if (currentDist < bestDist)
                    {
                        bestDist = currentDist;
                        bestMean = sum / m;
                        bestIndex = j;
                    }
                }
            }
            dp[i + 1][kk] = bestDist;
            bestMeans[i + 1][kk] = bestMean;
            bestIndices[i + 1][kk] = bestIndex;
        }
    }
    std::set<double> results;
    for (int i = n - 1, kk = k; kk >= 1; kk--)
    {
        results.insert(bestMeans[i + 1][kk]);
        i = bestIndices[i + 1][kk] - 1;
    }
    return results;
}
}
