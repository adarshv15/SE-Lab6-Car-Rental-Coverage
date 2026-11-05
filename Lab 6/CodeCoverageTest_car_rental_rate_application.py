
import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics
)


# 1. Test invalid rental list
def test_invalid_rental_list():
    with pytest.raises(ValueError):
        process_rental_fleet("invalid", 10.0)


# 2. Test negative administration fee
def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -5.0)


# 3. Test unconfirmed rental
def test_unconfirmed_rental():
    rentals = [
        {"is_confirmed": False}
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "EMPTY_BATCH"


# 4. Test invalid rental days
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

    assert result["total_revenue"] == 0.0
    assert result["status"] == "EMPTY_BATCH"


# 5. Test vehicle types, mileage and young driver charges
def test_vehicle_types_and_mileage():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "luxury",
            "driver_age": 24,
            "days": 2,
            "trip_segments": [100, 350]
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
            "vehicle_type": "other",
            "driver_age": 20,
            "days": 1,
            "trip_segments": [350, 100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 910.0
    assert result["status"] == "STANDARD"


# 6. Test negative mileage
def test_negative_mileage():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-10, 50]
        }
    ]

    result = process_rental_fleet(rentals, 5.0)

    assert result["total_revenue"] == 55.0
    assert result["status"] == "STANDARD"


# 7. Test high risk audit
def test_high_risk_audit():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-1, -1, -1, -1, -1]
        }
    ]

    result = process_rental_fleet(rentals, 5.0)

    assert result["status"] == "HIGH_RISK_AUDIT"


# 8. Test empty telematics data
def test_empty_telematics():
    result = check_fleet_telematics([])

    assert result == "NO_DATA"


# 9. Test consecutive speeding
def test_consecutive_speeding():
    telematics = [
        [80, 110, 120]
    ]

    result = check_fleet_telematics(telematics)

    assert result == "GROUND_VEHICLE"


# 10. Test safe driving and speeding streak reset
def test_safe_driving():
    telematics = [
        [110, 90, 110]
    ]

    result = check_fleet_telematics(telematics)

    assert result == "SAFE"
