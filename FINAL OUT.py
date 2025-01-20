from flask import Flask, request, jsonify, render_template_string
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'stress_management'
}

# Function to calculate stress index
def calculate_stress(stress_level, sleep_hours, exercise_hours, social_interaction):
    # Stress index formula (example)
    stress_index = (10 - sleep_hours) + (stress_level * 2) - (exercise_hours * 1.5) - social_interaction
    return max(0, min(100, stress_index))  # Ensure stress index is between 0 and 100

# Function to get recommendations based on stress index
def get_recommendations(stress_index):
    if stress_index < 20:
        return "Your stress levels are low. Keep up the good work by maintaining a healthy routine."
    elif 20 <= stress_index < 50:
        return "Your stress levels are moderate. Try to get more sleep, exercise regularly, and spend time with loved ones."
    elif 50 <= stress_index < 80:
        return "Your stress levels are high. Consider relaxation techniques like meditation or yoga and talk to a counselor."
    else:
        return "Your stress levels are critically high. Seek immediate help from a medical professional or counselor."

# Function to recommend doctor based on stress level
def recommend_doctor(stress_level):
    if 61 <= stress_level <= 70:
        return "Doctor 1: General Practitioner"
    elif 71 <= stress_level <= 80:
        return "Doctor 2: Psychologist"
    elif 81 <= stress_level <= 90:
        return "Doctor 3: Psychiatrist"
    elif 91 <= stress_level <= 100:
        return "Doctor 4: Stress Management Specialist"
    else:
        return "No doctor recommendation for stress level."

# Home route with embedded HTML and CSS
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stress Management</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background: url('https://publichealth.jhu.edu/sites/default/files/styles/article_feature/public/2024-09/publicmentalhealth.jpg?h=6e972868&itok=zQIfAxZv') no-repeat center center fixed;
                background-size: cover;
            }

            .container {
                width: 90%;
                max-width: 500px;
                background: rgba(255, 255, 255, 0.8); /* Semi-transparent background */
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease-in-out;
            }

            .container:hover {
                transform: translateY(-5px);
            }

            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 20px;
            }

            label {
                font-weight: bold;
                margin-top: 10px;
                display: block;
            }

            input {
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }

            button {
                width: 100%;
                padding: 10px;
                background-color: #28a745;
                color: #fff;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                cursor: pointer;
                margin-top: 20px;
                transition: background-color 0.3s ease;
            }

            button:hover {
                background-color: #218838;
            }

            .popup {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                justify-content: center;
                align-items: center;
            }

            .popup-content {
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                text-align: center;
                width: 80%;
                max-width: 400px;
            }

            .popup-content h2 {
                color: #333;
            }

            .popup-content p {
                margin: 10px 0;
                color: #555;
            }

            .popup-content button {
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            .popup-content button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stress Management Tool</h1>

            <label for="stress_level">Stress Level (1-100):</label>
            <input type="number" id="stress_level" min="1" max="10">

            <label for="sleep_hours">Sleep Hours (per day):</label>
            <input type="number" id="sleep_hours" min="0" max="24">

            <label for="exercise_hours">Exercise Hours (per week):</label>
            <input type="number" id="exercise_hours" min="0" max="168">

            <label for="social_interaction">Social Interaction Hours (per week):</label>
            <input type="number" id="social_interaction" min="0" max="168">

            <label for="age">Age:</label>
            <input type="number" id="age" min="1" max="120">

            <button id="generateReportBtn">Generate Insights Report</button>
        </div>

        <div id="recommendationsPopup" class="popup">
            <div class="popup-content">
                <h2>Health Recommendations</h2>
                <p id="recommendationsText"></p>
                <p id="doctorRecommendation"></p>
                <button onclick="closePopup()">Close</button>
            </div>
        </div>

        <script>
            function openPopup(recommendations, doctorRecommendation) {
                const popup = document.getElementById('recommendationsPopup');
                const recommendationsText = document.getElementById('recommendationsText');
                const doctorText = document.getElementById('doctorRecommendation');
                recommendationsText.innerText = recommendations;
                doctorText.innerText = doctorRecommendation;
                popup.style.display = 'flex';
            }

            function closePopup() {
                const popup = document.getElementById('recommendationsPopup');
                popup.style.display = 'none';
            }

            document.getElementById('generateReportBtn').addEventListener('click', function () {
                const stressLevel = document.getElementById('stress_level').value;
                const sleepHours = document.getElementById('sleep_hours').value;
                const exerciseHours = document.getElementById('exercise_hours').value;
                const socialInteraction = document.getElementById('social_interaction').value;
                const age = document.getElementById('age').value;

                if (!stressLevel || !sleepHours || !exerciseHours || !socialInteraction || !age) {
                    alert("Please fill in all the fields before generating the report.");
                    return;
                }

                fetch('/generate_report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        stress_level: stressLevel,
                        sleep_hours: sleepHours,
                        exercise_hours: exerciseHours,
                        social_interaction: socialInteraction,
                        age: age
                    })
                })
                .then(response => response.json())
                .then(data => {
                    openPopup(data.recommendations, data.doctor_recommendation);
                    // Add data to MySQL table
                    fetch('/save_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            stress_level: stressLevel,
                            sleep_hours: sleepHours,
                            exercise_hours: exerciseHours,
                            social_interaction: socialInteraction,
                            age: age
                        })
                    }).then(response => {
                        if (response.ok) {
                            console.log("Data saved successfully.");
                        } else {
                            console.error("Failed to save data.");
                        }
                    }).catch(error => {
                        console.error('Error:', error);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Something went wrong while generating the report.");
                });
            });
        </script>
    </body>
    </html>
    ''')

# Generate report route
@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    stress_level = int(data.get('stress_level', 0))
    sleep_hours = int(data.get('sleep_hours', 0))
    exercise_hours = int(data.get('exercise_hours', 0))
    social_interaction = int(data.get('social_interaction', 0))
    age = int(data.get('age', 0))

    # Calculate the stress index
    stress_index = calculate_stress(stress_level, sleep_hours, exercise_hours, social_interaction)

    # Get recommendations based on stress index
    recommendations = get_recommendations(stress_index)
    doctor_recommendation = recommend_doctor(stress_level)

    return jsonify({
        'stress_index': stress_index,
        'recommendations': recommendations,
        'doctor_recommendation': doctor_recommendation
    })

# Save data to the database
@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    stress_level = data.get('stress_level')
    sleep_hours = data.get('sleep_hours')
    exercise_hours = data.get('exercise_hours')
    social_interaction = data.get('social_interaction')
    age = data.get('age')

    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert data into the stress_data table
        cursor.execute('''
            INSERT INTO stress_data (stress_level, sleep_hours, exercise_hours, social_interaction, age)
            VALUES (%s, %s, %s, %s, %s)
        ''', (stress_level, sleep_hours, exercise_hours, social_interaction, age))

        # Commit the transaction
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Data saved successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'message': f'Error: {err}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
