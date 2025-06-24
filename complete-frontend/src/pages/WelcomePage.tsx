import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function WelcomePage() {
  const { login } = useAuth();
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [role, setRole] = useState<"patient" | "clinician">("patient");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !dob) {
      setError("All fields are required.");
      return;
    }
    setError("");
    login({ name, dob, role });
    if (role === "patient") navigate("/chat");
    else navigate("/dashboard");
  };

  return (
    <main
      className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 px-4 py-8"
      aria-label="Welcome page main content"
    >
      <div className="w-full max-w-md">
        <header className="text-center mb-8" aria-label="App logo and title">
          <div className="flex justify-center mb-4">
            <div className="size-12 bg-blue-700 rounded-xl flex items-center justify-center">
              <svg
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="size-8 text-white"
              >
                <path
                  d="M36.7273 44C33.9891 44 31.6043 39.8386 30.3636 33.69C29.123 39.8386 26.7382 44 24 44C21.2618 44 18.877 39.8386 17.6364 33.69C16.3957 39.8386 14.0109 44 11.2727 44C7.25611 44 4 35.0457 4 24C4 12.9543 7.25611 4 11.2727 4C14.0109 4 16.3957 8.16144 17.6364 14.31C18.877 8.16144 21.2618 4 24 4C26.7382 4 29.123 8.16144 30.3636 14.31C31.6043 8.16144 33.9891 4 36.7273 4C40.7439 4 44 12.9543 44 24C44 35.0457 40.7439 44 36.7273 44Z"
                  fill="currentColor"
                ></path>
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to HealthAI
          </h1>
          <p className="text-gray-700 text-lg">
            Sign in to access your health portal
          </p>
        </header>
        <form
          className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100"
          onSubmit={handleSubmit}
          aria-label="Login form"
          noValidate
        >
          <div className="mb-6">
            <label
              htmlFor="name"
              className="block text-base font-semibold text-gray-700 mb-2"
            >
              Full Name
            </label>
            <input
              id="name"
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:border-transparent transition-all duration-200 text-lg"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
              required
              autoComplete="name"
              aria-describedby="name-error"
              aria-invalid={!!error && !name.trim()}
            />
          </div>
          <div className="mb-6">
            <label
              htmlFor="dob"
              className="block text-base font-semibold text-gray-700 mb-2"
            >
              Date of Birth
            </label>
            <input
              id="dob"
              type="date"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:border-transparent transition-all duration-200 text-lg"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              required
              autoComplete="bday"
              aria-describedby="dob-error"
              aria-invalid={!!error && !dob}
            />
          </div>
          <fieldset className="mb-8">
            <legend className="block text-base font-semibold text-gray-700 mb-3">
              I am a
            </legend>
            <div className="space-y-3">
              <label className="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 focus-within:bg-blue-50 focus-within:border-blue-700 transition-all duration-200">
                <input
                  type="radio"
                  name="role"
                  value="patient"
                  checked={role === "patient"}
                  onChange={() => setRole("patient")}
                  className="sr-only"
                  aria-describedby="patient-description"
                />
                <div
                  className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                    role === "patient"
                      ? "border-blue-700 bg-blue-700"
                      : "border-gray-300"
                  }`}
                >
                  {role === "patient" && (
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  )}
                </div>
                <div>
                  <div className="font-medium text-gray-900">Patient</div>
                  <div
                    id="patient-description"
                    className="text-sm text-gray-500"
                  >
                    Access your health chat and medical records
                  </div>
                </div>
              </label>
              <label className="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 focus-within:bg-blue-50 focus-within:border-blue-700 transition-all duration-200">
                <input
                  type="radio"
                  name="role"
                  value="clinician"
                  checked={role === "clinician"}
                  onChange={() => setRole("clinician")}
                  className="sr-only"
                  aria-describedby="clinician-description"
                />
                <div
                  className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                    role === "clinician"
                      ? "border-blue-700 bg-blue-700"
                      : "border-gray-300"
                  }`}
                >
                  {role === "clinician" && (
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  )}
                </div>
                <div>
                  <div className="font-medium text-gray-900">Clinician</div>
                  <div
                    id="clinician-description"
                    className="text-sm text-gray-500"
                  >
                    Manage patients and view medical data
                  </div>
                </div>
              </label>
            </div>
          </fieldset>
          {error && (
            <div className="mb-4 text-red-700 text-base" role="alert">
              {error}
            </div>
          )}
          <button
            type="submit"
            className="w-full bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold text-lg hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:ring-offset-2 transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!name.trim() || !dob}
            aria-describedby="submit-help"
          >
            Sign In
          </button>
          <p
            id="submit-help"
            className="mt-2 text-sm text-gray-500 text-center"
          >
            All fields are required to continue
          </p>
        </form>
        <footer className="mt-8 text-center" aria-label="App footer">
          <p className="text-sm text-gray-500">
            Secure and HIPAA compliant health portal
          </p>
        </footer>
      </div>
    </main>
  );
}
