-- users
INSERT INTO users (user_name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)

-- locations
INSERT INTO locations (user_id, location_name) VALUES (%s, %s)
INSERT INTO locations (user_id, location_name, description) VALUES (%s, %s, %s)

-- data
INSERT INTO data (location_id, user_id, ph, bod, cod, temperature, ammonia, arsenic, calcium, ec, coliform, hardness, lead_pb, nitrogen, sodium, sulfate, tss, turbidity) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
