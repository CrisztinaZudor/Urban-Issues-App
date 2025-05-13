# Urban Issues App

**Urban Issues App** is a Streamlit-based web platform that helps identify and track urban problems in Cluj-Napoca through citizen participation and AI. Users can upload photos of public issues, and a YOLOv11 model detects and classifies the problem. The system generates structured reports, stores them in a SQLite database, and displays them on an interactive map. Administrators can manage these reports through a dedicated dashboard.

---

## Features

- Image upload and AI-based issue detection using YOLOv11  
- Automatic PDF report generation  
- Location support via GPS or manual address (geocoded)  
- Map visualization with status-based filtering  
- Admin dashboard to manage reports and update statuses  
- SQLite database for persistent report storage  

---

## User Roles

| Role        | Permissions |
|-------------|-------------|
| Citizen     | Upload photos, view map, generate reports |
| Admin       | Filter reports, update statuses, download PDFs |

---


## Model Overview

- **Architecture:** YOLOv11  
- **Training platform:** [Roboflow](https://app.roboflow.com/)  
- **Dataset size:** 9,775 labeled images  
- **Metrics:**
  - Precision: 88.0%  
  - Recall: 78.9%  
  - mAP@50: 84.1%  

**Detected classes and performance:**

| Class                   | Images | AP@50 |
|------------------------|--------|-------|
| Potholes               | 1,620  | 98%   |
| Cracks                 | 844    | 93%   |
| Illegal Parking        | 145    | 94%   |
| Overflowing Trash Bins| 214    | 87%   |
| Stray Animals          | 1,718  | 98%   |
| Trash                  | 1,214  | 35%   |
| Graffiti               | 1,022  | 69%   |
| Broken Urban Furniture | 336    | 97%   |
| Dangerous Buildings    | 22     | 100%  |
| Flood                  | 439    | 98%   |
| Roadkills              | 631    | 85%   |
| Wild Animals           | 275    | 83%   |
| Fallen Trees           | 563    | 79%   |
| Open Manholes          | 791    | 76%   |

---

## Dataset Sources

- **Most datasets:** Roboflow 
- **Roadkill:** [University of Natural Resources and Life Sciences, Vienna (2024). Roadkill. GBIF.](https://doi.org/10.15468/ejb47y)  
- **Trash:** [TACO Dataset – Trash Annotations in Context](https://tacodataset.org)  
- **Broken Urban Furniture & Dangerous Buildings:** Web-scraped using a custom Python script  

---


## Installation

```bash
git clone https://github.com/CrisztinaZudor/Urban-Issues-App.git
cd Urban-Issues-App
pip install -r requirements.txt
streamlit run main.py
```

<details>
<summary><strong>requirements.txt</strong></summary>

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

The app is publicly hosted on Streamlit Cloud:  
**[urban-issues-app.streamlit.app](https://urban-issues-app.streamlit.app)**
