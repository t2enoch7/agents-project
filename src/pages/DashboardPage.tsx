import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { apiService } from "../services/api";
import { DashboardMetrics, Agent } from "../types";

const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsResponse, agentsResponse] = await Promise.all([
          apiService.getDashboardMetrics(),
          apiService.getAgents(),
        ]);

        if (metricsResponse.success && metricsResponse.data) {
          setMetrics(metricsResponse.data);
        }

        if (agentsResponse.success && agentsResponse.data) {
          setAgents(agentsResponse.data);
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Mock data for charts
  const completionRateData = [
    { day: "Day 1", rate: 85 },
    { day: "Day 5", rate: 88 },
    { day: "Day 10", rate: 92 },
    { day: "Day 15", rate: 89 },
    { day: "Day 20", rate: 94 },
    { day: "Day 25", rate: 96 },
    { day: "Day 30", rate: 95 },
  ];

  const alertAccuracyData = [
    { category: "Category A", accuracy: 90 },
    { category: "Category B", accuracy: 70 },
    { category: "Category C", accuracy: 90 },
  ];

  const userSatisfactionData = [
    { feature: "Feature 1", satisfaction: 100 },
    { feature: "Feature 2", satisfaction: 100 },
    { feature: "Feature 3", satisfaction: 20 },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="px-40 flex flex-1 justify-center py-5">
      <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
        <div className="dashboard-header flex flex-wrap justify-between gap-3 p-4">
          <div className="dashboard-header-title min-w-72 flex flex-col gap-3">
            <p className="text-gray-900 text-2xl font-bold m-0">Dashboard</p>
            <p className="text-gray-500 text-sm m-0">
              Monitor your health information metrics
            </p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="dashboard-metrics flex flex-wrap gap-4 p-4">
          <div className="metric-card min-w-[158px] flex-1 flex flex-col gap-2 rounded-xl p-6 bg-gray-100">
            <p className="metric-title text-gray-900 text-base font-medium m-0">
              Completion Rate
            </p>
            <p className="metric-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.completionRate}%
            </p>
            <p className="metric-diff text-green-500 text-base font-medium m-0">
              +5%
            </p>
          </div>
          <div className="metric-card min-w-[158px] flex-1 flex flex-col gap-2 rounded-xl p-6 bg-gray-100">
            <p className="metric-title text-gray-900 text-base font-medium m-0">
              Alert Accuracy
            </p>
            <p className="metric-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.alertAccuracy}%
            </p>
            <p className="metric-diff text-green-500 text-base font-medium m-0">
              +3%
            </p>
          </div>
          <div className="metric-card min-w-[158px] flex-1 flex flex-col gap-2 rounded-xl p-6 bg-gray-100">
            <p className="metric-title text-gray-900 text-base font-medium m-0">
              User Satisfaction
            </p>
            <p className="metric-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.userSatisfaction}%
            </p>
            <p className="metric-diff text-green-500 text-base font-medium m-0">
              +2%
            </p>
          </div>
        </div>

        {/* Agent Status */}
        <h2 className="section-title text-gray-900 text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 mt-8 mb-0">
          Multi-Agent System Status
        </h2>
        <div className="flex flex-wrap gap-4 p-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="min-w-[200px] flex-1 flex flex-col gap-2 rounded-xl p-4 border border-gray-200 bg-white"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-gray-900 text-base font-medium m-0">
                  {agent.name}
                </h3>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    agent.status === "active"
                      ? "bg-green-100 text-green-800"
                      : agent.status === "inactive"
                      ? "bg-gray-100 text-gray-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {agent.status}
                </span>
              </div>
              <p className="text-gray-600 text-sm m-0">{agent.currentTask}</p>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.slice(0, 2).map((capability, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                  >
                    {capability}
                  </span>
                ))}
                {agent.capabilities.length > 2 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                    +{agent.capabilities.length - 2}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Detailed Metrics */}
        <h2 className="section-title text-gray-900 text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 mt-8 mb-0">
          Health Information Metrics
        </h2>
        <div className="metrics-details flex flex-wrap gap-4 p-6">
          {/* Completion Rate Chart */}
          <div className="details-card min-w-72 flex-1 flex flex-col gap-2 rounded-xl border border-gray-200 p-6 bg-white">
            <p className="details-title text-gray-900 text-base font-medium m-0">
              Completion Rate Over Time
            </p>
            <p className="details-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.completionRate}%
            </p>
            <div className="details-diff-row flex gap-1 items-center">
              <span className="details-diff-label text-gray-500 text-base font-normal">
                Last 30 Days
              </span>
              <span className="details-diff-value text-green-500 text-base font-medium">
                +5%
              </span>
            </div>
            <div className="details-graph min-h-[180px] flex flex-col gap-8 py-4">
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={completionRateData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="day" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="#3d98f4"
                    strokeWidth={3}
                    dot={{ fill: "#3d98f4" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Alert Accuracy Chart */}
          <div className="details-card min-w-72 flex-1 flex flex-col gap-2 rounded-xl border border-gray-200 p-6 bg-white">
            <p className="details-title text-gray-900 text-base font-medium m-0">
              Alert Accuracy by Category
            </p>
            <p className="details-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.alertAccuracy}%
            </p>
            <div className="details-diff-row flex gap-1 items-center">
              <span className="details-diff-label text-gray-500 text-base font-normal">
                Last 30 Days
              </span>
              <span className="details-diff-value text-green-500 text-base font-medium">
                +3%
              </span>
            </div>
            <div className="min-h-[180px] py-4">
              <ResponsiveContainer width="100%" height={120}>
                <BarChart data={alertAccuracyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="category" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="accuracy" fill="#3d98f4" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* User Satisfaction Chart */}
          <div className="details-card min-w-72 flex-1 flex flex-col gap-2 rounded-xl border border-gray-200 p-6 bg-white">
            <p className="details-title text-gray-900 text-base font-medium m-0">
              User Satisfaction by Feature
            </p>
            <p className="details-value text-gray-900 text-2xl font-bold leading-tight m-0">
              {metrics?.userSatisfaction}%
            </p>
            <div className="details-diff-row flex gap-1 items-center">
              <span className="details-diff-label text-gray-500 text-base font-normal">
                Last 30 Days
              </span>
              <span className="details-diff-value text-green-500 text-base font-medium">
                +2%
              </span>
            </div>
            <div className="feature-graph grid gap-6 py-4 min-h-[180px]">
              {userSatisfactionData.map((item, index) => (
                <div
                  key={index}
                  className="grid grid-cols-[auto_1fr] gap-4 items-center"
                >
                  <p className="feature-label text-gray-500 text-sm font-bold tracking-[0.015em] m-0">
                    {item.feature}
                  </p>
                  <div className="relative h-4 bg-gray-100 rounded">
                    <div
                      className="h-full bg-gray-300 border-r-2 border-gray-500 rounded"
                      style={{ width: `${item.satisfaction}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Additional Stats */}
        <div className="flex flex-wrap gap-4 p-4 mt-4">
          <div className="min-w-[200px] flex-1 flex flex-col gap-2 rounded-xl p-4 border border-gray-200 bg-white">
            <p className="text-gray-500 text-sm m-0">Active Patients</p>
            <p className="text-gray-900 text-2xl font-bold m-0">
              {metrics?.activePatients?.toLocaleString()}
            </p>
          </div>
          <div className="min-w-[200px] flex-1 flex flex-col gap-2 rounded-xl p-4 border border-gray-200 bg-white">
            <p className="text-gray-500 text-sm m-0">Total Conversations</p>
            <p className="text-gray-900 text-2xl font-bold m-0">
              {metrics?.totalConversations?.toLocaleString()}
            </p>
          </div>
          <div className="min-w-[200px] flex-1 flex flex-col gap-2 rounded-xl p-4 border border-gray-200 bg-white">
            <p className="text-gray-500 text-sm m-0">Avg Response Time</p>
            <p className="text-gray-900 text-2xl font-bold m-0">
              {metrics?.averageResponseTime}s
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
