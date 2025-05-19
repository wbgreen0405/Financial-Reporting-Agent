-- PortfolioAssetAllocation View
IF OBJECT_ID('PortfolioAssetAllocation', 'V') IS NOT NULL
DROP VIEW PortfolioAssetAllocation;
GO

CREATE VIEW PortfolioAssetAllocation AS
SELECT
    p.PortfolioID,
    p.Name AS PortfolioName,
    pa.AssetID,
    a.Name AS AssetName,
    pa.Allocation,
    a.CurrentValue,
    (pa.Allocation / 100.0) * a.CurrentValue AS AllocatedValue
FROM
    Portfolios p
JOIN
    PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
JOIN
    Assets a ON pa.AssetID = a.AssetID;
GO

-- ClientPortfolioValue View
IF OBJECT_ID('ClientPortfolioValue', 'V') IS NOT NULL
DROP VIEW ClientPortfolioValue;
GO

CREATE VIEW ClientPortfolioValue AS
SELECT
    c.ClientID,
    c.Name AS ClientName,
    SUM(pa.Allocation * a.CurrentValue / 100.0) AS TotalPortfolioValue
FROM
    Clients c
JOIN
    Portfolios p ON c.ClientID = p.ClientID
JOIN
    PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
JOIN
    Assets a ON pa.AssetID = a.AssetID
GROUP BY
    c.ClientID, c.Name;
GO

-- PortfolioSummary View
IF OBJECT_ID('PortfolioSummary', 'V') IS NOT NULL
DROP VIEW PortfolioSummary;
GO

CREATE VIEW PortfolioSummary AS
SELECT
    p.PortfolioID,
    p.Name AS PortfolioName,
    c.ClientID,
    c.Name AS ClientName,
    SUM(pa.Allocation * a.CurrentValue / 100.0) AS TotalPortfolioValue,
    COUNT(DISTINCT pa.AssetID) AS NumberOfAssets
FROM
    Portfolios p
JOIN
    Clients c ON p.ClientID = c.ClientID
JOIN
    PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
JOIN
    Assets a ON pa.AssetID = a.AssetID
GROUP BY
    p.PortfolioID, p.Name, c.ClientID, c.Name;
GO

-- AccountTransactionHistory View
IF OBJECT_ID('AccountTransactionHistory', 'V') IS NOT NULL
DROP VIEW AccountTransactionHistory;
GO

CREATE VIEW AccountTransactionHistory AS
SELECT TOP 100 PERCENT
    t.TransactionID,
    acc.AccountID, -- 🔵 FIXED here!
    acc.AccountType,
    t.AssetID,
    t.Date,
    t.Type AS TransactionType,
    t.Amount,
    a.CurrentValue
FROM
    Transactions t
JOIN
    Accounts acc ON t.AccountID = acc.AccountID
JOIN
    Assets a ON t.AssetID = a.AssetID
ORDER BY
    t.Date DESC;

GO

-- OverallWealthSummary View
IF OBJECT_ID('OverallWealthSummary', 'V') IS NOT NULL
DROP VIEW OverallWealthSummary;
GO

CREATE VIEW OverallWealthSummary AS
SELECT
    a.AssetType,
    COUNT(a.AssetID) AS NumberOfAssets,
    SUM(a.CurrentValue) AS TotalWealth
FROM
    Assets a
GROUP BY
    a.AssetType;
GO

