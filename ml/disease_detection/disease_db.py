"""
Comprehensive Agronomic Disease Information Database.
Provides symptoms, clinical signs, organic precautions, and chemical treatments
for crop pathologies and healthy foliage.
"""

DISEASE_DATABASE = {
    'Tomato_Early_Blight': {
        'crop': 'Tomato',
        'display_name': 'Tomato Early Blight',
        'pathogen': 'Alternaria solani (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Dark brown to black necrotic spots with characteristic concentric rings ("target board" pattern) '
            'developing first on older, lower foliage. Spots are surrounded by chlorotic yellow halos. '
            'Severe infestation leads to extensive defoliation, sunscald on fruits, and dark sunken stem lesions.'
        ),
        'precautions': (
            '1. Apply preventative copper-based fungicides or mancozeb/chlorothalonil at first sign of lesions.\n'
            '2. Prune and safely incinerate infected lower foliage to reduce splash-borne spore transmission.\n'
            '3. Practice minimum 3-year crop rotation with non-solanaceous crops.\n'
            '4. Implement drip irrigation rather than overhead sprinklers to keep foliage dry.'
        ),
        'organic_control': 'Apply Bacillus subtilis bio-fungicide or neem seed extract (3%). Use straw mulching to prevent soil splashing.',
        'chemical_control': 'Foliar spray of Chlorothalonil 75 WP (2g/L) or Azoxystrobin 23 SC (1ml/L) at 10-14 day intervals.'
    },
    'Tomato_Late_Blight': {
        'crop': 'Tomato',
        'display_name': 'Tomato Late Blight',
        'pathogen': 'Phytophthora infestans (Oomycete)',
        'is_healthy': False,
        'symptoms': (
            'Irregular, pale to dark green water-soaked lesions that rapidly expand and turn purplish-black. '
            'Under high humidity (>90%) and cool temperatures (15-20°C), delicate white cottony fungal sporulation '
            'appears on leaf undersides. Entire vines can collapse within days, with greasy brown rot on green fruit.'
        ),
        'precautions': (
            '1. Immediately destroy heavily infected plants; do not compost blight-infected debris.\n'
            '2. Apply systemic fungicides before high-humidity cool rain fronts arrive.\n'
            '3. Maintain wide plant spacing for rapid canopy drying and air circulation.\n'
            '4. Plant certified blight-resistant hybrid cultivars (e.g., Mountain Magic, Defiant).'
        ),
        'organic_control': 'Preventative copper hydroxide or copper octanoate sprays. Bio-control with Trichoderma harzianum.',
        'chemical_control': 'Metalaxyl + Mancozeb (Ridomil Gold 2.5g/L) or Cymoxanil + Mancozeb (2g/L) alternating with Dimethomorph.'
    },
    'Tomato_Leaf_Mold': {
        'crop': 'Tomato',
        'display_name': 'Tomato Leaf Mold',
        'pathogen': 'Passalora fulva (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Pale green or yellowish spots with indefinite margins on the upper leaf surface. The corresponding '
            'lower surface exhibits dense olive-green to grayish velvety fungal mold growth. Leaves curl, wither, '
            'and drop prematurely, especially in high-tunnel or greenhouse environments.'
        ),
        'precautions': (
            '1. Reduce relative humidity below 85% through aggressive greenhouse ventilation and horizontal fans.\n'
            '2. Avoid overhead irrigation; irrigate strictly at the base or through sub-surface drip.\n'
            '3. Prune bottom leaves to enhance under-canopy air currents.'
        ),
        'organic_control': 'Potassium bicarbonate sprays (3g/L) to increase leaf surface pH and suppress mycelial expansion.',
        'chemical_control': 'Copper oxychloride 50 WP (3g/L) or Difenoconazole 25 EC (0.5ml/L).'
    },
    'Tomato_Septoria_Leaf_Spot': {
        'crop': 'Tomato',
        'display_name': 'Tomato Septoria Leaf Spot',
        'pathogen': 'Septoria lycopersici (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Numerous small, circular spots (2-3 mm) with dark brown margins and sunken grayish-white centers. '
            'Tiny black specks (pycnidia fruiting bodies) are clearly visible inside lesion centers with a hand lens. '
            'Foliage yellows from the bottom upwards and drops rapidly, leaving exposed fruit vulnerable to sunscald.'
        ),
        'precautions': (
            '1. Remove and destroy infected lower leaves early in the season.\n'
            '2. Keep foliage dry and stake plants to elevate canopy at least 30 cm above bare soil.\n'
            '3. Deep plow or remove all solanaceous crop residues post-harvest.'
        ),
        'organic_control': 'Apply liquid copper soap or bio-fungicides formulated with Streptomyces lydicus.',
        'chemical_control': 'Mancozeb 75 WP (2.5g/L) or Chlorothalonil (2ml/L) sprayed at weekly intervals during wet weather.'
    },
    'Tomato_Spider_Mites': {
        'crop': 'Tomato',
        'display_name': 'Tomato Two-Spotted Spider Mite',
        'pathogen': 'Tetranychus urticae (Arachnid Pest)',
        'is_healthy': False,
        'symptoms': (
            'Fine yellow speckling, stippling, or chlorotic mottling across upper leaf surfaces. As the colony grows, '
            'delicate silk webbing coats leaf undersides and terminal shoots. Foliage turns bronzed, dry, and brittle, '
            'leading to rapid premature leaf drop under hot, arid conditions.'
        ),
        'precautions': (
            '1. Avoid excessive chemical nitrogen fertilization which accelerates mite reproduction rates.\n'
            '2. Overhead misting or increasing relative humidity disrupts mite egg laying and nymph feeding.\n'
            '3. Release predatory mites (Phytoseiulus persimilis or Neoseiulus californicus) early in the outbreak.'
        ),
        'organic_control': 'Horticultural neem oil spray (1.5-2%) or potassium salts of fatty acids (insecticidal soap) directed at leaf undersides.',
        'chemical_control': 'Spiromesifen 22.9 SC (1ml/L) or Abamectin 1.8 EC (0.5ml/L) with thorough underside canopy penetration.'
    },
    'Tomato_Target_Spot': {
        'crop': 'Tomato',
        'display_name': 'Tomato Target Spot',
        'pathogen': 'Corynespora cassiicola (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Pinpoint brown circular lesions that expand into target-like zones with brown centers and darker '
            'concentric rings. Distinguishable from early blight by smaller spot clusters and lesions on both foliage and green fruit.'
        ),
        'precautions': (
            '1. Improve row spacing and orient plantings parallel to prevailing daytime winds.\n'
            '2. Avoid weed hosts such as morning glory and wild solanums around field margins.'
        ),
        'organic_control': 'Copper octanoate bio-fungicide combined with Bacillus amyloliquefaciens.',
        'chemical_control': 'Azoxystrobin + Difenoconazole (Amistar Top 1ml/L) or Fluopyram + Tebuconazole.'
    },
    'Tomato_Tomato_Yellow_Leaf_Curl_Virus': {
        'crop': 'Tomato',
        'display_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'pathogen': 'Geminiviridae (Begomovirus) transmitted by Bemisia tabaci (Whitefly)',
        'is_healthy': False,
        'symptoms': (
            'Severe upward curling and cupping of leaflets, marked yellowing (chlorosis) along leaflet margins, '
            'leaf reduction (shoestringing), shortened internodes, and stunted bushy plant architecture. '
            'Flowers abort prematurely, preventing fruit set.'
        ),
        'precautions': (
            '1. Control whitefly populations using 50-mesh anti-insect netting in nurseries.\n'
            '2. Install yellow sticky traps (15-20 traps/acre) to monitor and intercept adult vectors.\n'
            '3. Rogue out and immediately bag infected plants to prevent field-wide vector acquisition.'
        ),
        'organic_control': 'Reflective silver polyethylene mulch to disorient whiteflies. Foliar spray of Beauveria bassiana bio-insecticide.',
        'chemical_control': 'Thiamethoxam 25 WG (0.3g/L) or Spirotetramat 150 OD (1ml/L) to suppress whitefly nymphs.'
    },
    'Tomato_Tomato_Mosaic_Virus': {
        'crop': 'Tomato',
        'display_name': 'Tomato Mosaic Virus (ToMV)',
        'pathogen': 'Tobamovirus (Mechanically transmitted)',
        'is_healthy': False,
        'symptoms': (
            'Alternating light green and dark green mosaic patterns on foliage. Leaflets may exhibit blistering, '
            'distortion, and severe fern-like narrowing ("strapping"). Fruit ripens unevenly with internal brown necrotic rings.'
        ),
        'precautions': (
            '1. Disinfect pruning shears, stakes, and hands with a 20% non-fat dry milk solution or 10% TSP.\n'
            '2. Strictly ban tobacco use near greenhouse and field facilities (tobacco transmits mosaic virions).\n'
            '3. Plant certified virus-free seed treated with trisodium phosphate.'
        ),
        'organic_control': 'No chemical cure exists for viral infections; isolate and destroy infected specimens immediately.',
        'chemical_control': 'Sanitize equipment with quaternary ammonium compounds or potassium peroxymonosulfate.'
    },
    'Tomato_Healthy': {
        'crop': 'Tomato',
        'display_name': 'Tomato — Healthy Foliage',
        'pathogen': 'None (Vibrant Plant)',
        'is_healthy': True,
        'symptoms': (
            'Leaves display rich deep-green chlorophyll coloration, firm turgor pressure, clean leaf margins, '
            'and no chlorosis, necrotic spotting, or pathogen sporulation. Vascular system and stems are robust and clear.'
        ),
        'precautions': (
            '1. Maintain balanced N-P-K fertilization with adequate calcium to prevent blossom end rot.\n'
            '2. Maintain steady soil moisture between 60-70% field capacity.\n'
            '3. Scout foliage weekly for early signs of vector insects or foliar micro-lesions.'
        ),
        'organic_control': 'Preventative foliar sprays of seaweed extract and compost tea to boost systemic acquired resistance (SAR).',
        'chemical_control': 'No corrective chemicals required. Continue standard preventative integrated pest management (IPM).'
    },
    'Potato_Early_Blight': {
        'crop': 'Potato',
        'display_name': 'Potato Early Blight',
        'pathogen': 'Alternaria solani (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Brownish-black circular spots with concentric rings confined by leaf veins, creating an angular appearance. '
            'Symptoms manifest first during tuber bulking on senescing lower leaves. Foliage turns yellow and dies.'
        ),
        'precautions': (
            '1. Maintain crop vigor with balanced nitrogen; nitrogen-deficient crops succumb much earlier.\n'
            '2. Harvest tubers only after skin set to avoid wound inoculations during digging.\n'
            '3. Rotate out of solanaceous crops for 3 consecutive seasons.'
        ),
        'organic_control': 'Copper sulfate pentahydrate or bio-agent sprays with Trichoderma viride.',
        'chemical_control': 'Chlorothalonil (2kg/ha) or Pyraclostrobin + Boscalid (Signet).'
    },
    'Potato_Late_Blight': {
        'crop': 'Potato',
        'display_name': 'Potato Late Blight',
        'pathogen': 'Phytophthora infestans (Oomycete)',
        'is_healthy': False,
        'symptoms': (
            'Water-soaked dark lesions spreading rapidly across foliage. In damp mornings, white mildew sporulation '
            'rings lesion edges on lower leaf surfaces. Stems show black lesions and tubers rot into a dry/wet reddish-brown granular decay.'
        ),
        'precautions': (
            '1. Destroy cull piles and volunteer potato sprouts before spring emergence.\n'
            '2. Spray fungicides preventively when late blight forecasting algorithms trigger risk alerts.\n'
            '3. Hill soil well over seed tubers (10-15 cm) to shield them from spores washed downward by rains.'
        ),
        'organic_control': 'Bordeaux mixture (1%) or copper octanoate applied before high-humidity weather.',
        'chemical_control': 'Cymoxanil + Mancozeb (Curzate 2g/L) or Mandipropamid (Revus 0.6ml/L).'
    },
    'Potato_Healthy': {
        'crop': 'Potato',
        'display_name': 'Potato — Healthy Foliage',
        'pathogen': 'None (Vibrant Plant)',
        'is_healthy': True,
        'symptoms': (
            'Vibrant green compound leaves, sturdy upright petioles, and healthy canopy expansion. '
            'Absence of water-soaked spots, concentric target rings, and aphid colonies.'
        ),
        'precautions': (
            '1. Monitor soil moisture carefully during flowering and tuber initiation.\n'
            '2. Ensure optimal potassium nutrition to support starch deposition in tubers.'
        ),
        'organic_control': 'Routine prophylactic bio-fungicide sprays (Trichoderma spp.) and beneficial soil inoculation.',
        'chemical_control': 'No corrective chemicals needed. Maintain standard crop monitoring.'
    },
    'Corn_Common_Rust': {
        'crop': 'Corn (Maize)',
        'display_name': 'Corn Common Rust',
        'pathogen': 'Puccinia sorghi (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Small, elongated cinnamon-brown to golden powdery pustules (uredinia) erupting on both upper and lower '
            'leaf surfaces. Ruptured epidermis scatters airborne rust spores. Severely affected leaves turn chlorotic, '
            'scorch, and senesce prematurely.'
        ),
        'precautions': (
            '1. Plant rust-resistant or tolerant corn hybrids with specific Rp resistance genes.\n'
            '2. Plant early in the season to evade mid-summer southerly storm spore showers.\n'
            '3. Scout upper canopy whorls before tassel emergence (VT stage).'
        ),
        'organic_control': 'Sulfur-based foliar dusts or bio-fungicide formulations containing Bacillus pumilus.',
        'chemical_control': 'Azoxystrobin + Propiconazole (Quilt Xcel 1.5ml/L) or Pyraclostrobin (Headline).'
    },
    'Corn_Northern_Leaf_Blight': {
        'crop': 'Corn (Maize)',
        'display_name': 'Corn Northern Leaf Blight (NCLB)',
        'pathogen': 'Exserohilum turcicum (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Long, elliptical, cigar-shaped grayish-green lesions (2.5 to 15 cm in length) with smooth margins. '
            'Under damp weather, lesions develop olive-gray fungal sporulation blankets, progressing from lower canopy upward.'
        ),
        'precautions': (
            '1. Select corn hybrids possessing Ht multigenic resistance.\n'
            '2. Manage crop residue with conservation tillage to accelerate stalk decomposition.\n'
            '3. Implement minimum 1-year non-host rotation (e.g., soybeans).'
        ),
        'organic_control': 'Copper octanoate foliar spray during early vegetative stages.',
        'chemical_control': 'Trifloxystrobin + Prothioconazole (Delaro) or Pyraclostrobin + Fluxapyroxad.'
    },
    'Corn_Gray_Leaf_Spot': {
        'crop': 'Corn (Maize)',
        'display_name': 'Corn Gray Leaf Spot (GLS)',
        'pathogen': 'Cercospora zeae-maydis (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Narrow, tan to gray rectangular lesions distinctly bounded by leaf veins ("blocky" appearance). '
            'Lesions coalesce under warm, humid conditions (25-30°C), blighting entire leaves and reducing ear fill.'
        ),
        'precautions': (
            '1. Practice crop rotation with soybeans, alfalfa, or small grains.\n'
            '2. Select hybrids with strong ratings against GLS.\n'
            '3. Avoid overhead irrigation during late afternoon.'
        ),
        'organic_control': 'Foliar sprays of potassium silicate and Bacillus subtilis.',
        'chemical_control': 'Propiconazole (Tilt 1ml/L) or Azoxystrobin (Amistar) at V6 to VT stages.'
    },
    'Corn_Healthy': {
        'crop': 'Corn (Maize)',
        'display_name': 'Corn (Maize) — Healthy Foliage',
        'pathogen': 'None (Vibrant Plant)',
        'is_healthy': True,
        'symptoms': (
            'Broad, deep-green linear leaves with clear parallel venation. Strong central midrib, '
            'free from pustules, streak lesions, or marginal scorch.'
        ),
        'precautions': (
            '1. Maintain nitrogen side-dressing during rapid vegetative stem elongation (V6-V8).\n'
            '2. Monitor soil moisture during critical silking and grain-filling windows.'
        ),
        'organic_control': 'Apply vesicular arbuscular mycorrhiza (VAM) to enhance phosphorus and moisture uptake.',
        'chemical_control': 'No chemical applications required.'
    },
    'Rice_Bacterial_Leaf_Blight': {
        'crop': 'Rice',
        'display_name': 'Rice Bacterial Leaf Blight (BLB)',
        'pathogen': 'Xanthomonas oryzae pv. oryzae (Bacterium)',
        'is_healthy': False,
        'symptoms': (
            'Water-soaked to yellowish-white wavy lesions starting at leaf tips and margins, progressing downwards. '
            'In early mornings, milky-amber bacterial ooze droplets form on leaf surfaces and dry into crusty beads. '
            'Leaves turn whitish-gray and roll inward ("kresek" wilt in seedlings).'
        ),
        'precautions': (
            '1. Avoid excessive nitrogen applications; split nitrogen into 3-4 split doses.\n'
            '2. Drain paddies temporarily when bacterial wilt symptoms first emerge.\n'
            '3. Plant resistant rice varieties carrying Xa4, xa5, or Xa21 genes.'
        ),
        'organic_control': 'Foliar spray of fresh cow dung slurry extract (20%) or Pseudomonas fluorescens (5g/L).',
        'chemical_control': 'Copper Hydroxide 77 WP (2g/L) combined with Streptomycin sulfate + Tetracycline (Plantomycin 0.5g/L).'
    },
    'Rice_Blast': {
        'crop': 'Rice',
        'display_name': 'Rice Blast',
        'pathogen': 'Magnaporthe oryzae / Pyricularia oryzae (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Characteristic spindle- or diamond-shaped lesions with gray-whitish centers and dark brown or reddish borders. '
            'Can infect leaf blades (leaf blast), culm nodes (node blast), and panicle necks (neck rot), causing '
            'complete lodging and white empty panicles.'
        ),
        'precautions': (
            '1. Maintain constant water level (2-5 cm) in paddies; water stress heavily predisposes plants to blast.\n'
            '2. Treat seeds with fungicides before nursery sowing.\n'
            '3. Avoid late transplanting and high seeding density.'
        ),
        'organic_control': 'Seed treatment and foliar application with Pseudomonas fluorescens (10g/kg seed; 5g/L water).',
        'chemical_control': 'Tricyclazole 75 WP (0.6g/L) or Isoprothiolane 40 EC (1.5ml/L) at heading stage.'
    },
    'Rice_Brown_Spot': {
        'crop': 'Rice',
        'display_name': 'Rice Brown Spot',
        'pathogen': 'Bipolaris oryzae (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Numerous circular to oval brown spots with distinct yellow or gold halo borders resembling sesame seeds. '
            'Coalescing spots cause large patches of foliar necrosis and discolored unfilled grains with dark blotches.'
        ),
        'precautions': (
            '1. Brown spot is a "poor man\'s disease" indicating nutritional deficiency (especially potassium and zinc) and drought.\n'
            '2. Apply balanced N-P-K along with Zinc Sulfate (25 kg/ha) and silicon amendments.\n'
            '3. Ensure uniform field leveling for consistent irrigation water depth.'
        ),
        'organic_control': 'Neem cake application to paddy soil combined with foliar bio-fertilizer sprays.',
        'chemical_control': 'Mancozeb 75 WP (2g/L) or Propiconazole 25 EC (1ml/L) at boot leaf emergence.'
    },
    'Rice_Healthy': {
        'crop': 'Rice',
        'display_name': 'Rice — Healthy Foliage',
        'pathogen': 'None (Vibrant Plant)',
        'is_healthy': True,
        'symptoms': (
            'Erect, vibrant green tillers and leaves with sharp, intact margins. Uniform canopy coloration '
            'without lesions, brown specks, or bacterial exudates.'
        ),
        'precautions': (
            '1. Maintain alternate wetting and moderate drying (AWD) water management to strengthen root aeration.\n'
            '2. Scout nursery and field borders regularly for planthopper and stem borer presence.'
        ),
        'organic_control': 'Bio-fertilizer Azospirillum and Phosphobacteria applications to sustain nutrient density.',
        'chemical_control': 'No corrective chemicals required.'
    },
    'Wheat_Yellow_Rust': {
        'crop': 'Wheat',
        'display_name': 'Wheat Stripe / Yellow Rust',
        'pathogen': 'Puccinia striiformis f. sp. tritici (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Bright yellow to orange-yellow powdery pustules (uredinia) arranged in distinct, continuous linear stripes '
            'parallel to leaf veins. Pustules rupture the leaf epidermis, depleting moisture and causing rapid leaf drying.'
        ),
        'precautions': (
            '1. Cultivate yellow rust resistant cultivars possessing adult plant resistance (APR) genes.\n'
            '2. Sow crop early within recommended planting windows.\n'
            '3. Scout low-lying or cold foggy field depressions during cool winters (10-15°C).'
        ),
        'organic_control': 'Sulfur wettable powder (3g/L) applied early in disease development.',
        'chemical_control': 'Tebuconazole 250 EC (1ml/L) or Propiconazole 25 EC (1ml/L) applied at first detection.'
    },
    'Wheat_Leaf_Rust': {
        'crop': 'Wheat',
        'display_name': 'Wheat Brown / Leaf Rust',
        'pathogen': 'Puccinia triticina (Fungus)',
        'is_healthy': False,
        'symptoms': (
            'Small, round to oval reddish-brown or rusty-orange pustules scattered randomly across the upper leaf surface '
            '(unlike the neat stripes of yellow rust). Heavy attacks destroy flag leaf photosynthetic capacity, '
            'severely shriveling grain kernels.'
        ),
        'precautions': (
            '1. Plant multi-gene rust resistant wheat varieties.\n'
            '2. Eliminate volunteer wheat grass along watercourses and bunds between seasons.'
        ),
        'organic_control': 'Bio-control application of Trichoderma viride and foliar silicon sprays.',
        'chemical_control': 'Azoxystrobin + Cyproconazole (Amistar Xtra) or Propiconazole (Tilt 1ml/L).'
    },
    'Wheat_Healthy': {
        'crop': 'Wheat',
        'display_name': 'Wheat — Healthy Foliage',
        'pathogen': 'None (Vibrant Plant)',
        'is_healthy': True,
        'symptoms': (
            'Rich dark-green linear blades, erect flag leaves, robust tillering structure, '
            'and no chlorosis, pustules, or powdery spore deposits.'
        ),
        'precautions': (
            '1. Ensure adequate zinc and nitrogen availability during tillering and jointing.\n'
            '2. Provide timely irrigation at crown root initiation (CRI) and grain milk stages.'
        ),
        'organic_control': 'Soil application of compost and bio-fertilizer consortium.',
        'chemical_control': 'No chemical intervention needed.'
    },
    'Healthy': {
        'crop': 'General Crop',
        'display_name': 'Healthy Crop Foliage',
        'pathogen': 'None (Optimal Plant Health)',
        'is_healthy': True,
        'symptoms': (
            'Foliage displays optimal chlorophyll pigmentation, intact epidermal cuticle, crisp leaf margins, '
            'and active cellular turgor. Zero signs of fungal sporulation, viral distortion, bacterial ooze, or pest stippling.'
        ),
        'precautions': (
            '1. Maintain current balanced agronomic management, drip irrigation schedule, and nutrient cycling.\n'
            '2. Continue weekly visual foliage scouting and record environmental telemetry trends.\n'
            '3. Keep field margins weed-free to prevent harboring insect vectors.'
        ),
        'organic_control': 'Prophylactic seaweed biostimulant or compost tea foliar spray to fortify natural plant defenses.',
        'chemical_control': 'No treatment required. Plant is robust and in prime condition.'
    }
}


def get_disease_info(disease_key: str) -> dict:
    """
    Look up disease information from the agronomic knowledge base.
    Handles exact matches, normalized underscore/space matches, and healthy fallbacks.
    """
    if not disease_key:
        return DISEASE_DATABASE['Healthy']

    # 1. Exact match
    if disease_key in DISEASE_DATABASE:
        return DISEASE_DATABASE[disease_key]

    # 2. Normalized match (e.g. "Tomato Early Blight" -> "Tomato_Early_Blight")
    normalized_key = disease_key.strip().replace(' ', '_')
    if normalized_key in DISEASE_DATABASE:
        return DISEASE_DATABASE[normalized_key]

    # 3. Case-insensitive lookup
    for k, v in DISEASE_DATABASE.items():
        if k.lower() == normalized_key.lower():
            return v
        if v['display_name'].lower() == disease_key.lower():
            return v

    # 4. Check for 'healthy' in key
    if 'healthy' in disease_key.lower():
        # Check if crop specific healthy exists
        for k in DISEASE_DATABASE:
            if 'healthy' in k.lower():
                crop_prefix = disease_key.split('_')[0].split(' ')[0].capitalize()
                if crop_prefix in k:
                    return DISEASE_DATABASE[k]
        return DISEASE_DATABASE['Healthy']

    # 5. Default fallback
    return {
        'crop': disease_key.split('_')[0] if '_' in disease_key else 'Unknown',
        'display_name': disease_key.replace('_', ' '),
        'pathogen': 'Unclassified Agronomic Pathogen',
        'is_healthy': False,
        'symptoms': 'Pathology symptoms have been detected. Inspect foliage closely for spotting, lesions, or wilting.',
        'precautions': 'Consult with local agronomic extension agents. Isolate suspected plant and avoid overhead watering.',
        'organic_control': 'Apply broad-spectrum bio-fungicide (Trichoderma or Bacillus subtilis).',
        'chemical_control': 'Apply protective broad-spectrum fungicide (e.g. Mancozeb or Copper Oxychloride).'
    }

