"""
AQI Calculator for Indoor Air Quality Monitor Project

This module calculates Indoor Air Quality Index values based on sensor readings.
"""

def calculate_gas_aqi(ppm):
    """
    Calculate AQI based on gas sensor PPM (MQ135 - primarily sensitive to CO2, ammonia, and VOCs)
    
    Args:
        ppm (float): Gas concentration in PPM
    
    Returns:
        dict: AQI value, category, and color
    """
    # Define breakpoints for gas AQI (MQ135 sensor approximation)
    breakpoints = [
        (400, 500, 0, 50, "Good", "#00e400"),              # Good
        (500, 700, 51, 100, "Moderate", "#F7D154"),        # Moderate (deeper yellow)
        (700, 800, 101, 150, "Unhealthy for Sensitive Groups", "#ff7e00"),  # Unhealthy for sensitive
        (800, 900, 151, 200, "Unhealthy", "#ff0000"),      # Unhealthy
        (900, 1000, 201, 300, "Very Unhealthy", "#99004c") # Very Unhealthy
    ]
    
    # Find appropriate breakpoint
    for c_low, c_high, i_low, i_high, category, color in breakpoints:
        if c_low <= ppm <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (ppm - c_low) + i_low
            return {
                "value": round(aqi),
                "category": category,
                "color": color
            }
    
    # If beyond highest breakpoint, it's hazardous
    if ppm > 1000:
        return {
            "value": 301,
            "category": "Hazardous",
            "color": "#7e0023"
        }
    
    # If below lowest breakpoint, it's good
    return {
        "value": 0,
        "category": "Good", 
        "color": "#00e400"
    }

def calculate_dust_aqi(dust_density):
    """
    Calculate AQI based on dust density (approximate PM2.5 conversion)
    
    Args:
        dust_density (float): Dust density in µg/m³
    
    Returns:
        dict: AQI value, category, and color
    """
    # If density is 0, this typically means either clean air or sensor error
    if dust_density <= 0:
        return {
            "value": 0,
            "category": "Undetermined",
            "color": "#cccccc"  # Gray
        }
    
    # Define breakpoints for PM2.5 AQI
    breakpoints = [
        (0, 12, 0, 50, "Good", "#00e400"),
        (12.1, 35.4, 51, 100, "Moderate", "#F7D154"),  # Moderate (deeper yellow)
        (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups", "#ff7e00"),
        (55.5, 150.4, 151, 200, "Unhealthy", "#ff0000"),
        (150.5, 250.4, 201, 300, "Very Unhealthy", "#99004c"),
        (250.5, 500.4, 301, 500, "Hazardous", "#7e0023")
    ]
    
    # Find appropriate breakpoint
    for c_low, c_high, i_low, i_high, category, color in breakpoints:
        if c_low <= dust_density <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (dust_density - c_low) + i_low
            return {
                "value": round(aqi),
                "category": category,
                "color": color
            }
    
    # Beyond highest breakpoint, it's hazardous
    if dust_density > 500.4:
        return {
            "value": 500,
            "category": "Hazardous",
            "color": "#7e0023"
        }
    
    # This should not happen, but just in case
    return {
        "value": 0,
        "category": "Undetermined",
        "color": "#cccccc"
    }

def get_humidity_health_index(humidity):
    """
    Get health index based on humidity levels
    
    Args:
        humidity (float): Relative humidity percentage
    
    Returns:
        dict: Index value, category, and color
    """
    if humidity < 30:
        return {
            "value": 150,
            "category": "Too Dry",
            "color": "#ff7e00",
            "message": "Low humidity can cause respiratory issues and skin dryness"
        }
    elif 30 <= humidity <= 50:
        return {
            "value": 25,
            "category": "Optimal",
            "color": "#00e400",
            "message": "Ideal humidity levels for health and comfort"
        }
    elif 50 < humidity <= 60:
        return {
            "value": 75,
            "category": "Acceptable",
            "color": "#F7D154",  # Deeper yellow
            "message": "Acceptable humidity, monitor for mold in enclosed spaces"
        }
    else:  # humidity > 60
        return {
            "value": 175,
            "category": "Too Humid",
            "color": "#ff0000",
            "message": "High humidity promotes mold growth and dust mites"
        }

def calculate_overall_aqi(data):
    """
    Calculate overall Indoor Air Quality Index from sensor data
    
    Args:
        data (dict): Sensor readings including gas_ppm, dust_density, etc.
    
    Returns:
        dict: Overall AQI information and individual component details
    """
    gas_ppm = data.get('gas_ppm')
    dust_density = data.get('dust_density')
    humidity = data.get('humidity')
    temperature = data.get('temperature')
    
    # Calculate individual indices
    gas_index = calculate_gas_aqi(gas_ppm) if gas_ppm is not None else {"value": 0, "category": "Unknown", "color": "#cccccc"}
    dust_index = calculate_dust_aqi(dust_density) if dust_density is not None else {"value": 0, "category": "Unknown", "color": "#cccccc"}
    humidity_index = get_humidity_health_index(humidity) if humidity is not None else {"value": 0, "category": "Unknown", "color": "#cccccc"}
    
    # Overall AQI is the highest of the individual indices
    indices = [gas_index, dust_index]
    max_index = max(indices, key=lambda x: x["value"])
    
    # Add temperature comfort level
    temp_comfort = get_temperature_comfort(temperature) if temperature is not None else {"category": "Unknown", "message": "No data"}
    
    return {
        "overall": {
            "value": max_index["value"],
            "category": max_index["category"],
            "color": max_index["color"],
        },
        "components": {
            "gas": gas_index,
            "dust": dust_index,
            "humidity": humidity_index,
            "temperature": temp_comfort
        },
        "recommendations": get_recommendations(max_index["value"], humidity_index["value"])
    }

def get_temperature_comfort(temperature):
    """
    Get comfort level based on temperature
    
    Args:
        temperature (float): Temperature in degrees Celsius
    
    Returns:
        dict: Comfort category and message
    """
    if temperature < 18:
        return {
            "category": "Too Cold",
            "message": "Below comfortable indoor temperature range"
        }
    elif 18 <= temperature <= 24:
        return {
            "category": "Comfortable",
            "message": "Ideal indoor temperature range"
        }
    else:  # temperature > 24
        return {
            "category": "Too Warm",
            "message": "Above comfortable indoor temperature range"
        }

def get_recommendations(aqi_value, humidity_index):
    """
    Get recommendations based on AQI value
    
    Args:
        aqi_value (int): The calculated AQI value
        humidity_index (int): The humidity health index value
    
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    # AQI-based recommendations
    if aqi_value <= 50:
        recommendations.append("Air quality is good. No action needed.")
    elif aqi_value <= 100:
        recommendations.append("Moderate air quality. Consider improving ventilation.")
    elif aqi_value <= 150:
        recommendations.append("Air quality may be unhealthy for sensitive individuals.")
        recommendations.append("Open windows to increase air circulation.")
        recommendations.append("Consider using an air purifier.")
    elif aqi_value <= 200:
        recommendations.append("Unhealthy air quality. Increase ventilation immediately.")
        recommendations.append("Use air purifiers if available.")
        recommendations.append("Avoid activities that generate more pollutants.")
    else:  # aqi_value > 200
        recommendations.append("Very unhealthy air. Use air filtration immediately.")
        recommendations.append("Minimize time in affected areas.")
        recommendations.append("Identify and address pollution sources.")
    
    # Humidity-based recommendations
    if humidity_index > 150:
        recommendations.append("Humidity is too high. Use a dehumidifier.")
    elif humidity_index < 50:
        recommendations.append("Humidity is too low. Consider using a humidifier.")
    
    return recommendations
