"""
Mental Health Helplines - India and International
"""

# Indian Mental Health Helplines
INDIAN_HELPLINES = {
    "Crisis & Suicide Prevention": [
        {
            "name": "AASRA (Mumbai)",
            "contact": "91-9820466726",
            "hours": "24/7",
            "languages": "English, Hindi",
            "description": "Suicide prevention helpline"
        },
        {
            "name": "Vandrevala Foundation",
            "contact": "1860-2662-345 / 1800-2333-330",
            "hours": "24/7",
            "languages": "English, Hindi, and regional languages",
            "description": "Mental health support and crisis intervention"
        },
        {
            "name": "iCall (TISS)",
            "contact": "9152987821",
            "hours": "Mon-Sat, 8 AM - 10 PM",
            "languages": "English, Hindi, Marathi",
            "description": "Psychosocial helpline by TISS"
        },
        {
            "name": "Sneha Foundation (Chennai)",
            "contact": "044-24640050",
            "hours": "24/7",
            "languages": "English, Tamil, Hindi",
            "description": "Suicide prevention center"
        },
        {
            "name": "Sumaitri (Delhi)",
            "contact": "011-23389090",
            "hours": "2 PM - 10 PM",
            "languages": "English, Hindi",
            "description": "Crisis intervention center"
        }
    ],
    "Mental Health Support": [
        {
            "name": "NIMHANS Helpline (Bangalore)",
            "contact": "080-46110007",
            "hours": "Mon-Sat, 9 AM - 5:30 PM",
            "languages": "English, Hindi, Kannada",
            "description": "National Institute of Mental Health"
        },
        {
            "name": "Parivarthan Counselling (Bangalore)",
            "contact": "7676602602",
            "hours": "Mon-Sat, 10 AM - 6 PM",
            "languages": "English, Hindi, Kannada",
            "description": "Professional counseling services"
        },
        {
            "name": "Mann Talks",
            "contact": "8686139139",
            "hours": "Mon-Sat, 10 AM - 6 PM",
            "languages": "English, Hindi",
            "description": "Mental health support"
        },
        {
            "name": "Fortis Stress Helpline",
            "contact": "8376804102",
            "hours": "24/7",
            "languages": "English, Hindi",
            "description": "Stress and anxiety support"
        }
    ],
    "Women & Children": [
        {
            "name": "Women's Helpline",
            "contact": "1091 / 181",
            "hours": "24/7",
            "languages": "All regional languages",
            "description": "For women in distress"
        },
        {
            "name": "Childline India",
            "contact": "1098",
            "hours": "24/7",
            "languages": "All regional languages",
            "description": "For children in need"
        },
        {
            "name": "POCSO (Child Abuse)",
            "contact": "1098 / 155260",
            "hours": "24/7",
            "languages": "All regional languages",
            "description": "Child sexual abuse helpline"
        }
    ],
    "Specific Issues": [
        {
            "name": "Alcoholics Anonymous",
            "contact": "9833583472",
            "hours": "24/7",
            "languages": "English, Hindi",
            "description": "Alcohol addiction support"
        },
        {
            "name": "Narcotics Anonymous",
            "contact": "9833583472",
            "hours": "24/7",
            "languages": "English, Hindi",
            "description": "Drug addiction support"
        },
        {
            "name": "Connecting NGO (LGBTQ+)",
            "contact": "9137501393",
            "hours": "Mon-Sat, 12 PM - 8 PM",
            "languages": "English, Hindi",
            "description": "LGBTQ+ mental health support"
        }
    ]
}

# International Helplines
INTERNATIONAL_HELPLINES = {
    "United States": [
        {
            "name": "Suicide & Crisis Lifeline",
            "contact": "988",
            "hours": "24/7",
            "description": "National suicide prevention"
        },
        {
            "name": "Crisis Text Line",
            "contact": "Text HOME to 741741",
            "hours": "24/7",
            "description": "Text-based crisis support"
        },
        {
            "name": "SAMHSA National Helpline",
            "contact": "1-800-662-4357",
            "hours": "24/7",
            "description": "Substance abuse and mental health"
        }
    ],
    "United Kingdom": [
        {
            "name": "Samaritans",
            "contact": "116 123",
            "hours": "24/7",
            "description": "Emotional support"
        },
        {
            "name": "Mind Infoline",
            "contact": "0300 123 3393",
            "hours": "Mon-Fri, 9 AM - 6 PM",
            "description": "Mental health information"
        }
    ],
    "Australia": [
        {
            "name": "Lifeline",
            "contact": "13 11 14",
            "hours": "24/7",
            "description": "Crisis support"
        },
        {
            "name": "Beyond Blue",
            "contact": "1300 22 4636",
            "hours": "24/7",
            "description": "Depression and anxiety support"
        }
    ],
    "Canada": [
        {
            "name": "Crisis Services Canada",
            "contact": "1-833-456-4566",
            "hours": "24/7",
            "description": "National crisis line"
        }
    ]
}

# Emergency Numbers
EMERGENCY_NUMBERS = {
    "India": {
        "Police": "100",
        "Ambulance": "102 / 108",
        "Emergency": "112",
        "Women Helpline": "1091"
    },
    "International": {
        "US Emergency": "911",
        "UK Emergency": "999",
        "Australia Emergency": "000",
        "Europe Emergency": "112"
    }
}

def get_helplines_by_country(country="India"):
    """Get helplines for specific country"""
    if country == "India":
        return INDIAN_HELPLINES
    else:
        return INTERNATIONAL_HELPLINES

def get_emergency_numbers(country="India"):
    """Get emergency numbers for specific country"""
    return EMERGENCY_NUMBERS.get(country, EMERGENCY_NUMBERS["India"])

def format_helpline_display(helplines_dict):
    """Format helplines for display"""
    formatted = []
    for category, helplines in helplines_dict.items():
        formatted.append(f"\n### {category}\n")
        for helpline in helplines:
            formatted.append(f"**{helpline['name']}**")
            formatted.append(f"📞 {helpline['contact']}")
            formatted.append(f"🕐 {helpline['hours']}")
            if 'languages' in helpline:
                formatted.append(f"🗣️ {helpline['languages']}")
            formatted.append(f"ℹ️ {helpline['description']}\n")
    return "\n".join(formatted)
