import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function WelcomePage() {
  const { login } = useAuth();
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [role, setRole] = useState<"patient" | "clinician">("patient");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login({ name, dob, role });
    if (role === "patient") navigate("/chat");
    else navigate("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form
        className="bg-white p-8 rounded-lg shadow-md w-full max-w-md"
        onSubmit={handleSubmit}
        aria-label="Login form"
      >
        <h1 className="text-2xl font-bold mb-6 text-center">
          Welcome to HealthAI
        </h1>
        <label className="block mb-2 font-medium" htmlFor="name">
          Name
        </label>
        <input
          id="name"
          className="form-input w-full mb-4"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          autoComplete="name"
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
          autoComplete="bday"
        />
        <label className="block mb-2 font-medium">Role</label>
        <div className="flex gap-4 mb-6">
          <label>
            <input
              type="radio"
              name="role"
              value="patient"
              checked={role === "patient"}
              onChange={() => setRole("patient")}
              className="mr-2"
            />
            Patient
          </label>
          <label>
            <input
              type="radio"
              name="role"
              value="clinician"
              checked={role === "clinician"}
              onChange={() => setRole("clinician")}
              className="mr-2"
            />
            Clinician
          </label>
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          Login
        </button>
      </form>
    </div>
  );
}
