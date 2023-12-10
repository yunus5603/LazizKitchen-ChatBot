CREATE DATABASE  IF NOT EXISTS 'laziz_kitchen' ;
USE 'laziz_kitchen';

DROP TABLE IF EXISTS 'food_items';

CREATE TABLE 'food_items' (
  'item_id' int NOT NULL,
  'name' varchar(255) DEFAULT NULL,
  'price' decimal(10,2) DEFAULT NULL,
  PRIMARY KEY ('item_id')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES 'food_items' WRITE;

INSERT INTO 'food_items' VALUES (1,'Pav Bhaji',6.00),(2,'Chole Bhature',7.00),(3,'Pizza',8.00),(4,'Mango Lassi',5.00),(5,'Masala Dosa',6.00),(6,'Vegetable Biryani',9.00),(7,'Vada Pav',4.00),(8,'Rava Dosa',7.00),(9,'Samosa',5.00);

UNLOCK TABLES;


DROP TABLE IF EXISTS 'order_tracking';

CREATE TABLE 'order_tracking' (
  'order_id' int NOT NULL,
  'status' varchar(255) DEFAULT NULL,
  PRIMARY KEY ('order_id')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES 'order_tracking' WRITE;

INSERT INTO 'order_tracking' VALUES (40,'delivered'),(41,'in transit');

UNLOCK TABLES;


DROP TABLE IF EXISTS 'orders';

CREATE TABLE 'orders' (
  'order_id' int NOT NULL,
  'item_id' int NOT NULL,
  'quantity' int DEFAULT NULL,
  'total_price' decimal(10,2) DEFAULT NULL,
  PRIMARY KEY ('order_id','item_id'),
  KEY 'orders_ibfk_1' ('item_id'),
  CONSTRAINT 'orders_ibfk_1' FOREIGN KEY ('item_id') REFERENCES 'food_items' ('item_id')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES 'orders' WRITE;

INSERT INTO 'orders' VALUES (40,1,2,12.00),(40,3,1,8.00),(41,4,3,15.00),(41,6,2,18.00),(41,9,4,20.00);

UNLOCK TABLES;

DELIMITER ;;
CREATE DEFINER='root'@'localhost' FUNCTION 'get_price_for_item'(p_item_name VARCHAR(255)) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
    DECLARE v_price DECIMAL(10, 2);
    
    -- Check if the item_name exists in the food_items table
    IF (SELECT COUNT(*) FROM food_items WHERE name = p_item_name) > 0 THEN
        -- Retrieve the price for the item
        SELECT price INTO v_price
        FROM food_items
        WHERE name = p_item_name;
        
        RETURN v_price;
    ELSE
        -- Invalid item_name, return -1
        RETURN -1;
    END IF;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE DEFINER='root'@'localhost' FUNCTION 'get_total_order_price'(p_order_id INT) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
    DECLARE v_total_price DECIMAL(10, 2);
    
    -- Check if the order_id exists in the orders table
    IF (SELECT COUNT(*) FROM orders WHERE order_id = p_order_id) > 0 THEN
        -- Calculate the total price
        SELECT SUM(total_price) INTO v_total_price
        FROM orders
        WHERE order_id = p_order_id;
        
        RETURN v_total_price;
    ELSE
        -- Invalid order_id, return -1
        RETURN -1;
    END IF;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE DEFINER='root'@'localhost' PROCEDURE 'insert_order_item'(
  IN p_food_item VARCHAR(255),
  IN p_quantity INT,
  IN p_order_id INT
)
BEGIN
    DECLARE v_item_id INT;
    DECLARE v_price DECIMAL(10, 2);
    DECLARE v_total_price DECIMAL(10, 2);

    -- Get the item_id and price for the food item
    SET v_item_id = (SELECT item_id FROM food_items WHERE name = p_food_item);
    SET v_price = (SELECT get_price_for_item(p_food_item));

    -- Calculate the total price for the order item
    SET v_total_price = v_price * p_quantity;

    -- Insert the order item into the orders table
    INSERT INTO orders (order_id, item_id, quantity, total_price)
    VALUES (p_order_id, v_item_id, p_quantity, v_total_price);
END ;;
DELIMITER ;

