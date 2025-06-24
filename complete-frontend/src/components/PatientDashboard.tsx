import React, { useState } from "react";
import { getPatientHistory } from "../api/patientApi";
import type { Patient } from "../api/patientApi";
import { sendNotification } from "../api/notificationApi";

export default function PatientDashboard({ patient }: { patient: Patient }) {
  const [history, setHistory] = useState(() => getPatientHistory(patient.id));
  const [notifSent, setNotifSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleNotify = async () => {
    setLoading(true);
    await sendNotification(patient.id);
    setNotifSent(true);
    setLoading(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow w-full max-w-2xl">
      <h2 className="text-xl font-bold mb-4">Patient Dashboard</h2>
      <div className="mb-4">
        <div>
          <span className="font-medium">Name:</span> {patient.name}
        </div>
        <div>
          <span className="font-medium">DOB:</span> {patient.dob}
        </div>
        <div>
          <span className="font-medium">ID:</span> {patient.id}
        </div>
      </div>
      <h3 className="text-lg font-semibold mb-2">Historical Data</h3>
      <ul className="mb-4">
        {history.map((item, idx) => (
          <li
            key={idx}
            className="mb-2 border-b pb-2 last:border-b-0 last:pb-0"
          >
            <div>
              <span className="font-medium">Date:</span> {item.date}
            </div>
            <div>
              <span className="font-medium">Summary:</span> {item.summary}
            </div>
          </li>
        ))}
      </ul>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        onClick={handleNotify}
        disabled={loading || notifSent}
        aria-busy={loading}
      >
        {notifSent
          ? "Notification Sent"
          : loading
          ? "Sending..."
          : "Send Notification"}
      </button>
    </div>
  );
}
