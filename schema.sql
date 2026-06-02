-- ==========================================
-- 1. ТАБЛИЦЫ-СПРАВОЧНИКИ (Для 3НФ)
-- ==========================================

CREATE TABLE Roles (
    RoleID SERIAL PRIMARY KEY,
    RoleName VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Categories (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Manufacturers (
    ManufacturerID SERIAL PRIMARY KEY,
    ManufacturerName VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Suppliers (
    SupplierID SERIAL PRIMARY KEY,
    SupplierName VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Units (
    UnitID SERIAL PRIMARY KEY,
    UnitName VARCHAR(20) UNIQUE NOT NULL
);

-- ==========================================
-- 2. ОСНОВНЫЕ ТАБЛИЦЫ
-- ==========================================

CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    FullName VARCHAR(150) NOT NULL,
    RoleID INT NOT NULL,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE RESTRICT
);

CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    ProductName VARCHAR(150) NOT NULL,
    ProductDescription TEXT,
    CategoryID INT NOT NULL,
    ManufacturerID INT NOT NULL,
    SupplierID INT NOT NULL,
    UnitID INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL CHECK (Price >= 0), -- Цена не отрицательная
    Discount INT NOT NULL DEFAULT 0 CHECK (Discount >= 0 AND Discount <= 100),
    StockQuantity INT NOT NULL DEFAULT 0 CHECK (StockQuantity >= 0), -- Остаток не отрицательный
    ImagePath VARCHAR(255) DEFAULT 'picture.png', -- Картинка-заглушка по ТЗ
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID) ON DELETE RESTRICT,
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID) ON DELETE RESTRICT,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE RESTRICT,
    FOREIGN KEY (UnitID) REFERENCES Units(UnitID) ON DELETE RESTRICT
);

-- ==========================================
-- 3. ЗАКАЗЫ И СОСТАВ ЗАКАЗА
-- ==========================================

CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    UserID INT NOT NULL,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Status VARCHAR(50) DEFAULT 'Новый' NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE RESTRICT
);

CREATE TABLE OrderItems (
    OrderItemID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    PriceAtPurchase DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT 
    -- КРИТИЧНО ДЛЯ ТЗ: ON DELETE RESTRICT запрещает удалять товар, если он есть в заказе
);