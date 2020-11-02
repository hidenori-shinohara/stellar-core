// Copyright 2020 Stellar Development Foundation and contributors. Licensed
// under the Apache License, Version 2.0. See the COPYING file at the root
// of this distribution or at http://www.apache.org/licenses/LICENSE-2.0

#include "history/HistoryArchiveReportWork.h"
#include "historywork/GetHistoryArchiveStateWork.h"
#include "util/Logging.h"
#include <Tracy.hpp>
#include <fmt/format.h>

namespace stellar
{
HistoryArchiveReportWork::HistoryArchiveReportWork(
    Application& app,
    std::vector<std::shared_ptr<HistoryArchive>> const& archives)
    : Work(app, "history-archive-report-work", BasicWork::RETRY_NEVER)
    , mGetHistoryArchiveStateWorks()
    , mAdded(false)
    , mArchives(archives)
{
}

BasicWork::State
HistoryArchiveReportWork::doWork()
{
    ZoneScoped;

    if (!mAdded)
    {
        for (auto const& archive : mArchives)
        {
            mGetHistoryArchiveStateWorks.push_back(
                addWork<GetHistoryArchiveStateWork>(
                    0, archive, "archive-report-" + archive->getName(),
                    BasicWork::RETRY_NEVER));
        }
        mAdded = true;
    }

    if (allChildrenDone())
    {
        bool allSuccess = true;
        for (auto const& work : mGetHistoryArchiveStateWorks)
        {
            allSuccess &= work->getState() == State::WORK_SUCCESS;
        }
        if (!allSuccess)
        {
            // This assert seems to always fail.
            assert(!allChildrenSuccessful());
        }
        if (allChildrenSuccessful())
        {
            return State::WORK_SUCCESS;
        }
        else
        {
            return State::WORK_FAILURE;
        }
    }

    if (anyChildRunning())
    {
        return State::WORK_RUNNING;
    }

    return State::WORK_WAITING;
}

void
HistoryArchiveReportWork::logReports()
{
    for (auto const& work : mGetHistoryArchiveStateWorks)
    {
        if (work->getState() == State::WORK_SUCCESS)
        {
            CLOG(INFO, "History") << fmt::format(
                "Archive information: [name: {}, server: {}, currentLedger: "
                "{}]",
                work->getArchive()->getName(),
                work->getHistoryArchiveState().server,
                work->getHistoryArchiveState().currentLedger);
        }
    }
}

void
HistoryArchiveReportWork::onFailureRaise()
{
    logReports();
    CLOG(INFO, "History") << "HistoryArchiveReport failed for some archive(s)";
    Work::onFailureRaise();
}

void
HistoryArchiveReportWork::onSuccess()
{
    logReports();
    CLOG(INFO, "History") << "HistoryArchiveReport succeeded for all archives";
    Work::onSuccess();
}
}
