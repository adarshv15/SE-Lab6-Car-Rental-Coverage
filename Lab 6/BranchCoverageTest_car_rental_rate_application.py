
import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics
)


# 1. Test invalid rental input
def test_invalid_rental_input():
    with pytest.raises(ValueError):
        process_rental_fleet("invalid", 10.0)


# 2. Test negative administration fee
def test_invalid_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -5.0)


# 3. Test empty rental batch
def test_empty_rental_batch():
    result = process_rental_fleet([], 10.0)

    assert result == {
        "total_revenue": 0.0,
        "status": "EMPTY_BATCH"
    }


# 4. Test unconfirmed rental
def test_unconfirmed_rental():
    rentals = [
        {"is_confirmed": False}
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


# 5. Test invalid rental days
def test_invalid_rental_days():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 0,
            "trip_segments": [100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


# 6. Test all vehicle types and driver age conditions
def test_all_vehicle_types_and_age_conditions():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "luxury",
            "driver_age": 24,
            "days": 2,
            "trip_segments": []
        },
        {
            "is_confirmed": True,
            "vehicle_type": "suv",
            "driver_age": 30,
            "days": 1,
            "trip_segments": []
        },
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 25,
            "days": 1,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"
    assert result["total_revenue"] == 480.0


# 7. Test negative mileage and normal mileage
def test_negative_and_normal_mileage():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-10, 100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"
    assert result["total_revenue"] == 70.0


# 8. Test long trip with driver below 21
def test_long_trip_young_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 19,
            "days": 2,
            "trip_segments": [350, 100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 380.0
    assert result["status"] == "STANDARD"


# 9. Test long trip with driver aged 21 or above
def test_long_trip_adult_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 22,
            "days": 1,
            "trip_segments": [350]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 210.0
    assert result["status"] == "STANDARD"


# 10. Test high risk audit
def test_high_risk_audit():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-1, -2, -3, -4, -5]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "HIGH_RISK_AUDIT"


# 11. Test empty telematics matrix
def test_empty_telematics_matrix():
    result = check_fleet_telematics([])

    assert result == "NO_DATA"


# 12. Test speeding streak reset
def test_speeding_streak_reset():
    telematics = [
        [110, 90, 120]
    ]

    result = check_fleet_telematics(telematics)

    assert result == "SAFE"


# 13. Test two consecutive speeding readings
def test_two_consecutive_speeding_readings():
    telematics = [
        [80, 110, 120]
    ]

    result = check_fleet_telematics(telematics)

    assert result == "GROUND_VEHICLE"


# 14. Test multiple vehicle logs
def test_multiple_vehicle_logs():
    telematics = [
        [],
        [110],
        [90, 80, 100]
    ]

    result = check_fleet_telematics(telematics)

    assert result == "SAFE"
