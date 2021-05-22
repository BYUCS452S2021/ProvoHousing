
PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS Housing;
DROP TABLE IF EXISTS MarriedHousing;
DROP TABLE IF EXISTS SingleHousing;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS AuthTokens;
DROP TABLE IF EXISTS Listings;
DROP TABLE IF EXISTS Watching;

CREATE TABLE Housing (
	roomId INT PRIMARY KEY AUTOINCREMENT,
	addressFull VARCHAR(255),
	pricePerMonth INT,
	startAvailability DATE,
	endAvailability DATE,
	endContract DATE,
	hasWasher BOOLEAN,
	HasDishwasher BOOLEAN,
	photoLink VARCHAR(450)
);

CREATE TABLE MarriedHousing (
	roomId INT PRIMARY KEY,
	numBedrooms INT,
	FOREIGN KEY(roomId) REFERENCES Housing(roomId)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);

CREATE TABLE SingleHousing (
	roomId INT PRIMARY KEY,
    isShared BOOLEAN,
	numRoommates INT,
	isMale BOOLEAN,
	isBYUApproved BOOLEAN,
	FOREIGN KEY(roomId) REFERENCES Housing(roomId)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);

CREATE TABLE Users (
	userId VARCHAR(50) PRIMARY KEY UNIQUE,
    firstName VARCHAR(50),
	lastName VARCHAR(50),
    password VARCHAR(50),
    email VARCHAR(50) UNIQUE,
	phone VARCHAR(15)
);

CREATE TABLE AuthTokens (
	userId VARCHAR(50),
	authToken VARCHAR(100),
	FOREIGN KEY(userId) REFERENCES User(userId)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE Listings (
	userId VARCHAR(50),
    roomId INT,
	listingDate DATE,
	showPhoneOnListing BOOLEAN,
		 PRIMARY KEY (userId, roomId),
        FOREIGN KEY(userId) REFERENCES User(userId)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	    FOREIGN KEY(roomId) REFERENCES Housing(roomId)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE Watching (
	userId VARCHAR(50),
    roomId INT,
		PRIMARY KEY (userId, roomId),
        FOREIGN KEY(userId) REFERENCES User(userId)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	    FOREIGN KEY(roomId) REFERENCES Housing(roomId)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

PRAGMA foreign_keys=on;
