# routes/auto_seed.py
import threading
import time
from flask import current_app
from extensions import db
from models import College
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your college data - you can also load this from a JSON file
COLLEGES_DATA = [
    # ── Tier 1 Engineering ────────────────────────────────────────
    {
        "name": "IIT Bombay",
        "city": "Mumbai",
        "state": "Maharashtra",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 3,
        "fees_per_year": 2.5,
        "avg_ctc": 28.5,
        "highest_ctc": 2.15,
        "placement_pct": 95,
        "established": 1958,
        "accreditation": "NAAC A++",
        "website": "https://www.iitb.ac.in",
        "top_recruiters": ["Google", "Microsoft", "Goldman Sachs", "Uber", "Flipkart", "DE Shaw", "Quadeye"]
    },
    {
        "name": "IIT Delhi",
        "city": "New Delhi",
        "state": "Delhi",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 2,
        "fees_per_year": 2.5,
        "avg_ctc": 27.0,
        "highest_ctc": 2.40,
        "placement_pct": 94,
        "established": 1961,
        "accreditation": "NAAC A++",
        "website": "https://home.iitd.ac.in",
        "top_recruiters": ["Microsoft", "Google", "Optiver", "Sprinklr", "Paytm", "Samsung Research"]
    },
    {
        "name": "IIT Madras",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 1,
        "fees_per_year": 2.5,
        "avg_ctc": 26.8,
        "highest_ctc": 1.80,
        "placement_pct": 92,
        "established": 1959,
        "accreditation": "NAAC A++",
        "website": "https://www.iitm.ac.in",
        "top_recruiters": ["Apple", "Amazon", "Oracle", "Intel", "Qualcomm", "Texas Instruments"]
    },
    {
        "name": "IIT Kanpur",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 4,
        "fees_per_year": 2.5,
        "avg_ctc": 25.0,
        "highest_ctc": 1.50,
        "placement_pct": 90,
        "established": 1959,
        "accreditation": "NAAC A++",
        "website": "https://www.iitk.ac.in",
        "top_recruiters": ["Jane Street", "Tower Research", "Goldman Sachs", "Google", "Cisco"]
    },
    {
        "name": "BITS Pilani",
        "city": "Pilani",
        "state": "Rajasthan",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 26,
        "fees_per_year": 5.8,
        "avg_ctc": 18.5,
        "highest_ctc": 1.20,
        "placement_pct": 92,
        "established": 1964,
        "accreditation": "NAAC A",
        "website": "https://www.bits-pilani.ac.in",
        "top_recruiters": ["Microsoft", "Samsung", "Capgemini", "Oracle", "VMware", "Nutanix"]
    },
    {
        "name": "NIT Trichy",
        "city": "Trichy",
        "state": "Tamil Nadu",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 9,
        "fees_per_year": 1.5,
        "avg_ctc": 14.0,
        "highest_ctc": 0.75,
        "placement_pct": 89,
        "established": 1964,
        "accreditation": "NAAC A++",
        "website": "https://www.nitt.edu",
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Zoho", "Qualcomm", "Amazon"]
    },
    {
        "name": "NIT Warangal",
        "city": "Warangal",
        "state": "Telangana",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 15,
        "fees_per_year": 1.4,
        "avg_ctc": 13.5,
        "highest_ctc": 0.70,
        "placement_pct": 87,
        "established": 1959,
        "accreditation": "NAAC A++",
        "website": "https://www.nitw.ac.in",
        "top_recruiters": ["Microsoft", "Amazon", "Deloitte", "Cognizant", "Hyundai", "Vedanta"]
    },
    {
        "name": "IIIT Hyderabad",
        "city": "Hyderabad",
        "state": "Telangana",
        "stream": "Engineering",
        "tier": 1,
        "nirf_rank": 32,
        "fees_per_year": 3.2,
        "avg_ctc": 22.0,
        "highest_ctc": 1.10,
        "placement_pct": 93,
        "established": 1998,
        "accreditation": "NAAC A",
        "website": "https://www.iiit.ac.in",
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Adobe", "Uber", "Intuit", "Atlassian"]
    },
    # ── Tier 2 Engineering ────────────────────────────────────────
    {
        "name": "VIT Vellore",
        "city": "Vellore",
        "state": "Tamil Nadu",
        "stream": "Engineering",
        "tier": 2,
        "nirf_rank": 11,
        "fees_per_year": 2.1,
        "avg_ctc": 9.5,
        "highest_ctc": 0.45,
        "placement_pct": 83,
        "established": 1984,
        "accreditation": "NAAC A++",
        "website": "https://vit.ac.in",
        "top_recruiters": ["TCS", "Wipro", "Infosys", "Capgemini", "L&T Infotech", "HCL"]
    },
    {
        "name": "SRM Institute of Science and Technology",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "stream": "Engineering",
        "tier": 2,
        "nirf_rank": 24,
        "fees_per_year": 3.0,
        "avg_ctc": 7.5,
        "highest_ctc": 0.35,
        "placement_pct": 80,
        "established": 1985,
        "accreditation": "NAAC A++",
        "website": "https://www.srmist.edu.in",
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "Capgemini", "Hexaware"]
    },
    {
        "name": "Manipal Institute of Technology",
        "city": "Manipal",
        "state": "Karnataka",
        "stream": "Engineering",
        "tier": 2,
        "nirf_rank": 49,
        "fees_per_year": 3.5,
        "avg_ctc": 8.0,
        "highest_ctc": 0.40,
        "placement_pct": 82,
        "established": 1957,
        "accreditation": "NAAC A++",
        "website": "https://manipal.edu/mit.html",
        "top_recruiters": ["Accenture", "Infosys", "TCS", "Mindtree", "Mphasis", "SAP"]
    },
    {
        "name": "Thapar Institute of Engineering",
        "city": "Patiala",
        "state": "Punjab",
        "stream": "Engineering",
        "tier": 2,
        "nirf_rank": 36,
        "fees_per_year": 2.7,
        "avg_ctc": 10.0,
        "highest_ctc": 0.50,
        "placement_pct": 85,
        "established": 1956,
        "accreditation": "NAAC A",
        "website": "https://www.thapar.edu",
        "top_recruiters": ["Microsoft", "Google", "Samsung", "Sapient", "Adobe", "Qualcomm"]
    },
    # ── Tier 3 Engineering ────────────────────────────────────────
    {
        "name": "GLBITM Greater Noida",
        "city": "Greater Noida",
        "state": "Uttar Pradesh",
        "stream": "Engineering",
        "tier": 3,
        "nirf_rank": None,
        "fees_per_year": 1.8,
        "avg_ctc": 5.5,
        "highest_ctc": 0.22,
        "placement_pct": 72,
        "established": 2000,
        "accreditation": "NAAC B++",
        "website": "https://glbitm.ac.in",
        "top_recruiters": ["TCS", "Infosys", "Wipro", "HCL", "Cognizant", "Tech Mahindra"]
    },
    # ── Tier 1 MBA ────────────────────────────────────────────────
    {
        "name": "IIM Ahmedabad",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "stream": "MBA",
        "tier": 1,
        "nirf_rank": 1,
        "fees_per_year": 16.0,
        "avg_ctc": 36.0,
        "highest_ctc": 1.10,
        "placement_pct": 100,
        "established": 1961,
        "accreditation": "NAAC A++",
        "website": "https://www.iima.ac.in",
        "top_recruiters": ["McKinsey", "BCG", "Bain", "Goldman Sachs", "Amazon", "Flipkart"]
    },
    {
        "name": "IIM Bangalore",
        "city": "Bangalore",
        "state": "Karnataka",
        "stream": "MBA",
        "tier": 1,
        "nirf_rank": 2,
        "fees_per_year": 24.0,
        "avg_ctc": 34.0,
        "highest_ctc": 1.20,
        "placement_pct": 100,
        "established": 1973,
        "accreditation": "NAAC A++",
        "website": "https://www.iimb.ac.in",
        "top_recruiters": ["McKinsey", "Deloitte", "JP Morgan", "Google", "Myntra", "PhonePe"]
    },
    {
        "name": "IIM Calcutta",
        "city": "Kolkata",
        "state": "West Bengal",
        "stream": "MBA",
        "tier": 1,
        "nirf_rank": 3,
        "fees_per_year": 27.0,
        "avg_ctc": 34.5,
        "highest_ctc": 1.30,
        "placement_pct": 100,
        "established": 1961,
        "accreditation": "NAAC A++",
        "website": "https://www.iimcal.ac.in",
        "top_recruiters": ["BCG", "Morgan Stanley", "Citigroup", "RIL", "Avendus", "OC&C"]
    },
    # ── Tier 2 MBA ────────────────────────────────────────────────
    {
        "name": "MDI Gurgaon",
        "city": "Gurugram",
        "state": "Delhi",
        "stream": "MBA",
        "tier": 2,
        "nirf_rank": 9,
        "fees_per_year": 22.0,
        "avg_ctc": 24.5,
        "highest_ctc": 0.60,
        "placement_pct": 99,
        "established": 1973,
        "accreditation": "NAAC A",
        "website": "https://www.mdi.ac.in",
        "top_recruiters": ["Deloitte", "Amazon", "HUL", "KPMG", "EY", "Nestle", "Asian Paints"]
    },
    {
        "name": "SPJIMR Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "stream": "MBA",
        "tier": 2,
        "nirf_rank": 7,
        "fees_per_year": 20.0,
        "avg_ctc": 28.0,
        "highest_ctc": 0.80,
        "placement_pct": 100,
        "established": 1981,
        "accreditation": "NAAC A++",
        "website": "https://www.spjimr.org",
        "top_recruiters": ["Flipkart", "HDFC", "Kotak", "Accenture", "P&G", "Airtel"]
    },
    # ── MCA ───────────────────────────────────────────────────────
    {
        "name": "NIT Trichy - MCA",
        "city": "Trichy",
        "state": "Tamil Nadu",
        "stream": "MCA",
        "tier": 1,
        "nirf_rank": 9,
        "fees_per_year": 0.8,
        "avg_ctc": 10.0,
        "highest_ctc": 0.35,
        "placement_pct": 88,
        "established": 1964,
        "accreditation": "NAAC A++",
        "website": "https://www.nitt.edu",
        "top_recruiters": ["TCS", "Infosys", "Zoho", "Freshworks", "Hexaware"]
    },
    {
        "name": "NIT Allahabad (MCA)",
        "city": "Allahabad",
        "state": "Uttar Pradesh",
        "stream": "MCA",
        "tier": 2,
        "nirf_rank": None,
        "fees_per_year": 0.6,
        "avg_ctc": 7.0,
        "highest_ctc": 0.28,
        "placement_pct": 82,
        "established": 1961,
        "accreditation": "NAAC A",
        "website": "https://www.mnnit.ac.in",
        "top_recruiters": ["TCS", "Wipro", "HCL", "Cognizant", "Infosys"]
    },
]

def seed_initial_data(app):
    """Seed initial college data and create admin user"""
    with app.app_context():
        try:
            # Check if we already have data
            existing_count = College.query.count()
            
            if existing_count > 0:
                logger.info(f"Database already has {existing_count} colleges. Skipping initial seed.")
                return
            
            # Add colleges
            colleges_added = 0
            for college_data in COLLEGES_DATA:
                try:
                    college = College(**college_data)
                    db.session.add(college)
                    colleges_added += 1
                except Exception as e:
                    logger.error(f"Error adding college {college_data.get('name')}: {e}")
                    continue
            
            # Add admin user
            from models import User
            
            admin_email = "admin@placeiq.in"
            admin = User.query.filter_by(email=admin_email).first()
            
            if not admin:
                admin = User(
                    name="PlaceIQ Admin",
                    email=admin_email,
                    role="admin",
                    stream="Administration"
                )
                admin.set_password("AdminPass@123")
                db.session.add(admin)
                logger.info("Admin user created")
            
            db.session.commit()
            logger.info(f"✅ Successfully seeded {colleges_added} colleges")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during initial seeding: {e}")

def auto_update_colleges(app):
    """Auto-update college data from external source"""
    with app.app_context():
        try:
            logger.info("Starting auto-update of college data...")
            
            # You can add logic here to fetch data from external APIs
            # For now, we'll just update existing records or add new ones
            
            for college_data in COLLEGES_DATA:
                existing = College.query.filter_by(
                    name=college_data["name"],
                    stream=college_data["stream"]
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in college_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.info(f"Updated: {college_data['name']}")
                else:
                    # Add new record
                    new_college = College(**college_data)
                    db.session.add(new_college)
                    logger.info(f"Added: {college_data['name']}")
            
            db.session.commit()
            logger.info("✅ Auto-update completed successfully")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during auto-update: {e}")

def update_from_json_file(app, json_file_path):
    """Update colleges from a JSON file"""
    import json
    
    with app.app_context():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                colleges_data = json.load(f)
            
            for college_data in colleges_data:
                existing = College.query.filter_by(
                    name=college_data["name"],
                    stream=college_data["stream"]
                ).first()
                
                if existing:
                    for key, value in college_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_college = College(**college_data)
                    db.session.add(new_college)
            
            db.session.commit()
            logger.info(f"Successfully updated from {json_file_path}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating from JSON: {e}")
            return False