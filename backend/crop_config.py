"""
Configurable Crop Growth Telemetry & Agronomic Profiles.
Defines growth stages (Germination, Seedling, Vegetative, Flowering, Fruiting, Harvesting),
crop varieties, total cycle durations, and biological progress calculation models.
"""

from datetime import date, timedelta

# The standard 6 biological growth stages
GROWTH_STAGES = [
    'Germination',
    'Seedling',
    'Vegetative',
    'Flowering',
    'Fruiting',
    'Harvesting'
]

# Detailed metadata for each growth stage
STAGE_METADATA = {
    'Germination': {
        'icon': 'bi-moisture',
        'badge_class': 'badge-info',
        'color': '#0ea5e9',
        'summary': 'Seed imbibition, activation of enzymes, and emergence of radicle and shoot through soil surface.',
        'water_need': 'Moderate moisture (keep topsoil damp, avoid waterlogging to prevent seed rot)',
        'nutrient_focus': 'Phosphorus-rich starter fertilizer to stimulate strong root initiation',
        'risk_factors': 'Damping-off fungal pathogens, soil crusting, and uneven seedbed depth'
    },
    'Seedling': {
        'icon': 'bi-sprout',
        'badge_class': 'badge-success',
        'color': '#10b981',
        'summary': 'Establishment of first true leaves, rapid root elongation, and transition to autotrophic photosynthesis.',
        'water_need': 'Light, frequent irrigation to maintain soil moisture around shallow root zone',
        'nutrient_focus': 'Balanced N-P-K (1:1:1) with micro-nutrients (Zinc, Iron) to support foliar expansion',
        'risk_factors': 'Cutworms, flea beetles, seedling blights, and wind desiccation'
    },
    'Vegetative': {
        'icon': 'bi-flower1',
        'badge_class': 'badge-primary',
        'color': '#16a34a',
        'summary': 'Vigorous vegetative biomass accumulation, stem elongation, tiller/branch production, and canopy expansion.',
        'water_need': 'Consistent deep watering (60-70% available field capacity) supporting high transpiration',
        'nutrient_focus': 'High Nitrogen top-dressing to build chlorophyll, leaf area, and sturdy structural stalks',
        'risk_factors': 'Foliar fungal spots, defoliating caterpillars, and severe weed competition'
    },
    'Flowering': {
        'icon': 'bi-flower2',
        'badge_class': 'badge-warning',
        'color': '#f59e0b',
        'summary': 'Flower bud initiation, anthesis, pollen release, and ovule fertilization (critical yield determination window).',
        'water_need': 'Peak critical moisture demand; water stress during flowering causes massive bloom/tassel drop',
        'nutrient_focus': 'Potassium and Phosphorus rich fertilization with Calcium and Boron for pollen viability',
        'risk_factors': 'Heat stress, drought shock, thrips, blossom blights, and fungal rusts'
    },
    'Fruiting': {
        'icon': 'bi-apple',
        'badge_class': 'badge-danger',
        'color': '#ef4444',
        'summary': 'Fruit set, cell expansion, starch and sugar translocation, grain filling, or tuber bulking.',
        'water_need': 'Even, steady irrigation; fluctuating soil moisture leads to fruit cracking and blossom end rot',
        'nutrient_focus': 'High Potassium (K) to optimize sugar translocation, starch synthesis, and fruit size/weight',
        'risk_factors': 'Fruit borers, anthracnose, downy mildew, and lodging under heavy fruit load'
    },
    'Harvesting': {
        'icon': 'bi-basket',
        'badge_class': 'badge-dark',
        'color': '#84cc16',
        'summary': 'Physiological maturity reached. Grain moisture drops, fruit reaches optimal brix/color, foliage naturally senesces.',
        'water_need': 'Taper off or stop irrigation 7-14 days prior to harvest to ease field machinery entry and dry grain',
        'nutrient_focus': 'Zero additional nitrogen; allow plant to translocate remaining reserves to harvest organs',
        'risk_factors': 'Pre-harvest sprouting, untimely rainfall, post-maturity shatter, and storage molds'
    }
}

# Configurable Crop Agronomic Profiles (durations, varieties, and stage days)
CROP_PROFILES = {
    'rice': {
        'display_name': 'Rice (Paddy)',
        'category': 'Cereal Grain',
        'total_days': 120,
        'varieties': ['Basmati 370', 'IR64', 'Jasmine', 'Sona Masoori', 'Ponni', 'Swarna', 'Pusa 1121'],
        'stage_durations': {
            'Germination': 10,
            'Seedling': 15,
            'Vegetative': 30,
            'Flowering': 25,
            'Fruiting': 25,
            'Harvesting': 15
        }
    },
    'wheat': {
        'display_name': 'Wheat',
        'category': 'Cereal Grain',
        'total_days': 115,
        'varieties': ['Sharbati', 'HD-2967', 'Durum', 'PBW-343', 'Emmer', 'Sonora 64', 'Kalyansona'],
        'stage_durations': {
            'Germination': 8,
            'Seedling': 14,
            'Vegetative': 28,
            'Flowering': 25,
            'Fruiting': 25,
            'Harvesting': 15
        }
    },
    'corn': {
        'display_name': 'Corn (Maize)',
        'category': 'Cereal Grain',
        'total_days': 105,
        'varieties': ['Sweet Corn', 'Golden Bantam', 'Dent Corn', 'Pioneer P3394', 'Flint Corn', 'DKC 9108'],
        'stage_durations': {
            'Germination': 7,
            'Seedling': 13,
            'Vegetative': 30,
            'Flowering': 20,
            'Fruiting': 22,
            'Harvesting': 13
        }
    },
    'tomato': {
        'display_name': 'Tomato',
        'category': 'Solanaceous Vegetable',
        'total_days': 90,
        'varieties': ['Roma VF', 'Beefsteak', 'San Marzano', 'Cherry Red', 'Celebrity', 'Early Girl'],
        'stage_durations': {
            'Germination': 8,
            'Seedling': 16,
            'Vegetative': 21,
            'Flowering': 17,
            'Fruiting': 18,
            'Harvesting': 10
        }
    },
    'potato': {
        'display_name': 'Potato',
        'category': 'Tuber Crop',
        'total_days': 95,
        'varieties': ['Russet Burbank', 'Yukon Gold', 'Kennebec', 'Red Pontiac', 'Kufri Jyoti', 'Atlantic'],
        'stage_durations': {
            'Germination': 12,
            'Seedling': 13,
            'Vegetative': 23,
            'Flowering': 20,
            'Fruiting': 17,
            'Harvesting': 10
        }
    },
    'cotton': {
        'display_name': 'Cotton',
        'category': 'Fiber Cash Crop',
        'total_days': 150,
        'varieties': ['Bt Cotton RCH-2', 'Pima Extra Long', 'Upland Delta', 'Giza 86', 'Suraj'],
        'stage_durations': {
            'Germination': 10,
            'Seedling': 18,
            'Vegetative': 32,
            'Flowering': 35,
            'Fruiting': 40,
            'Harvesting': 15
        }
    },
    'soybean': {
        'display_name': 'Soybean',
        'category': 'Legume & Oilseed',
        'total_days': 100,
        'varieties': ['JS-335', 'Bragg', 'Clark 63', 'Williams 82', 'Edamame Green', 'Hardee'],
        'stage_durations': {
            'Germination': 7,
            'Seedling': 13,
            'Vegetative': 25,
            'Flowering': 20,
            'Fruiting': 23,
            'Harvesting': 12
        }
    },
    'sugarcane': {
        'display_name': 'Sugarcane',
        'category': 'Perennial Grass / Cash Crop',
        'total_days': 360,
        'varieties': ['Co 0238', 'Co 86032', 'CoLk 94184', 'CP 72-2086', 'Yellow Mauritius'],
        'stage_durations': {
            'Germination': 35,
            'Seedling': 55,
            'Vegetative': 140,
            'Flowering': 40,
            'Fruiting': 60,
            'Harvesting': 30
        }
    },
    'pepper': {
        'display_name': 'Chili & Bell Pepper',
        'category': 'Solanaceous Vegetable',
        'total_days': 85,
        'varieties': ['California Wonder', 'Jalapeño M', 'Cayenne Long Slim', 'Habanero Orange', 'Guntur Sannam'],
        'stage_durations': {
            'Germination': 9,
            'Seedling': 15,
            'Vegetative': 20,
            'Flowering': 16,
            'Fruiting': 15,
            'Harvesting': 10
        }
    },
    'other': {
        'display_name': 'General Field Crop',
        'category': 'Agronomic Crop',
        'total_days': 90,
        'varieties': ['Standard Certified Variety', 'Heritage Variety', 'Hybrid F1', 'Local Selection'],
        'stage_durations': {
            'Germination': 8,
            'Seedling': 14,
            'Vegetative': 24,
            'Flowering': 18,
            'Fruiting': 16,
            'Harvesting': 10
        }
    }
}


def get_crop_profile(crop_type: str) -> dict:
    """Return the configuration profile for a crop type, with sensible fallbacks."""
    key = (crop_type or 'other').strip().lower()
    return CROP_PROFILES.get(key, CROP_PROFILES['other'])


def calculate_crop_growth(crop_type: str, planting_date: date, custom_variety: str = None) -> dict:
    """
    Calculate biological crop growth progress, current and milestone stages,
    expected harvest date, and S-curve telemetry points.

    Returns rich dictionary containing:
      - elapsed_days: days elapsed since planting date
      - total_days: total crop cycle duration
      - progress: overall percentage [0.0, 100.0]
      - harvest_date: calculated harvest date (planting_date + total_days)
      - days_remaining: days left until target harvest
      - is_harvest_ready: boolean whether cycle has reached or exceeded 100%
      - current_stage: name of the currently active growth stage
      - current_stage_index: index of active stage (0 to 5)
      - stage_progress_percent: progress percentage WITHIN the active stage
      - stages_timeline: list of detailed dictionaries for all 6 stages
      - chart_curve: x (days) and y (biomass %) data points for Chart.js
    """
    profile = get_crop_profile(crop_type)
    total_days = profile['total_days']
    stage_durations = profile['stage_durations']

    today = date.today()
    if isinstance(planting_date, str):
        try:
            planting_date = date.fromisoformat(planting_date)
        except ValueError:
            planting_date = today

    # Elapsed days calculation
    elapsed_days = max(0, (today - planting_date).days)
    progress = min(100.0, round((elapsed_days / total_days) * 100.0, 1))
    harvest_date = planting_date + timedelta(days=total_days)
    days_remaining = max(0, (harvest_date - today).days)
    is_harvest_ready = elapsed_days >= total_days

    # Build the 6-stage chronological milestone timeline
    accumulated_days = 0
    stages_timeline = []
    active_stage_name = GROWTH_STAGES[-1]
    active_stage_idx = len(GROWTH_STAGES) - 1
    stage_progress_pct = 100.0

    for idx, stage_name in enumerate(GROWTH_STAGES):
        duration = stage_durations.get(stage_name, int(total_days / len(GROWTH_STAGES)))
        stage_start_day = accumulated_days
        stage_end_day   = accumulated_days + duration
        accumulated_days = stage_end_day

        meta = STAGE_METADATA.get(stage_name, STAGE_METADATA['Vegetative'])

        # Stage status check
        if elapsed_days >= stage_end_day:
            status = 'completed'
            sub_pct = 100.0
        elif stage_start_day <= elapsed_days < stage_end_day:
            status = 'current'
            active_stage_name = stage_name
            active_stage_idx = idx
            stage_elapsed = elapsed_days - stage_start_day
            sub_pct = round((stage_elapsed / duration) * 100.0, 1)
            stage_progress_pct = sub_pct
        else:
            status = 'upcoming'
            sub_pct = 0.0

        stage_start_date = planting_date + timedelta(days=stage_start_day)
        stage_end_date   = planting_date + timedelta(days=stage_end_day)

        stages_timeline.append({
            'index': idx,
            'name': stage_name,
            'status': status,
            'duration_days': duration,
            'start_day': stage_start_day,
            'end_day': stage_end_day,
            'start_date': stage_start_date,
            'end_date': stage_end_date,
            'sub_progress_percent': sub_pct,
            'icon': meta['icon'],
            'badge_class': meta['badge_class'],
            'color': meta['color'],
            'summary': meta['summary'],
            'water_need': meta['water_need'],
            'nutrient_focus': meta['nutrient_focus'],
            'risk_factors': meta['risk_factors']
        })

    # If elapsed days exceeds total days, current is Harvesting (100% complete)
    if is_harvest_ready:
        active_stage_name = 'Harvesting'
        active_stage_idx = 5
        stage_progress_pct = 100.0
        stages_timeline[-1]['status'] = 'current'

    # Generate Biological S-Curve (Sigmoidal) Data Points for Chart.js
    # y(t) = 100 / (1 + exp(-k * (t - t0)))
    chart_days = []
    chart_expected = []
    step = max(1, total_days // 15)
    for d in range(0, total_days + 1, step):
        chart_days.append(f"Day {d}")
        # Sigmoidal growth curve normalized to 0-100%
        # Midpoint around 55% of cycle
        norm = (d - (total_days * 0.45)) / (total_days * 0.16)
        sig = 100.0 / (1.0 + (2.71828 ** (-norm)))
        chart_expected.append(round(sig, 1))

    # Ensure Day 0 is ~0% and final day is 100%
    chart_expected[0] = 0.0
    chart_expected[-1] = 100.0

    return {
        'crop_type': crop_type,
        'profile_name': profile['display_name'],
        'category': profile['category'],
        'variety': custom_variety or profile['varieties'][0],
        'available_varieties': profile['varieties'],
        'planting_date': planting_date,
        'harvest_date': harvest_date,
        'elapsed_days': elapsed_days,
        'total_days': total_days,
        'days_remaining': days_remaining,
        'progress': progress,
        'is_harvest_ready': is_harvest_ready,
        'current_stage': active_stage_name,
        'current_stage_index': active_stage_idx,
        'stage_progress_percent': stage_progress_pct,
        'current_stage_meta': STAGE_METADATA.get(active_stage_name, {}),
        'stages': stages_timeline,
        'chart': {
            'labels': chart_days,
            'expected_curve': chart_expected,
            'current_day': elapsed_days,
            'current_progress': progress
        }
    }

