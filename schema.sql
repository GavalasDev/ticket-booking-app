BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "User" (
	"email"	TEXT,
	"password"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("email")
);
CREATE TABLE IF NOT EXISTS "Category" (
	"name"	TEXT,
	PRIMARY KEY("name")
);
CREATE TABLE IF NOT EXISTS "Reservation" (
	"number"	INTEGER,
	"user_email"	TEXT NOT NULL,
	"receipt_num"	INTEGER NOT NULL,
	"datetime"	TEXT NOT NULL,
	"tickets_no"	INTEGER NOT NULL DEFAULT 1 CHECK("tickets_no" > 0),
	"happening_id"	INTEGER NOT NULL,
	FOREIGN KEY("happening_id") REFERENCES "Happening"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	FOREIGN KEY("user_email") REFERENCES "User"("email") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("number" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Seat" (
	"id"	INTEGER,
	"number"	TEXT NOT NULL,
	"location_id"	INTEGER NOT NULL,
	"type"	INTEGER,
	FOREIGN KEY("location_id") REFERENCES "Location"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Happening" (
	"id"	INTEGER,
	"event_id"	INTEGER NOT NULL,
	"datetime"	TEXT NOT NULL,
	"location_id"	INTEGER NOT NULL,
	"available_seats"	INTEGER NOT NULL DEFAULT 0 CHECK("available_seats" >= 0),
	FOREIGN KEY("location_id") REFERENCES "Location"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	FOREIGN KEY("event_id") REFERENCES "Event"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Ticket" (
	"barcode"	INTEGER,
	"name"	TEXT NOT NULL,
	"reservation_num"	INTEGER NOT NULL,
	"seat_id"	INTEGER NOT NULL,
	"happening_id"	INTEGER NOT NULL,
	FOREIGN KEY("happening_id") REFERENCES "Happening"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	FOREIGN KEY("reservation_num") REFERENCES "Reservation"("number") ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY("seat_id") REFERENCES "Seat"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	PRIMARY KEY("barcode" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Location" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"description"	INTEGER,
	"latitude"	REAL NOT NULL CHECK("latitude" >= -90 AND "latitude" <= 90),
	"longitude"	REAL NOT NULL CHECK("longitude" >= -180 AND "longitude" <= 180),
	"capacity"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Event" (
	"id"	INTEGER,
	"description"	TEXT,
	"name"	TEXT NOT NULL,
	"category"	TEXT,
	FOREIGN KEY("category") REFERENCES "Category"("name") ON DELETE SET NULL ON UPDATE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE INDEX IF NOT EXISTS "ticket_happening_id_index" ON "Ticket" (
	"happening_id"
);
CREATE INDEX IF NOT EXISTS "seat_location_id_index" ON "Seat" (
	"location_id"
);
CREATE INDEX IF NOT EXISTS "ticket_seat_id_index" ON "Ticket" (
	"seat_id"
);
CREATE INDEX IF NOT EXISTS "happening_location_id_index" ON "Happening" (
	"location_id"
);
CREATE INDEX IF NOT EXISTS "happening_available_seats_index" ON "Happening" (
	"available_seats"
);
CREATE INDEX IF NOT EXISTS "event_name_index" ON "Event" (
	"name"
);
CREATE INDEX IF NOT EXISTS "happening_event_id_index" ON "Happening" (
	"event_id"
);
CREATE INDEX IF NOT EXISTS "happening_datetime_index" ON "Happening" (
	"datetime"
);
CREATE INDEX IF NOT EXISTS "location_name_index" ON "Location" (
	"name"
);
CREATE INDEX IF NOT EXISTS "reservation_user_email_index" ON "Reservation" (
	"user_email"
);
CREATE INDEX IF NOT EXISTS "reservation_happening_id_index" ON "Reservation" (
	"happening_id"
);
CREATE INDEX IF NOT EXISTS "seat_number_index" ON "Seat" (
	"number"
);
CREATE INDEX IF NOT EXISTS "ticket_reservation_num_index" ON "Ticket" (
	"reservation_num"
);
CREATE TRIGGER check_ticket_count_before_insert BEFORE INSERT ON Ticket
BEGIN
  SELECT
    CASE
      WHEN (SELECT tickets_no FROM Reservation WHERE number = NEW.reservation_num) - 1 < (SELECT COUNT(*) FROM Ticket WHERE reservation_num = NEW.reservation_num)
      THEN RAISE(ABORT, 'Number of tickets exceeds reservation ticket count')
    END;
END;
CREATE TRIGGER check_seat_location_before_insert BEFORE INSERT ON Ticket
BEGIN
  SELECT
    CASE
      WHEN (SELECT location_id FROM Seat WHERE id = NEW.seat_id) <> (SELECT location_id FROM Happening WHERE id = NEW.happening_id) THEN
        RAISE(ABORT, 'Seat does not belong to happening location')
    END;
END;
CREATE TRIGGER available_seats_after_insert AFTER INSERT ON Reservation
BEGIN
  UPDATE Happening
  SET available_seats = available_seats - NEW.tickets_no
  WHERE id = NEW.happening_id;
END;
CREATE TRIGGER reservation_date_check_before_insert BEFORE INSERT ON Reservation
BEGIN
  SELECT
    CASE
      WHEN NEW.datetime > (SELECT h.datetime FROM Happening h WHERE h.id = NEW.happening_id) THEN
        RAISE(ABORT, 'Reservation date must be earlier than happening date')
    END;
END;
CREATE TRIGGER reservation_date_check_before_update BEFORE UPDATE ON Reservation
BEGIN
  SELECT
    CASE
      WHEN NEW.datetime > (SELECT h.datetime FROM Happening h WHERE h.id = NEW.happening_id) THEN
        RAISE(ABORT, 'Reservation date must be earlier than happening date')
    END;
END;
CREATE TRIGGER check_seat_location_before_update BEFORE UPDATE ON Ticket
BEGIN
  SELECT
    CASE
      WHEN (SELECT location_id FROM Seat WHERE id = NEW.seat_id) <> (SELECT location_id FROM Happening WHERE id = NEW.happening_id) THEN
        RAISE(ABORT, 'Seat does not belong to happening location')
    END;
END;
CREATE TRIGGER check_ticket_count_before_update BEFORE UPDATE ON Ticket
BEGIN
  SELECT
    CASE
      WHEN (SELECT tickets_no FROM Reservation WHERE number = NEW.reservation_num) - 1 < (SELECT COUNT(*) FROM Ticket WHERE reservation_num = NEW.reservation_num)
      THEN RAISE(ABORT, 'Number of tickets exceeds reservation ticket count')
    END;
END;
CREATE TRIGGER available_seats_after_update AFTER UPDATE ON Reservation
BEGIN
  UPDATE Happening
  SET available_seats = available_seats - NEW.tickets_no + OLD.tickets_no
  WHERE id = NEW.happening_id;
END;
COMMIT;
