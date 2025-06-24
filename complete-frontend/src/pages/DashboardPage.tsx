import React, { useState } from "react";
import PatientSearch from "../components/PatientSearch";
import PatientDashboard from "../components/PatientDashboard";
import type { Patient } from "../api/patientApi";
import Header from "../components/Header";

export default function DashboardPage() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main
        className="flex-1 flex flex-col items-center justify-center"
        aria-label="Clinician dashboard main content"
      >
        <section
          className="w-full max-w-2xl p-4"
          aria-label="Patient search section"
        >
          {!selectedPatient ? (
            <PatientSearch onSelect={setSelectedPatient} />
          ) : (
            <PatientDashboard patient={selectedPatient} />
          )}
        </section>
      </main>
    </div>
  );
}
