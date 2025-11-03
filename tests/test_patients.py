"""
Patient CRUD Tests
Test-Driven Development: These tests MUST FAIL initially
Then we implement code to make them PASS
"""
import pytest


class TestPatientCreate:
    """Test patient creation endpoint"""

    def test_create_patient_success(self, client):
        """Test creating a new patient with valid data"""
        response = client.post(
            "/api/patients",
            json={"name": "John Doe", "notes": "Initial consultation"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["notes"] == "Initial consultation"
        assert "id" in data
        assert "date_created" in data
        assert "date_last_updated" in data

    def test_create_patient_duplicate_name(self, client):
        """Test that duplicate patient names are rejected"""
        # Create first patient
        client.post(
            "/api/patients",
            json={"name": "John Doe"}
        )

        # Try to create another with same name
        response = client.post(
            "/api/patients",
            json={"name": "John Doe"}
        )
        assert response.status_code == 409  # Conflict

    def test_create_patient_missing_name(self, client):
        """Test that patient without name is rejected"""
        response = client.post(
            "/api/patients",
            json={"notes": "No name provided"}
        )
        assert response.status_code == 422  # Validation error

    def test_create_patient_empty_name(self, client):
        """Test that empty name is rejected"""
        response = client.post(
            "/api/patients",
            json={"name": ""}
        )
        assert response.status_code == 422


class TestPatientRead:
    """Test patient retrieval endpoints"""

    def test_get_all_patients_empty(self, client):
        """Test getting all patients when none exist"""
        response = client.get("/api/patients")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_patients_multiple(self, client):
        """Test getting multiple patients"""
        # Create patients
        client.post("/api/patients", json={"name": "Patient A"})
        client.post("/api/patients", json={"name": "Patient B"})

        response = client.get("/api/patients")
        assert response.status_code == 200
        patients = response.json()
        assert len(patients) == 2
        assert patients[0]["name"] == "Patient A"
        assert patients[1]["name"] == "Patient B"

    def test_get_patient_by_id_success(self, client):
        """Test getting a patient by ID"""
        # Create patient
        create_response = client.post(
            "/api/patients",
            json={"name": "John Doe", "notes": "Test patient"}
        )
        patient_id = create_response.json()["id"]

        # Get patient by ID
        response = client.get(f"/api/patients/{patient_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == patient_id
        assert data["name"] == "John Doe"
        assert data["notes"] == "Test patient"

    def test_get_patient_by_id_not_found(self, client):
        """Test getting a non-existent patient"""
        response = client.get("/api/patients/999")
        assert response.status_code == 404


class TestPatientUpdate:
    """Test patient update endpoints"""

    def test_update_patient_success(self, client):
        """Test updating a patient"""
        # Create patient
        create_response = client.post(
            "/api/patients",
            json={"name": "John Doe", "notes": "Initial"}
        )
        patient_id = create_response.json()["id"]

        # Update patient
        response = client.put(
            f"/api/patients/{patient_id}",
            json={"name": "John Doe", "notes": "Updated notes"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes"
        assert data["id"] == patient_id

    def test_update_patient_not_found(self, client):
        """Test updating non-existent patient"""
        response = client.put(
            "/api/patients/999",
            json={"name": "John Doe"}
        )
        assert response.status_code == 404

    def test_update_patient_invalid_data(self, client):
        """Test updating with invalid data"""
        # Create patient
        create_response = client.post(
            "/api/patients",
            json={"name": "John Doe"}
        )
        patient_id = create_response.json()["id"]

        # Try to update with empty name
        response = client.put(
            f"/api/patients/{patient_id}",
            json={"name": ""}
        )
        assert response.status_code == 422


class TestPatientDelete:
    """Test patient deletion endpoints"""

    def test_delete_patient_success(self, client):
        """Test deleting a patient"""
        # Create patient
        create_response = client.post(
            "/api/patients",
            json={"name": "John Doe"}
        )
        patient_id = create_response.json()["id"]

        # Delete patient
        response = client.delete(f"/api/patients/{patient_id}")
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/api/patients/{patient_id}")
        assert get_response.status_code == 404

    def test_delete_patient_not_found(self, client):
        """Test deleting non-existent patient"""
        response = client.delete("/api/patients/999")
        assert response.status_code == 404
