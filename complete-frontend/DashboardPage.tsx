import React, { useState } from "react";
import PatientSearch from "../components/PatientSearch";
import PatientDashboard from "../components/PatientDashboard";
import { Patient } from "../api/patientApi";

export default function DashboardPage() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="p-4 bg-white shadow text-xl font-bold">
        Clinician Dashboard
      </header>
      <main className="flex-1 flex flex-col items-center justify-center">
        {!selectedPatient ? (
          <PatientSearch onSelect={setSelectedPatient} />
        ) : (
          <PatientDashboard patient={selectedPatient} />
        )}
      </main>
    </div>
  );
}
