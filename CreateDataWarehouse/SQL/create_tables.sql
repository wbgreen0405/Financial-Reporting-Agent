-- Advisors table
IF OBJECT_ID('Advisors', 'U') IS NOT NULL
DROP TABLE Advisors;
GO

CREATE TABLE Advisors (
    AdvisorID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    ContactInfo NVARCHAR(100)
);
GO

-- Clients table
IF OBJECT_ID('Clients', 'U') IS NOT NULL
DROP TABLE Clients;
GO

CREATE TABLE Clients (
    ClientID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    ContactInfo NVARCHAR(100),
    AdvisorID INT,
    RiskProfile NVARCHAR(50),
    FOREIGN KEY (AdvisorID) REFERENCES Advisors(AdvisorID)
);
GO

-- Accounts table
IF OBJECT_ID('Accounts', 'U') IS NOT NULL
DROP TABLE Accounts;
GO

CREATE TABLE Accounts (
    AccountID INT IDENTITY(1,1) PRIMARY KEY,
    AccountType NVARCHAR(50) NOT NULL,
    ClientID INT,
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);
GO

-- Assets table
IF OBJECT_ID('Assets', 'U') IS NOT NULL
DROP TABLE Assets;
GO

CREATE TABLE Assets (
    AssetID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    AssetType NVARCHAR(50),
    CurrentValue DECIMAL(18, 2)
);
GO

-- Transactions table
IF OBJECT_ID('Transactions', 'U') IS NOT NULL
DROP TABLE Transactions;
GO

CREATE TABLE Transactions (
    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
    AccountID INT,
    AssetID INT,
    Date DATETIME,
    Type NVARCHAR(50),
    Amount DECIMAL(18, 2),
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    FOREIGN KEY (AssetID) REFERENCES Assets(AssetID)
);
GO

-- Portfolios table
IF OBJECT_ID('Portfolios', 'U') IS NOT NULL
DROP TABLE Portfolios;
GO

CREATE TABLE Portfolios (
    PortfolioID INT IDENTITY(1,1) PRIMARY KEY,
    ClientID INT,
    Name NVARCHAR(100),
    RiskLevel NVARCHAR(50),
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);
GO

-- PortfolioAssets table
IF OBJECT_ID('PortfolioAssets', 'U') IS NOT NULL
DROP TABLE PortfolioAssets;
GO

CREATE TABLE PortfolioAssets (
    PortfolioAssetID INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioID INT,
    AssetID INT,
    Allocation DECIMAL(18, 2),
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID),
    FOREIGN KEY (AssetID) REFERENCES Assets(AssetID)
);
GO

-- Projections table
IF OBJECT_ID('Projections', 'U') IS NOT NULL
DROP TABLE Projections;
GO

CREATE TABLE Projections (
    ProjectionID INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioID INT,
    FutureValue DECIMAL(18, 2),
    ProjectionDate DATETIME,
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID)
);
GO
