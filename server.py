from flask import Flask, request, jsonify
import psycopg2
import re
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

def is_valid_date(date_str):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(date_pattern, date_str) is not None

@app.route('/api/countries', methods=['POST'])
def add_country():
    data = request.get_json()
    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO countries (name, latitude, longitude) VALUES (%s, %s, %s) RETURNING id",
            (data['nume'], data['lat'], data['lon'])
        )
        country_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'id': country_id}), 201
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Country already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, latitude, longitude FROM countries")
        rows = cursor.fetchall()
        conn.close()
        countries = [
            { "id": row[0], "nume": row[1], "lat": row[2], "lon": row[3] }
            for row in rows
        ]
        return jsonify(countries), 200
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route('/api/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    data = request.get_json()
    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM countries WHERE id = %s", (country_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute(
            "UPDATE countries SET name = %s, latitude = %s, longitude = %s WHERE id = %s",
            (data['nume'], data['lat'], data['lon'], country_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Country updated successfully'}), 200
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Invalid input: country name already exists'}), 409
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/api/countries/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM countries WHERE id = %s", (country_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute("DELETE FROM countries WHERE id = %s", (country_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Country deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/api/cities', methods=['POST'])
def add_city():
    data = request.get_json()
    if not data or 'idTara' not in data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM countries WHERE id = %s", (data['idTara'],))
        country = cursor.fetchone()
        if not country:
            conn.close()
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute(
            "INSERT INTO cities (country_id, name, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['idTara'], data['nume'], data['lat'], data['lon'])
        )
        city_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'id': city_id}), 201
    except psycopg2.IntegrityError:
        return jsonify({'error': 'City already exists in this country'}), 409
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, country_id, name, latitude, longitude FROM cities")
        rows = cursor.fetchall()
        conn.close()
        cities = [
            {
                "id": row[0],
                "idTara": row[1],
                "nume": row[2],
                "lat": row[3],
                "lon": row[4]
            }
            for row in rows
        ]
        return jsonify(cities), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cities/country/<int:country_id>', methods=['GET'])
def get_cities_by_country(country_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM countries WHERE id = %s", (country_id,))
        country = cursor.fetchone()
        if not country:
            conn.close()
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute(
            "SELECT id, country_id, name, latitude, longitude FROM cities WHERE country_id = %s",
            (country_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        cities = [
            {
                "id": row[0],
                "idTara": row[1],
                "nume": row[2],
                "lat": row[3],
                "lon": row[4]
            }
            for row in rows
        ]
        return jsonify(cities), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cities/<int:city_id>', methods=['PUT'])
def update_city(city_id):
    data = request.get_json()
    if not data or 'idTara' not in data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    if 'id' in data and data['id'] != city_id:
        return jsonify({'error': 'ID in the body does not match the ID in the URL'}), 400
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cities WHERE id = %s", (city_id,))
        city = cursor.fetchone()
        if not city:
            conn.close()
            return jsonify({'error': 'City not found'}), 404
        cursor.execute("SELECT id FROM countries WHERE id = %s", (data['idTara'],))
        country = cursor.fetchone()
        if not country:
            conn.close()
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute(
            "UPDATE cities SET country_id = %s, name = %s, latitude = %s, longitude = %s WHERE id = %s",
            (data['idTara'], data['nume'], data['lat'], data['lon'], city_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'City updated successfully'}), 200
    except psycopg2.IntegrityError:
        return jsonify({'error': 'City name already exists in this country'}), 409
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/api/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cities WHERE id = %s", (city_id,))
        city = cursor.fetchone()
        if not city:
            conn.close()
            return jsonify({'error': 'City not found'}), 404
        cursor.execute("DELETE FROM cities WHERE id = %s", (city_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'City deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400
    
@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    data = request.get_json()
    if not data or 'idOras' not in data or 'valoare' not in data:
        return jsonify({'error': 'Invalid input. idOras and valoare are required'}), 400
    timestamp = data.get('timestamp')
    if timestamp and not is_valid_date(timestamp):
        return jsonify({'error': 'Invalid date format for timestamp. Use AAAA-LL-ZZ'}), 400
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM cities WHERE id = %s", (data['idOras'],))
                city = cursor.fetchone()
                if not city:
                    return jsonify({'error': 'City not found'}), 404
                if timestamp:
                    cursor.execute(
                        "INSERT INTO temperatures (city_id, value, timestamp) VALUES (%s, %s, %s) RETURNING id",
                        (data['idOras'], data['valoare'], timestamp)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO temperatures (city_id, value) VALUES (%s, %s) RETURNING id",
                        (data['idOras'], data['valoare'])
                    )
                temperature_id = cursor.fetchone()[0]
                conn.commit()
                return jsonify({'id': temperature_id}), 201
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Temperature already exists for this city'}), 409
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 400

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    date_from = request.args.get('from')
    date_until = request.args.get('until')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    try:
        query = """
            SELECT t.id, t.value, t.timestamp
            FROM temperatures t
            JOIN cities c ON t.city_id = c.id
            WHERE 1=1
        """
        params = []
        if date_from:
            query += " AND t.timestamp >= %s"
            params.append(date_from)
        if date_until:
            query += " AND t.timestamp <= %s"
            params.append(date_until)
        if lat:
            query += " AND c.latitude = %s"
            params.append(lat)
        if lon:
            query += " AND c.longitude = %s"
            params.append(lon)
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
        temperatures = [
            {
                "id": row[0],
                "valoare": row[1],
                "timestamp": row[2].strftime('%Y-%m-%d')
            }
            for row in results
        ]
        return jsonify(temperatures), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/temperatures/cities/<int:idOras>', methods=['GET'])
def get_temperatures_by_city(idOras):
    date_from = request.args.get('from')
    date_until = request.args.get('until')
    if date_from and not is_valid_date(date_from):
        return jsonify({'error': 'Invalid date format for "from". Use AAAA-LL-ZZ'}), 400
    if date_until and not is_valid_date(date_until):
        return jsonify({'error': 'Invalid date format for "until". Use AAAA-LL-ZZ'}), 400
    try:
        query = """
            SELECT t.id, t.value, t.timestamp
            FROM temperatures t
            WHERE t.city_id = %s
        """
        params = [idOras]
        if date_from:
            query += " AND t.timestamp >= %s"
            params.append(date_from)
        if date_until:
            query += " AND t.timestamp <= %s"
            params.append(date_until)
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM cities WHERE id = %s", (idOras,))
                city = cursor.fetchone()
                if not city:
                    return jsonify({'error': 'City not found'}), 404
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
        temperatures = [
            {
                "id": row[0],
                "valoare": row[1],
                "timestamp": row[2].strftime('%Y-%m-%d')  
            }
            for row in results
        ]
        return jsonify(temperatures), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/temperatures/countries/<int:id_tara>', methods=['GET'])
def get_temperatures_by_country(id_tara):
    date_from = request.args.get('from')
    date_until = request.args.get('until')
    if date_from and not is_valid_date(date_from):
        return jsonify({'error': 'Invalid date format for "from". Use AAAA-LL-ZZ'}), 400
    if date_until and not is_valid_date(date_until):
        return jsonify({'error': 'Invalid date format for "until". Use AAAA-LL-ZZ'}), 400
    try:
        query = """
            SELECT t.id, t.value, t.timestamp
            FROM temperatures t
            JOIN cities c ON t.city_id = c.id
            WHERE c.country_id = %s
        """
        params = [id_tara]
        if date_from:
            query += " AND t.timestamp >= %s"
            params.append(date_from)
        if date_until:
            query += " AND t.timestamp <= %s"
            params.append(date_until)
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM countries WHERE id = %s", (id_tara,))
                country = cursor.fetchone()
                if not country:
                    return jsonify({'error': 'Country not found'}), 404
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
        temperatures = [
            {
                "id": row[0],
                "valoare": row[1],
                "timestamp": row[2].strftime('%Y-%m-%d')
            }
            for row in results
        ]

        return jsonify(temperatures), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/temperatures/<int:temperature_id>', methods=['PUT'])
def update_temperature(temperature_id):
    data = request.get_json()
    if not data or 'id' not in data or data['id'] != temperature_id:
        return jsonify({'error': 'ID in body does not match ID in URL'}), 400
    if 'idOras' not in data or 'valoare' not in data:
        return jsonify({'error': 'Invalid input. idOras and valoare are required'}), 400
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM temperatures WHERE id = %s", (temperature_id,))
                temperature = cursor.fetchone()
                if not temperature:
                    return jsonify({'error': 'Temperature not found'}), 404
                cursor.execute("SELECT id FROM cities WHERE id = %s", (data['idOras'],))
                city = cursor.fetchone()
                if not city:
                    return jsonify({'error': 'City not found'}), 404
                cursor.execute(
                    "UPDATE temperatures SET city_id = %s, value = %s WHERE id = %s",
                    (data['idOras'], data['valoare'], temperature_id)
                )
                conn.commit()
        return jsonify({'message': 'Temperature updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/temperatures/<int:temperature_id>', methods=['DELETE'])
def delete_temperature(temperature_id):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM temperatures WHERE id = %s", (temperature_id,))
                temperature = cursor.fetchone()
                if not temperature:
                    return jsonify({'error': 'Temperature not found'}), 404
                cursor.execute("DELETE FROM temperatures WHERE id = %s", (temperature_id,))
                conn.commit()
        return jsonify({'message': 'Temperature deleted successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Invalid input'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
