export async function sendNotification(patientId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  // No-op for synthetic
}
