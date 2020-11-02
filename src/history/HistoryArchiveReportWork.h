#pragma once

// Copyright 2020 Stellar Development Foundation and contributors. Licensed
// under the Apache License, Version 2.0. See the COPYING file at the root
// of this distribution or at http://www.apache.org/licenses/LICENSE-2.0

#include "history/HistoryArchive.h"
#include "work/Work.h"

namespace stellar
{
class GetHistoryArchiveStateWork;
class HistoryArchiveReportWork : public Work
{
  protected:
    BasicWork::State doWork() override;
    void onSuccess() override;
    void onFailureRaise() override;

  public:
    HistoryArchiveReportWork(
        Application& app,
        std::vector<std::shared_ptr<HistoryArchive>> const& archives);

  private:
    std::vector<std::shared_ptr<GetHistoryArchiveStateWork>>
        mGetHistoryArchiveStateWorks;
    bool mAdded;
    void logReports();
    std::vector<std::shared_ptr<HistoryArchive>> const& mArchives;
};
}
