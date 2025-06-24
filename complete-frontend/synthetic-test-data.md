# Synthetic Test Data & Instructions for HealthAI App

This file provides synthetic data and step-by-step instructions to test all user flows and features in the HealthAI app.

---

## 1. **Test Users**

### **Patients**

| Name     | DOB        | Role    |
| -------- | ---------- | ------- |
| Sarah    | 1990-01-01 | patient |
| John Doe | 1985-05-12 | patient |

### **Clinician**

| Name     | DOB      | Role      |
| -------- | -------- | --------- |
| Any name | Any date | clinician |

---

## 2. **Patient Historical Data**

For any patient:

- 2024-06-01: Routine checkup. All vitals normal.
- 2024-05-15: Reported fatigue. Advised rest and hydration.
- 2024-04-10: Annual physical. No issues found.

---

## 3. **Sample Questionnaire**

After the patient answers "How are you today?", the following questionnaire is shown:

1. **How would you rate your overall energy level today?**
   - Excellent, Good, Fair, Poor
2. **Have you experienced any pain or discomfort recently?**
   - No, Mild, Moderate, Severe
3. **How many hours did you sleep last night?**
   - (Short text answer)
4. **Are you currently taking any medications? If yes, please list them.**
   - (Short text answer)
5. **Is there anything else you would like your care team to know today?**
   - (Short text answer)

---

## 4. **Testing Patient Flow**

1. **Login as Sarah (patient):**
   - Name: `Sarah`
   - DOB: `1990-01-01`
   - Role: `patient`
2. **Chat page:**
   - Respond to "How are you today?"
   - Fill out the questionnaire
   - View the summary page
3. **Repeat for John Doe (patient)**

---

## 5. **Testing Clinician Flow**

1. **Login as clinician:**
   - Name: any (e.g., `Dr. Smith`)
   - DOB: any (e.g., `1980-01-01`)
   - Role: `clinician`
2. **Dashboard:**
   - Search for `Sarah` with DOB `1990-01-01`
   - View patient dashboard, history, and send notification
   - Repeat for `John Doe`

---

## 6. **Synthetic Chat Bot Responses**

- The chat bot gives a generic synthetic response:
  `"This is a synthetic response. (Replace with real API call.)"`

---

## 7. **Notification**

- Sending a notification is simulated and always succeeds.

---

## 8. **Extending for Backend/Custom Logic**

- To allow the questionnaire to be sent from the backend, update `getQuestionnaire()` in `src/api/questionnaireApi.ts` to fetch from an API endpoint instead of returning static data.
- To customize questions for different patient types, add logic in `getQuestionnaire()` to return different sets of questions based on patient info.

---

## 9. **How to Use This Data**

- Use the above users and flows to test all features of the app.
- You can add more synthetic users or questions as needed for further testing.
