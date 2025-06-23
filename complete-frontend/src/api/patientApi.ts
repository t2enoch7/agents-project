export type Patient = {
  id: string;
  name: string;
  dob: string;
};

const patients: Patient[] = [
  { id: "1", name: "Sarah", dob: "1990-01-01" },
  { id: "2", name: "John Doe", dob: "1985-05-12" },
];

export async function searchPatient(name: string, dob: string): Promise<Patient | null> {
  await new Promise((r) => setTimeout(r, 800));
  return patients.find(p => p.name.toLowerCase() === name.toLowerCase() && p.dob === dob) || null;
}

export function getPatientHistory(patientId: string): { date: string; summary: string }[] {
  // Synthetic data
  return [
    { date: "2024-06-01", summary: "Routine checkup. All vitals normal." },
    { date: "2024-05-15", summary: "Reported fatigue. Advised rest and hydration." },
    { date: "2024-04-10", summary: "Annual physical. No issues found." },
  ];
}
