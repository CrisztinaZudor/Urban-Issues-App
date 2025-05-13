
# Urban Issues App

**Urban Issues App** is a citizen-driven reporting system built with AI to detect and track urban problems in Cluj-Napoca. It empowers both citizens and city administrators to collaboratively improve city maintenance. Citizens can upload a photo of a problem they observe, and an AI model automatically identifies the issue and files a structured report. Administrators can then review and manage the status of these reports.

---

## Project Description

This Streamlit-based web application integrates a YOLOv11 object detection model trained on urban infrastructure issues. The app allows:

- **Citizens** to report issues (e.g., potholes, illegal parking, trash) via photo upload.
- **AI model** to detect the issue and generate a structured PDF report.
- **City administrators** to view, filter, and update the status of problems on an interactive map and dashboard.

The system supports multiple user roles (citizens and admins) and maintains persistent reports using SQLite.

---

## Model Details

The model, trained on **9,775 labeled images**, detects 14 urban issue classes

- **Model:** YOLOv11 
- **Training platform:** [Roboflow](https://app.roboflow.com/)
- **Precision:** 88.0%
- **Recall:** 78.9%
- **mAP@50:** 84.1%

| Class                    | Images | AP@50 |
|-------------------------|--------|-------|
| Cracks                  | 844    | 93%   |
| Potholes                | 1620   | 98%   |
| Graffiti                | 1022   | 69%   |
| Illegal Parking         | 145    | 94%   |
| Overflowing Trash Bins  | 214    | 87%   |
| Stray Animals           | 1718   | 98%   |
| Trash                   | 1214   | 35%   |
| Broken Urban Furniture  | 336    | 97%   |
| Dangerous Buildings     | 22     | 100%  |
| Flood                   | 439    | 98%   |
| Roadkills               | 631    | 85%   |
| Wild Animals            | 275    | 83%   |
| Fallen Trees            | 563    | 79%   |
| Open Manholes           | 791    | 76%   |

---

## Dataset

**Total images:** 9,775  
**Source breakdown:**

- **Most datasets **: Roboflow
- **Roadkill**: [BOKU University, 2024, GBIF](https://doi.org/10.15468/ejb47y)
- **Trash**: [TACO Dataset](https://tacodataset.org/)
- **Broken Urban Furniture & Dangerous Buildings**: Web-scraped using a custom script
  
---

## Features

- Image-based problem reporting
- Real-time object detection using YOLOv11
- Map with interactive markers by report status
- Automatic PDF report generation (FPDF)
- Admin-only dashboard with report status management
- GPS + address geocoding (via OpenCage + `streamlit-current-location`)
- Persistent SQLite-based storage

---

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

<details>
<summary><strong>requirements.txt contents</strong></summary>

```
streamlit==1.45.0  
pandas  
pydeck  
geopy  
fpdf  
requests  
Pillow  
opencv-python-headless  
streamlit-javascript  
streamlit-current-location  
streamlit-folium
```
</details>

---

## Deployment

The app is publicly available and hosted on [Streamlit Cloud](https://urban-issues-app.streamlit.app).

### Local Run (optional)

```bash
git clone https://github.com/CrisztinaZudor/Urban-Issues-App.git
cd Urban-Issues-App
streamlit run main.py
```

---

## User Roles

| Role         | Capabilities                                                 |
|--------------|--------------------------------------------------------------|
| Citizen      | Upload image, generate report, see map of public issues      |
| Administrator| Log in, filter/manage reports, change status, download PDFs |

---

##  Citation

For datasets reused in this project:

> **Roadkills**:  
> University of Natural Resources and Life Sciences, Vienna (2024). Roadkill. Occurrence dataset https://doi.org/10.15468/ejb47y accessed via GBIF.org on 2025-05-10.  

> **Trash**:  
> TACO Dataset: Trash Annotations in Context - https://tacodataset.org/

---

