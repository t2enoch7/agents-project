#### Notes



#### **diagram**

+------------------------------+
|        Patient Input         |
+---------------+--------------+
                |
                v
       +------------------+
       |  PRO_Pipeline     |  <-- SequentialAgent
       +--------+----------+
                |
        +-------+-------+-------+
        |       |       |       |
        v       v       v       v
Companion  Adaptive   TrendMonitor
 Agent     Questions     Agent
                      (calls cloud function)
                            |
                 +----------v----------+
                 | Cloud Function API  |
                 | + mock_patient_data |
                 +---------------------+




#### **Directory structure**

healthcare_pro_agent_system/
├── main.py
├── requirements.txt
├── data/
│   └── mock_patient_data.json
├── subagents/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── companion_agent.py
│   ├── adaptive_questionnaire_agent.py
│   └── trend_monitoring_agent.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── patient_data_service.py
├── cloud_function/
│   ├── main.py
│   ├── requirements.txt
│   └── data/
│       └── mock_patient_data.json

