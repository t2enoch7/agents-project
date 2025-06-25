import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import random

from .models import Patient, TrendAnalysis, TrendAlert, AlertSeverity
from .database import DatabaseManager

load_dotenv()

logger = logging.getLogger(__name__)

class TrendMonitoringAgent:
    def __init__(self):
        """Initialize the Trend Monitoring Agent with mock responses for testing"""
        self.db_manager = DatabaseManager()

        # Agent capabilities and personality
        self.system_prompt = """
        You are a clinical trend monitoring agent designed to analyze Patient Reported Outcomes (PROs) and detect concerning patterns. Your role is to:

        1. **Pattern Recognition**: Identify trends, anomalies, and patterns in patient data
        2. **Risk Assessment**: Evaluate patient risk levels based on PRO trends
        3. **Clinical Insights**: Generate actionable insights for healthcare providers
        4. **Alert Generation**: Create appropriate alerts for concerning patterns
        5. **Predictive Analysis**: Identify potential future issues based on current trends
        6. **Data Interpretation**: Convert raw PRO data into meaningful clinical information

        Key Guidelines:
        - Focus on clinically significant patterns
        - Consider patient context and condition
        - Generate actionable recommendations
        - Maintain appropriate alert thresholds
        - Consider temporal patterns and seasonality
        - Account for patient engagement levels
        """

        # Risk thresholds for different conditions
        self.risk_thresholds = {
            "diabetes": {
                "blood_sugar_high": 180,  # mg/dL
                "blood_sugar_low": 70,    # mg/dL
                "symptom_frequency": 0.7,  # 70% of responses
                "medication_adherence": 0.8  # 80% adherence
            },
            "hypertension": {
                "systolic_high": 140,     # mmHg
                "diastolic_high": 90,     # mmHg
                "stress_level": 7,        # Scale 1-10
                "symptom_frequency": 0.6
            },
            "depression": {
                "mood_low": 4,            # Scale 1-10
                "energy_low": 3,          # Scale 1-10
                "sleep_issues": 0.5,      # 50% of responses
                "symptom_frequency": 0.6
            },
            "chronic_pain": {
                "pain_level_high": 7,     # Scale 1-10
                "impact_high": 8,         # Scale 1-10
                "frequency_high": 0.7     # 70% of responses
            }
        }

        # Alert types and their severity mappings
        self.alert_types = {
            "trend_deterioration": AlertSeverity.MEDIUM,
            "sudden_change": AlertSeverity.HIGH,
            "risk_threshold_exceeded": AlertSeverity.HIGH,
            "engagement_decline": AlertSeverity.LOW,
            "medication_non_adherence": AlertSeverity.MEDIUM,
            "symptom_increase": AlertSeverity.MEDIUM,
            "critical_value": AlertSeverity.CRITICAL
        }

    async def analyze_patient_trends(self, patient: Dict[str, Any], pro_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patient PRO data for trends and patterns"""
        try:
            if not pro_data:
                return {
                    "patient_id": patient.get("id"),
                    "analysis_date": datetime.now(),
                    "trends": [],
                    "alerts": [],
                    "recommendations": ["Insufficient data for trend analysis"],
                    "risk_score": None,
                    "data_points": 0
                }

            # Simple analysis based on condition and data
            condition = patient.get("condition", "").lower()

            # Generate mock trends based on condition
            trends = await self._generate_mock_trends(condition, pro_data)

            # Generate mock anomalies
            anomalies = await self._generate_mock_anomalies(pro_data)

            # Assess risk
            risk_assessment = await self._assess_risk(condition, pro_data)

            # Generate alerts
            alerts = await self._generate_alerts(trends, anomalies, risk_assessment, patient)

            # Generate recommendations
            recommendations = await self._generate_recommendations(condition, risk_assessment)

            # Calculate overall risk score
            risk_score = self._calculate_risk_score(risk_assessment)

            # Store alerts in database
            for alert in alerts:
                await self.db_manager.create_trend_alert(
                    patient_id=patient.get("id"),
                    alert_type=alert["type"],
                    severity=alert["severity"],
                    description=alert["description"]
                )

            return {
                "patient_id": patient.get("id"),
                "analysis_date": datetime.now(),
                "trends": trends,
                "anomalies": anomalies,
                "risk_assessment": risk_assessment,
                "alerts": alerts,
                "recommendations": recommendations,
                "risk_score": risk_score,
                "data_points": len(pro_data)
            }

        except Exception as e:
            logger.error(f"Error analyzing patient trends: {e}")
            return {
                "patient_id": patient.get("id"),
                "analysis_date": datetime.now(),
                "trends": [],
                "alerts": [],
                "recommendations": ["Error in trend analysis"],
                "risk_score": None,
                "data_points": 0
            }

    async def _generate_mock_trends(self, condition: str, pro_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mock trends based on condition"""
        try:
            trends = []

            if condition == "diabetes":
                trends.append({
                    "question_id": "blood_sugar",
                    "trend_direction": "increasing",
                    "rate_of_change": 15.5,
                    "mean_value": 165.0,
                    "std_value": 25.0,
                    "min_value": 140.0,
                    "max_value": 200.0,
                    "data_points": len(pro_data),
                    "clinical_significance": {
                        "significance": "high",
                        "clinical_impact": "Blood sugar levels are trending upward",
                        "urgency": "medium",
                        "recommendation": "Consider medication adjustment"
                    },
                    "slope": 0.8
                })
            elif condition == "hypertension":
                trends.append({
                    "question_id": "blood_pressure",
                    "trend_direction": "stable",
                    "rate_of_change": 2.0,
                    "mean_value": 135.0,
                    "std_value": 10.0,
                    "min_value": 125.0,
                    "max_value": 145.0,
                    "data_points": len(pro_data),
                    "clinical_significance": {
                        "significance": "medium",
                        "clinical_impact": "Blood pressure is well controlled",
                        "urgency": "low",
                        "recommendation": "Continue current management"
                    },
                    "slope": 0.1
                })
            elif condition == "depression":
                trends.append({
                    "question_id": "mood",
                    "trend_direction": "decreasing",
                    "rate_of_change": -1.5,
                    "mean_value": 4.5,
                    "std_value": 1.5,
                    "min_value": 3.0,
                    "max_value": 6.0,
                    "data_points": len(pro_data),
                    "clinical_significance": {
                        "significance": "high",
                        "clinical_impact": "Mood is declining",
                        "urgency": "high",
                        "recommendation": "Schedule follow-up appointment"
                    },
                    "slope": -0.3
                })

            return trends

        except Exception as e:
            logger.error(f"Error generating mock trends: {e}")
            return []

    async def _generate_mock_anomalies(self, pro_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mock anomalies"""
        try:
            anomalies = []

            # Generate a few mock anomalies
            if len(pro_data) > 0:
                anomalies.append({
                    "question_id": "blood_sugar",
                    "timestamp": datetime.now(),
                    "value": "220",
                    "z_score": 2.5,
                    "severity": "medium"
                })

            return anomalies

        except Exception as e:
            logger.error(f"Error generating mock anomalies: {e}")
            return []

    async def _assess_risk(self, condition: str, pro_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess patient risk based on PRO data"""
        try:
            risk_factors = {}
            overall_risk = "low"

            # Simple risk assessment based on condition
            if condition == "diabetes":
                # Check for high blood sugar mentions
                high_sugar_count = sum(1 for data in pro_data if "blood_sugar" in data.get("question_id", "").lower())
                if high_sugar_count > 0:
                    risk_factors["blood_sugar"] = "high"
                    overall_risk = "medium"

            elif condition == "hypertension":
                risk_factors["blood_pressure"] = "medium"
                overall_risk = "medium"

            elif condition == "depression":
                risk_factors["mood"] = "high"
                overall_risk = "high"

            return {
                "overall_risk": overall_risk,
                "risk_factors": risk_factors,
                "condition": condition,
                "assessment_date": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return {
                "overall_risk": "unknown",
                "risk_factors": {},
                "condition": condition,
                "assessment_date": datetime.now()
            }

    async def _generate_alerts(self, trends: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], risk_assessment: Dict[str, Any], patient: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on trends, anomalies, and risk assessment"""
        try:
            alerts = []

            # Alert for high overall risk
            if risk_assessment.get("overall_risk") in ["high", "critical"]:
                alerts.append({
                    "type": "risk_threshold_exceeded",
                    "severity": risk_assessment.get("overall_risk"),
                    "description": f"Patient has {risk_assessment.get('overall_risk')} overall risk level"
                })

            # Alerts for concerning trends
            for trend in trends:
                if trend.get("clinical_significance", {}).get("significance") == "high":
                    alerts.append({
                        "type": "trend_deterioration",
                        "severity": trend.get("clinical_significance", {}).get("urgency", "medium"),
                        "description": f"Significant {trend.get('trend_direction')} trend detected in {trend.get('question_id')}"
                    })

            # Alerts for anomalies
            for anomaly in anomalies:
                if anomaly.get("severity") == "high":
                    alerts.append({
                        "type": "sudden_change",
                        "severity": "high",
                        "description": f"Unusual value detected in {anomaly.get('question_id')}: {anomaly.get('value')}"
                    })

            return alerts

        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return []

    async def _generate_recommendations(self, condition: str, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate clinical recommendations based on analysis"""
        try:
            recommendations = []

            # Generate recommendations based on risk level
            if risk_assessment.get("overall_risk") == "critical":
                recommendations.append("Immediate clinical attention recommended")
                recommendations.append("Consider urgent care or emergency evaluation")

            elif risk_assessment.get("overall_risk") == "high":
                recommendations.append("Schedule follow-up appointment within 1 week")
                recommendations.append("Consider medication adjustment")

            # Generate condition-specific recommendations
            condition_recommendations = await self._generate_condition_recommendations(condition, risk_assessment)
            recommendations.extend(condition_recommendations)

            return list(set(recommendations))  # Remove duplicates

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Continue monitoring patient progress"]

    async def _generate_condition_recommendations(self, condition: str, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate condition-specific recommendations"""
        try:
            if condition == "diabetes":
                return [
                    "Monitor blood sugar levels more closely",
                    "Review medication adherence",
                    "Consider dietary adjustments"
                ]
            elif condition == "hypertension":
                return [
                    "Continue blood pressure monitoring",
                    "Maintain stress management techniques",
                    "Review medication effectiveness"
                ]
            elif condition == "depression":
                return [
                    "Schedule mental health follow-up",
                    "Consider therapy or counseling",
                    "Monitor medication side effects"
                ]
            else:
                return [f"Continue monitoring {condition} symptoms"]

        except Exception as e:
            logger.error(f"Error generating condition recommendations: {e}")
            return [f"Continue monitoring {condition} symptoms"]

    def _calculate_risk_score(self, risk_assessment: Dict[str, Any]) -> Optional[float]:
        """Calculate numerical risk score"""
        try:
            risk_mapping = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
            overall_risk = risk_assessment.get("overall_risk", "low")
            return risk_mapping.get(overall_risk, 0.5)

        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return None

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using mock logic instead of Gemini"""
        try:
            # Simple response generation based on keywords
            prompt_lower = prompt.lower()

            if "trend" in prompt_lower:
                return "Trend analysis completed"
            elif "risk" in prompt_lower:
                return "Risk assessment generated"
            else:
                return "Analysis completed"

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Analysis completed"
