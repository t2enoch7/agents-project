import React, { useState } from "react";
import { searchPatient, Patient } from "../api/patientApi";

export default function PatientSearch({
  onSelect,
}: {
  onSelect: (p: Patient) => void;
}) {
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const patient = await searchPatient(name, dob);
      if (patient) onSelect(patient);
      else setError("Patient not found.");
    } catch {
      setError("Error searching for patient.");
    }
    setLoading(false);
  };

  return (
    <form
      className="bg-white p-6 rounded-lg shadow w-full max-w-md"
      onSubmit={handleSubmit}
      aria-label="Patient search form"
    >
      <h2 className="text-xl font-bold mb-4">Search Patient</h2>
      <label className="block mb-2 font-medium" htmlFor="name">
        Name
      </label>
      <input
        id="name"
        className="form-input w-full mb-4"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <label className="block mb-2 font-medium" htmlFor="dob">
        Date of Birth
      </label>
      <input
        id="dob"
        type="date"
        className="form-input w-full mb-4"
        value={dob}
        onChange={(e) => setDob(e.target.value)}
        required
      />
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        disabled={loading}
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
