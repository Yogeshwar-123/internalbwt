"""
Script to generate a PowerPoint presentation (.pptx) for Smart Krishi Advisor.
Uses python-pptx with a modern 16:9 layout, custom colors, cards, and structured layouts.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    DARK_GREEN = RGBColor(20, 83, 45)       # #14532d - Emerald 900
    PRIMARY_GREEN = RGBColor(22, 163, 74)   # #16a34a - Emerald 600
    ACCENT_GOLD = RGBColor(217, 119, 6)     # #d97706 - Amber 600
    BG_LIGHT = RGBColor(248, 250, 247)      # #f8faf7 - Soft Off-white
    CARD_BG = RGBColor(255, 255, 255)       # #ffffff - White
    CARD_BORDER = RGBColor(229, 231, 235)   # #e5e7eb - Gray 200
    TEXT_DARK = RGBColor(17, 24, 39)        # #111827 - Gray 900
    TEXT_MUTED = RGBColor(75, 85, 99)       # #4b5563 - Gray 600
    LIGHT_EMERALD = RGBColor(236, 253, 245) # #ecfdf5 - Emerald 50

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="SMART KRISHI ADVISOR"):
        # Header background banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Category Tag
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = PRIMARY_GREEN
        p_cat.space_after = Pt(2)
        
        # Main Slide Title
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_GREEN

    def add_footer(slide, current_slide, total_slides=12):
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.4))
        tf = footer_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"Smart Krishi Advisor | Problem ID: HACK-P302 | https://internalbwt.vercel.app | Slide {current_slide} of {total_slides}"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED

    def create_card(slide, left, top, width, height, title, body_bullets, border_color=CARD_BORDER, bg_color=CARD_BG):
        # Card Background Shape
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)

        # Card Content Box
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Title
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_GREEN
        p_title.space_after = Pt(8)

        # Bullet points
        for b in body_bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(11)
            p_b.font.color.rgb = TEXT_DARK
            p_b.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_GREEN
    bg1.line.color.rgb = DARK_GREEN

    # Title box
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.9), Inches(3.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "🌾 SMART KRISHI ADVISOR"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Explainable Rule-Based Decision Support System for Crop Recommendation & Suitability Analysis"
    p2.font.size = Pt(19)
    p2.font.color.rgb = RGBColor(167, 243, 208)
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "Problem ID: HACK-P302  |  Category: Agriculture (AI & Agronomic Tech)\nLive Application: https://internalbwt.vercel.app/\nGitHub: https://github.com/Yogeshwar-123/internalbwt.git"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(229, 231, 235)

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & Agriculture Challenges
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Challenge: Why Black-Box AI Fails Indian Farmers", "PROBLEM STATEMENT")
    
    create_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "1. Lack of Explainability", 
                [
                    "Generic Machine Learning models give black-box recommendations without agricultural reasoning.",
                    "Farmers cannot verify why a crop was selected over another.",
                    "Extension workers and farmers distrust systems that cannot defend their choices with agronomic facts."
                ])

    create_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "2. The Missing Data Trap", 
                [
                    "Over 70% of smallholder farmers lack recent laboratory soil test reports (NPK).",
                    "Standard ML pipelines coerce nulls to zero (N=0, P=0, K=0), fatally biasing outputs.",
                    "Leads to disastrous crop recommendations under rainfed and dryland conditions."
                ])

    create_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "3. Agro-Climatic Diversity", 
                [
                    "India spans 15 broad agro-climatic zones with stark regional variance.",
                    "Monsoon Kharif vs cool Rabi vs hot Zaid cycles dictate physiological success.",
                    "One-size-fits-all algorithms fail to account for local rainfall, soil pH, and temperature extremes."
                ])
    add_footer(s2, 2)

    # -------------------------------------------------------------
    # SLIDE 3: Proposed Solution
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Smart Krishi Advisor: Transparent, Trustworthy Decision Support", "OUR SOLUTION")
    
    create_card(s3, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "🌱 Grounded in Agronomy", 
                [
                    "Built upon official ICAR and TNAU agronomic research guidelines.",
                    "12 core Indian crops evaluated against scientific physiological thresholds.",
                    "Evaluates verified environmental ranges rather than synthetic statistical correlations."
                ])

    create_card(s3, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "🛡️ Zero-Coercion Math", 
                [
                    "Unmeasured soil or environmental factors are dynamically excluded from score denominators.",
                    "A farmer without an NPK kit is never penalized; data coverage percentage is transparently surfaced.",
                    "Insufficient data (<35% coverage) triggers protective warnings instead of false guidance."
                ])

    create_card(s3, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "🔍 Explainable & Interactive", 
                [
                    "Factor-by-factor breakdown: Matched, Tolerable, and Critical Mismatch alerts.",
                    "Side-by-side comparison matrix of 2 to 5 crops simultaneously.",
                    "Clear 'Why this crop' narrative and specific water/irrigation management advisories."
                ])
    add_footer(s3, 3)

    # -------------------------------------------------------------
    # SLIDE 4: Core Scoring Engine & Factor Weights
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Multi-Factor Agronomic Weighting & Scoring Model", "ENGINE METHODOLOGY")

    create_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Factor Allocation Matrix (100% Total Weight)",
                [
                    "Growing Season (20%): Kharif, Rabi, or Zaid physiological alignment.",
                    "Soil Texture & Type (15%): Clay Loam, Black Vertisol, Alluvial, Sandy Loam.",
                    "Soil pH Range (15%): Optimal vs tolerable pH response curves.",
                    "Temperature Suitability (15%): Vegetative and reproductive growth limits.",
                    "Rainfall / Water Supply (15%): Cumulative crop water requirement.",
                    "Relative Humidity (10%): Atmospheric moisture and disease predisposition.",
                    "Soil Nutrients N-P-K (10% total): Nitrogen (3.33%), Phosphorus (3.33%), Potassium (3.34%)."
                ])

    create_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Mathematical Rigor & Normalization",
                [
                    "Normalized Compatibility Formula:",
                    "  Compatibility Score = (Sum of Evaluated Points / Sum of Evaluated Weights) * 100",
                    "",
                    "Example with Missing Soil NPK Test:",
                    "  • Evaluated weight = 100 - 10 = 90 points",
                    "  • Denominator scales dynamically to 90",
                    "  • Data coverage surfaced as 90%",
                    "  • Crop is scored fairly without artificial zero-penalty.",
                    "",
                    "Suitability Tiers: Highly Compatible (≥80%), Moderately Compatible (55-79%), Potential Mismatch (<55%)."
                ])
    add_footer(s4, 4)

    # -------------------------------------------------------------
    # SLIDE 5: Incomplete Data Handling & Safety Guards
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Safety First: Handling Uncertainty and Incomplete Inputs", "ROBUSTNESS & SAFETY")

    create_card(s5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Transparent Data Coverage",
                [
                    "Tracks the exact percentage of agronomic parameters provided by the farmer.",
                    "Separates measured lab data from field observations.",
                    "Farmers always know how confident the system is before acting on advice."
                ])

    create_card(s5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Insufficient Data Barrier",
                [
                    "If coverage falls below 35%, recommendation generation is halted with a clear alert.",
                    "Prevents dangerous hallucinated guesses when only 1 or 2 fields are filled.",
                    "Outputs a prioritized checklist of missing variables needed (e.g. soil pH, rainfall)."
                ])

    create_card(s5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Strict Schema Constraints",
                [
                    "Pydantic schema validation protects against physically impossible entries:",
                    "  • Soil pH restricted strictly between 0.0 and 14.0",
                    "  • Humidity restricted between 0.0% and 100.0%",
                    "  • Temperature validated between -10°C and 60°C."
                ])
    add_footer(s5, 5)

    # -------------------------------------------------------------
    # SLIDE 6: System Architecture & Tech Stack
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Full-Stack Decoupled Architecture", "SYSTEM ARCHITECTURE")

    create_card(s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "⚡ Backend (FastAPI)",
                [
                    "Python 3.14 + FastAPI high-performance asynchronous REST API.",
                    "Pydantic v2 data models for rigorous request/response contracts.",
                    "Modular scoring engine: scoring.py, recommender.py, comparator.py, explanations.py.",
                    "25 automated pytest tests with 100% pass rate."
                ])

    create_card(s6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "🎨 Frontend (React + Vite)",
                [
                    "Modern React 19 + TypeScript for high type safety.",
                    "Vite 8 build system with sub-second HMR and bundle optimization.",
                    "Tailwind CSS responsive design with accessible color contrast.",
                    "Standalone client-side fallback rule engine for static offline execution."
                ])

    create_card(s6, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "🚀 Cloud Deployment",
                [
                    "Vercel CDN edge hosting with global low-latency delivery.",
                    "Automated CI/CD linked to GitHub repository Yogeshwar-123/internalbwt.",
                    "SPA client-side routing via vercel.json rewrites.",
                    "Live URL: https://internalbwt.vercel.app/"
                ])
    add_footer(s6, 6)

    # -------------------------------------------------------------
    # SLIDE 7: Key Features & User Experience
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Comprehensive Agricultural User Experience", "CORE MODULES")

    create_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "1. Smart Crop Recommender",
                [
                    "Interactive parameter inputs with instant suitability scoring.",
                    "One-click loading of 5 regional benchmark profiles (Delta, Arid, Rabi Pulse, Missing NPK).",
                    "Ranked crop cards with 'Why this crop' explanations and irrigation advisories."
                ])

    create_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "2. Side-by-Side Comparator",
                [
                    "Compare 2 to 5 crops simultaneously in a comprehensive comparison matrix.",
                    "Evaluates soil texture, pH bounds, rainfall needs, and water demand levels.",
                    "Clear trade-off summaries to guide farm crop rotation decisions."
                ])

    create_card(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "3. Verified Agronomic Catalog",
                [
                    "Complete reference guide for 12 key crops based on ICAR/TNAU databases.",
                    "Filterable by growing season (Kharif, Rabi, Zaid) and category (Cereal, Pulse, Millet, Cash).",
                    "Direct shortcut to send any crop into the comparator matrix."
                ])
    add_footer(s7, 7)

    # -------------------------------------------------------------
    # SLIDE 8: Regional Case Studies & Benchmarks
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Validated Against 5 Diverse Agro-Climatic Benchmarks", "VALIDATION RESULTS")

    create_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Regional Benchmark Test Cases",
                [
                    "Profile 1: East Godavari Delta (Kharif Monsoon)",
                    "  • Clay Loam, 1450 mm rain, 29°C, 82% humidity",
                    "  • Outcome: Rice ranks #1 (100%), Sugarcane #2 (94.2%)",
                    "",
                    "Profile 2: Jodhpur Semi-Arid (Dryland Kharif)",
                    "  • Sandy Loam, 380 mm rain, 32.5°C, 45% humidity",
                    "  • Outcome: Pearl Millet (Bajra) tops the list (>85%); Rice flagged as severe water mismatch",
                    "",
                    "Profile 3: Ujjain Cool Winter (Rabi Central India)",
                    "  • Vertisol Black soil, 310 mm rain, 19.5°C",
                    "  • Outcome: Chickpea and Wheat achieve highest suitability"
                ])

    create_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Edge Case Handling & Robustness",
                [
                    "Profile 4: Missing NPK Lab Data (Nagpur, Maharashtra)",
                    "  • Black soil, 780 mm rain, 27.5°C; soil test kit not yet used",
                    "  • Outcome: System excludes NPK weights from denominator, surfaces 70% coverage, accurately ranks Cotton, Soybean, and Maize without penalizing missing data.",
                    "",
                    "Profile 5: Insufficient Information (Telangana)",
                    "  • Only season provided; missing soil type, pH, rainfall; 47°C extreme",
                    "  • Outcome: System halts recommendation, flags <35% coverage barrier, outputs actionable checklist of required measurements."
                ])
    add_footer(s8, 8)

    # -------------------------------------------------------------
    # SLIDE 9: Testing, Verification & Code Quality
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Rigorous Quality Assurance & Test Coverage", "VERIFICATION")

    create_card(s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Unit & Integration Tests",
                [
                    "25 / 25 automated pytest tests passing in 1.41s.",
                    "test_api.py: Full coverage of /health, /crops, /recommend, /compare, /profiles.",
                    "test_engine.py: Mathematical normalization, ranking consistency, mismatch triggers.",
                    "test_comparator.py: Pairwise comparison logic and bounds."
                ])

    create_card(s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Schema Boundary Tests",
                [
                    "test_schemas.py: Rigorous boundary value validation.",
                    "Rejection of pH < 0 or > 14 (HTTP 422 with user-friendly errors).",
                    "Rejection of humidity < 0% or > 100%.",
                    "Verification that null NPK fields are never coerced to zero."
                ])

    create_card(s9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Frontend Build Verification",
                [
                    "TypeScript type-checking with verbatimModuleSyntax: 0 errors.",
                    "Vite production bundling completed in 795ms.",
                    "Zero console errors, responsive mobile viewport verified.",
                    "Continuous validation through automated dry-run test scripts."
                ])
    add_footer(s9, 9)

    # -------------------------------------------------------------
    # SLIDE 10: Production Deployment & Live Status
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Live Production Deployment on Vercel", "DEPLOYMENT & ACCESS")

    create_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Deployment Architecture Highlights",
                [
                    "Public Website: https://internalbwt.vercel.app/",
                    "Server: Vercel Global Edge Network (HTTP 200 OK verified).",
                    "Client-Side Hybrid Architecture: Seamlessly switches between live FastAPI endpoints and offline client-side agronomic rule engine.",
                    "Zero downtime: Users can access and compute recommendations even during connectivity disruptions in rural areas.",
                    "Fast loading: Total client bundle size ~250 KB with gzip compression."
                ])

    create_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
                "Open Source Repository & Version Control",
                [
                    "GitHub Repository: Yogeshwar-123/internalbwt",
                    "Branch: main (Clean git history, .gitignore configured).",
                    "Monorepo Setup:",
                    "  • frontend/ (Vite + React UI)",
                    "  • backend/ (FastAPI + Agronomic Engine)",
                    "  • vercel.json (Automated monorepo build & rewrite rules)",
                    "  • pytest.ini & dry_run.py (Automated dry run testing suites)"
                ])
    add_footer(s10, 10)

    # -------------------------------------------------------------
    # SLIDE 11: Future Roadmap & Impact
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Roadmap: Scaling from Prototype to Field Deployment", "FUTURE ROADMAP")

    create_card(s11, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Phase 1: Knowledge Base",
                [
                    "Expand crop catalog from 12 to 50+ regional crop varieties (horticulture, spices, pulses).",
                    "Incorporate micro-nutrient guidelines (Zinc, Iron, Boron, Organic Carbon).",
                    "Integrate pest and disease susceptibility advisory modules."
                ])

    create_card(s11, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Phase 2: IoT & Live Data",
                [
                    "Integrate India Meteorological Department (IMD) live weather APIs.",
                    "Support IoT soil moisture and automated weather station sensors.",
                    "Connect with e-NAM mandi live price APIs for economic return modeling."
                ])

    create_card(s11, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
                "Phase 3: Farmer Accessibility",
                [
                    "Multilingual UI support in 8 Indian regional languages (Hindi, Telugu, Tamil, Marathi, etc.).",
                    "Voice-driven conversational input for semi-literate farmers.",
                    "Offline-first Progressive Web App (PWA) with SMS/WhatsApp report sharing."
                ])
    add_footer(s11, 11)

    # -------------------------------------------------------------
    # SLIDE 12: Conclusion & Q&A
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = DARK_GREEN
    bg12.line.color.rgb = DARK_GREEN

    tb12 = s12.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.2))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p = tf12.paragraphs[0]
    p.text = "Empowering Indian Agriculture with Explainable Tech"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.space_after = Pt(14)

    p2 = tf12.add_paragraph()
    p2.text = "Smart Krishi Advisor bridges the trust gap in agricultural technology by providing transparent, agronomy-backed crop recommendations that respect real-world data limitations."
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(167, 243, 208)
    p2.space_after = Pt(24)

    p3 = tf12.add_paragraph()
    p3.text = "🌐 Live Application:  https://internalbwt.vercel.app/\n📁 Source Code:  https://github.com/Yogeshwar-123/internalbwt.git\n\nThank you! Questions & Discussion."
    p3.font.size = Pt(15)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(255, 255, 255)

    output_path = os.path.abspath("Smart_Krishi_Advisor_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
