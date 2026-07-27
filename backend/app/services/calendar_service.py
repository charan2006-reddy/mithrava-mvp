"""Crop calendar service.

Provides crop-specific stage timelines for major Indian crops, calculates
the current growth stage based on sowing date, and returns personalised
weekly tasks and daily priority actions for the farmer dashboard.

Supported crops: Tomato, Onion, Rice (Paddy), Wheat, Maize, Cotton,
Sugarcane, and Groundnut.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class CropStage:
    """A single growth stage in a crop's lifecycle."""

    name: str
    week_start: int
    week_end: int
    tasks: list[str] = field(default_factory=list)
    priority: str = "medium"  # high | medium | low
    advice: str = ""


@dataclass
class CropTimeline:
    """Full lifecycle definition for a crop."""

    crop_name: str
    total_weeks: int
    stages: list[CropStage] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Crop-specific stage database
# ---------------------------------------------------------------------------

CROP_TIMELINES: dict[str, CropTimeline] = {
    # ── Tomato ────────────────────────────────────────────────────────────
    "tomato": CropTimeline(
        crop_name="Tomato",
        total_weeks=16,
        stages=[
            CropStage(
                name="Land Preparation",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Plough the field 2-3 times to a fine tilth",
                    "Apply FYM (Farm Yard Manure) 20 tonnes/acre",
                    "Apply basal fertilizer: DAP 100 kg/acre + MOP 50 kg/acre",
                    "Prepare raised beds 15 cm high, 1 metre wide",
                ],
                advice=(
                    "Prepare the land well before sowing. Mix organic manure "
                    "thoroughly into the soil. Good preparation leads to better yields."
                ),
            ),
            CropStage(
                name="Nursery & Transplanting",
                week_start=3,
                week_end=4,
                priority="high",
                tasks=[
                    "Transplant seedlings when 4-6 true leaves appear",
                    "Maintain plant spacing of 60 cm x 45 cm",
                    "Water immediately after transplanting",
                    "Apply Trichoderma root dip before planting",
                ],
                advice=(
                    "Handle seedling roots carefully during transplanting. "
                    "Water in the evening to reduce transplant shock."
                ),
            ),
            CropStage(
                name="Vegetative Growth",
                week_start=5,
                week_end=8,
                priority="medium",
                tasks=[
                    "Apply Urea 50 kg/acre at week 5 for vegetative boost",
                    "Spray neem oil (5 ml/L) for pest control every 10 days",
                    "Install support stakes at week 6",
                    "Earthing up around the base of plants",
                    "Weed the field and maintain clean rows",
                ],
                advice=(
                    "Focus on strong leaf and stem growth. Regular pest "
                    "monitoring is crucial — look for leaf curl and whitefly."
                ),
            ),
            CropStage(
                name="Flowering & Fruit Set",
                week_start=9,
                week_end=12,
                priority="high",
                tasks=[
                    "Apply Potash (MOP) 40 kg/acre for fruit quality",
                    "Spray Boron (0.2%) to improve fruit set",
                    "Avoid heavy irrigation during flowering",
                    "Monitor for fruit borer — install pheromone traps",
                    "Maintain consistent moisture, do not let soil dry out completely",
                ],
                advice=(
                    "Flowering is the most critical stage. Avoid overhead "
                    "watering. If fruit set is poor, gently shake plants "
                    "to aid pollination."
                ),
            ),
            CropStage(
                name="Fruit Development & Ripening",
                week_start=13,
                week_end=14,
                priority="medium",
                tasks=[
                    "Reduce irrigation frequency as fruits mature",
                    "Apply Calcium spray to prevent blossom end rot",
                    "Monitor for late blight — spray Metalaxyl if needed",
                    "Begin harvesting first ripe fruits at colour break",
                ],
                advice=(
                    "Fruits are gaining colour and weight. Reduce watering "
                    "to concentrate flavours. Pick at the 'breaker' stage "
                    "for market transport."
                ),
            ),
            CropStage(
                name="Harvest & Post-Harvest",
                week_start=15,
                week_end=16,
                priority="high",
                tasks=[
                    "Harvest all remaining fruits at breaker or red stage",
                    "Handle carefully to avoid bruising",
                    "Sort and grade by size and colour",
                    "Store at 12-15°C for longer shelf life",
                ],
                advice=(
                    "Harvest in the morning when fruits are cool. Avoid "
                    "dropping or stacking heavy. Proper grading fetches "
                    "better mandi prices."
                ),
            ),
        ],
    ),

    # ── Onion ─────────────────────────────────────────────────────────────
    "onion": CropTimeline(
        crop_name="Onion",
        total_weeks=14,
        stages=[
            CropStage(
                name="Land Preparation & Sowing",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Deep plough the field and add FYM 15 tonnes/acre",
                    "Apply DAP 80 kg/acre as basal dose",
                    "Sow seeds in raised beds or transplant seedlings",
                    "Ensure proper drainage — onions hate waterlogging",
                ],
                advice=(
                    "Onions need well-drained, loose soil. Raised beds "
                    "are recommended. Sow during the cool part of the season."
                ),
            ),
            CropStage(
                name="Seedling Establishment",
                week_start=3,
                week_end=5,
                priority="medium",
                tasks=[
                    "Thin seedlings to 10 cm spacing at week 3",
                    "First light irrigation immediately after sowing",
                    "Apply Urea 30 kg/acre at week 4 for early growth",
                    "Weed carefully — shallow weeding only to protect roots",
                ],
                advice=(
                    "Keep the field moist but not wet. Do not allow "
                    "weed competition in the first month."
                ),
            ),
            CropStage(
                name="Bulb Formation",
                week_start=6,
                week_end=9,
                priority="high",
                tasks=[
                    "Apply Potash (MOP) 40 kg/acre for bulb size",
                    "Irrigate every 5-7 days during bulb development",
                    "Spray Sulphur (0.4%) to prevent thrips",
                    "Monitor for purple blotch — remove infected leaves",
                    "Earthing up around bulbs as they develop",
                ],
                advice=(
                    "This is the most important stage for bulb size. "
                    "Consistent moisture and nutrition directly affect yield."
                ),
            ),
            CropStage(
                name="Maturity & Curing",
                week_start=10,
                week_end=12,
                priority="medium",
                tasks=[
                    "Stop irrigation when 50% of onion tops fall over",
                    "Reduce watering gradually over 2 weeks",
                    "Apply final Potash spray for storage quality",
                    "Monitor neck rot — ensure good airflow",
                ],
                advice=(
                    "When the onion tops start falling over naturally, "
                    "stop watering. This triggers the curing process "
                    "needed for good storage life."
                ),
            ),
            CropStage(
                name="Harvest & Storage",
                week_start=13,
                week_end=14,
                priority="high",
                tasks=[
                    "Harvest when 60-70% tops have fallen over",
                    "Lift bulbs carefully with a fork, avoid cuts",
                    "Cure in the field for 3-5 sunny days",
                    "Store in a well-ventilated, dry place",
                ],
                advice=(
                    "Harvest when onion tops fall over completely. Dry "
                    "thoroughly before storage — moisture causes rot. "
                    "Good curing extends shelf life to 3-6 months."
                ),
            ),
        ],
    ),

    # ── Rice (Paddy) ──────────────────────────────────────────────────────
    "rice": CropTimeline(
        crop_name="Rice (Paddy)",
        total_weeks=20,
        stages=[
            CropStage(
                name="Nursery & Land Preparation",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Soak seeds for 24 hours, then pre-germinate in moist cloth",
                    "Prepare nursery bed — 1 cm water level maintained",
                    "Plough main field 2-3 times, puddle the soil",
                    "Apply basal dose: DAP 100 kg/acre + Zinc Sulphate 25 kg/acre",
                ],
                advice=(
                    "Start the nursery 20-25 days before transplanting. "
                    "Use certified, high-yielding种子 like Samba Mahsuri "
                    "or BPT-5204."
                ),
            ),
            CropStage(
                name="Transplanting",
                week_start=3,
                week_end=4,
                priority="high",
                tasks=[
                    "Transplant 20-25 day old seedlings at 3-4 per hill",
                    "Maintain 5 cm water level in the field",
                    "Space rows 20 cm x 15 cm for optimal growth",
                    "Apply Urea 30 kg/acre 7 days after transplanting",
                ],
                advice=(
                    "Transplant in the evening or on cloudy days. Keep "
                    "a thin layer of standing water — this is the key "
                    "to weed control in rice."
                ),
            ),
            CropStage(
                name="Vegetative Growth",
                week_start=5,
                week_end=10,
                priority="medium",
                tasks=[
                    "Maintain 5 cm water level consistently",
                    "Apply Urea 50 kg/acre at week 6 (tillering dose)",
                    "Control weeds — apply pre-emergence herbicide if needed",
                    "Monitor for stem borer — install light traps",
                    "Drain the field briefly at week 8, then re-flood",
                ],
                advice=(
                    "Rice needs constant water. Never let the field dry "
                    "out completely during vegetative growth. Nitrogen "
                    "at this stage determines the number of tillers."
                ),
            ),
            CropStage(
                name="Reproductive Stage",
                week_start=11,
                week_end=14,
                priority="high",
                tasks=[
                    "Maintain 5-7 cm water depth during flowering",
                    "Apply Potash (MOP) 30 kg/acre at booting stage",
                    "Watch for bacterial leaf blight — drain and spray",
                    "Control leaf folder with Chlorantraniliprole if needed",
                    "Avoid water stress during panicle initiation",
                ],
                advice=(
                    "Flowering rice is very sensitive to water shortage. "
                    "Keep good water depth. Any stress now will reduce "
                    "grains per panicle significantly."
                ),
            ),
            CropStage(
                name="Grain Filling",
                week_start=15,
                week_end=17,
                priority="medium",
                tasks=[
                    "Reduce water level gradually from week 15",
                    "Apply Potash spray (2% KCl) for grain weight",
                    "Monitor for sheath blight in humid conditions",
                    "Stop irrigation 7-10 days before expected harvest",
                ],
                advice=(
                    "Grains are filling up. Slowly reduce water to allow "
                    "the crop to mature. Draining too early reduces grain "
                    "weight; too late delays harvest."
                ),
            ),
            CropStage(
                name="Harvest & Post-Harvest",
                week_start=18,
                week_end=20,
                priority="high",
                tasks=[
                    "Harvest when 80% of panicles turn golden yellow",
                    "Cut at 15 cm height, stack in stooks to dry",
                    "Thresh after 3-4 days of sun drying",
                    "Dry grain to 14% moisture for safe storage",
                ],
                advice=(
                    "Timing the harvest is critical. Too early means "
                    "chalky grains; too late means shattering losses. "
                    "Harvest in the morning, dry well before storage."
                ),
            ),
        ],
    ),

    # ── Wheat ─────────────────────────────────────────────────────────────
    "wheat": CropTimeline(
        crop_name="Wheat",
        total_weeks=16,
        stages=[
            CropStage(
                name="Land Preparation & Sowing",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Prepare fine seedbed with 2-3 ploughings",
                    "Apply FYM 8-10 tonnes/acre",
                    "Sow seeds at 22-25 cm row spacing, 5 cm depth",
                    "Apply basal fertilizer: DAP 130 kg/acre + MOP 30 kg/acre",
                ],
                advice=(
                    "Sow in mid-November for Rabi wheat. Use certified "
                    "seed like HD-3226, WB-02, or WH-1270. Timely sowing "
                    "is the single biggest yield factor."
                ),
            ),
            CropStage(
                name="Germination & Crown Root",
                week_start=3,
                week_end=4,
                priority="medium",
                tasks=[
                    "First irrigation (Crown Root Initiation) at 20-25 DAS",
                    "Light hoeing to control weeds",
                    "Apply Urea 40 kg/acre at first irrigation",
                    "Watch for termite damage — apply Chlorpyriphos if needed",
                ],
                advice=(
                    "The first irrigation at Crown Root Initiation stage "
                    "is the most critical. Do not delay it — it sets "
                    "the root system for the whole season."
                ),
            ),
            CropStage(
                name="Vegetative Growth",
                week_start=5,
                week_end=8,
                priority="medium",
                tasks=[
                    "Second irrigation at tillering stage (40-45 DAS)",
                    "Apply Urea 40 kg/acre for tiller development",
                    "Weed the field — apply weedicide or manual weeding",
                    "Third irrigation at late jointing (60 DAS)",
                    "Monitor for rust — spray Propiconazole if detected",
                ],
                advice=(
                    "Manage weeds in the first 40 days — they cause the "
                    "most damage early. Keep an eye on leaf rust, "
                    "especially if neighbours have yellowing wheat."
                ),
            ),
            CropStage(
                name="Flowering & Grain Filling",
                week_start=9,
                week_end=12,
                priority="high",
                tasks=[
                    "Fourth irrigation at heading stage (75-80 DAS)",
                    "Fifth irrigation at milk stage (100 DAS)",
                    "Apply Potash (MOP) 20 kg/acre at heading",
                    "Spray Sulphur (0.2%) to improve grain protein",
                    "Monitor for powdery mildew and aphids",
                ],
                advice=(
                    "Irrigations at heading and milk stage determine "
                    "grain weight. Skipping even one irrigation here "
                    "can reduce yield by 15-20%."
                ),
            ),
            CropStage(
                name="Maturation & Harvest",
                week_start=13,
                week_end=16,
                priority="high",
                tasks=[
                    "Sixth (last) irrigation at dough stage (110 DAS)",
                    "Stop all irrigation 15-20 days before harvest",
                    "Harvest when grain is hard and golden (25% moisture)",
                    "Thresh and dry to 12% moisture for storage",
                    "Clean and grade grain for best mandi prices",
                ],
                advice=(
                    "Harvest at the right time — too early means shriveled "
                    "grains, too late means shattering losses. Use a "
                    "combine or sickle depending on your field size."
                ),
            ),
        ],
    ),

    # ── Maize ─────────────────────────────────────────────────────────────
    "maize": CropTimeline(
        crop_name="Maize",
        total_weeks=14,
        stages=[
            CropStage(
                name="Land Preparation & Sowing",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Plough the field 2 times and level properly",
                    "Apply FYM 10 tonnes/acre before last ploughing",
                    "Sow seeds at 60 cm row spacing, 5 cm depth",
                    "Apply DAP 120 kg/acre + MOP 40 kg/acre as basal",
                    "Treat seeds with Carbofuran 3G for stem borer protection",
                ],
                advice=(
                    "Maize needs well-drained loamy soil. Sow during "
                    "Kharif (June-July) or Rabi (January-February). "
                    "Use hybrid seeds for best results."
                ),
            ),
            CropStage(
                name="Germination & Early Growth",
                week_start=3,
                week_end=4,
                priority="medium",
                tasks=[
                    "Thinning to maintain one strong plant per hill at 15 cm",
                    "First irrigation at 10-15 days after sowing",
                    "Apply Urea 50 kg/acre at knee-high stage",
                    "Earthing up around the base for root support",
                ],
                advice=(
                    "Thin seedlings early — overcrowding leads to weak "
                    "plants and poor yields. One strong plant per hill "
                    "is better than three weak ones."
                ),
            ),
            CropStage(
                name="Vegetative Growth",
                week_start=5,
                week_end=8,
                priority="medium",
                tasks=[
                    "Second irrigation at 30-35 DAS",
                    "Apply Urea 50 kg/acre at tasseling initiation",
                    "Weed between rows at 25 and 45 DAS",
                    "Monitor for fall armyworm — spray Emamectin benzoate",
                    "Check for stem borer damage in the stalks",
                ],
                advice=(
                    "Maize grows fast during this phase. Weed control "
                    "is essential — the crop cannot compete with weeds "
                    "for nutrients and light."
                ),
            ),
            CropStage(
                name="Tasseling & Silking",
                week_start=9,
                week_end=11,
                priority="high",
                tasks=[
                    "Critical irrigation at tasseling — do not miss this",
                    "Apply Potash (MOP) 30 kg/acre at flowering",
                    "Spray Boron (0.2%) to improve kernel set",
                    "Avoid any water stress during pollination",
                    "Monitor for earworm — apply Chlorantraniliprole",
                ],
                advice=(
                    "Tasseling and silking is the most water-critical "
                    "period. Even 2-3 days of water stress can cause "
                    "bare tips on cobs. Irrigate immediately."
                ),
            ),
            CropStage(
                name="Grain Filling & Harvest",
                week_start=12,
                week_end=14,
                priority="high",
                tasks=[
                    "One final irrigation at milk stage if needed",
                    "Stop irrigation when husks start turning brown",
                    "Harvest when kernels are hard and nails are black",
                    "Dry cobs in the sun for 3-4 days",
                    "Shell and dry grain to 14% moisture",
                ],
                advice=(
                    "Harvest when the husk is dry and brown, and kernels "
                    "are hard when pressed with a fingernail. Dry "
                    "thoroughly before storage to prevent fungal growth."
                ),
            ),
        ],
    ),

    # ── Cotton ────────────────────────────────────────────────────────────
    "cotton": CropTimeline(
        crop_name="Cotton",
        total_weeks=24,
        stages=[
            CropStage(
                name="Land Preparation & Sowing",
                week_start=1,
                week_end=2,
                priority="high",
                tasks=[
                    "Deep ploughing followed by 2 cross ploughings",
                    "Apply FYM 12 tonnes/acre and mix well",
                    "Sow BT cotton seeds at 90 cm x 60 cm spacing",
                    "Apply DAP 100 kg/acre + MOP 50 kg/acre as basal",
                    "Treat seeds with Thiamethoxam for early pest protection",
                ],
                advice=(
                    "Cotton needs deep, well-drained soil. Use BT hybrid "
                    "seeds (e.g., RCH-134, JKCH-1947). Sow after the "
                    "first good monsoon rain."
                ),
            ),
            CropStage(
                name="Establishment & Early Vegetative",
                week_start=3,
                week_end=6,
                priority="medium",
                tasks=[
                    "Thinning to one strong plant per hill at 15 DAS",
                    "First irrigation at 15-20 DAS if no rain",
                    "Apply Urea 40 kg/acre at 25 DAS",
                    "First weeding at 20 DAS, second at 40 DAS",
                    "Monitor for sucking pests (aphids, jassids, whitefly)",
                ],
                advice=(
                    "Early pest management sets the tone for the season. "
                    "Install yellow sticky traps for whitefly monitoring. "
                    "Do not spray unnecessarily — use IPM approach."
                ),
            ),
            CropStage(
                name="Vegetative Growth",
                week_start=7,
                week_end=12,
                priority="medium",
                tasks=[
                    "Apply Urea 60 kg/acre at 45 DAS for branching",
                    "Irrigate every 10-12 days during dry spells",
                    "Monitor for pink bollworm — use pheromone traps",
                    "Install bird perches (25/acre) for natural pest control",
                    "Top-dress with Potash 40 kg/acre at 75 DAS",
                ],
                advice=(
                    "Cotton is a long-season crop. Patience with pest "
                    "management and balanced nutrition is key. Avoid "
                    "excess nitrogen — it attracts sucking pests."
                ),
            ),
            CropStage(
                name="Flowering & Boll Formation",
                week_start=13,
                week_end=18,
                priority="high",
                tasks=[
                    "Maintain consistent moisture — irrigate every 7-10 days",
                    "Apply Potash (MOP) 30 kg/acre at peak flowering",
                    "Spray mepiquat chloride if plants are too tall",
                    "Intensive monitoring for bollworm — check 10 plants weekly",
                    "If bollworm damage exceeds threshold, spray Emamectin benzoate",
                ],
                advice=(
                    "Bollworm is the biggest threat during this stage. "
                    "Scout regularly — check flowers, squares, and small "
                    "bolls. Act quickly when damage crosses 10%."
                ),
            ),
            CropStage(
                name="Boll Maturity",
                week_start=19,
                week_end=22,
                priority="medium",
                tasks=[
                    "Reduce irrigation frequency as bolls mature",
                    "Continue monitoring for late-season whitefly",
                    "Apply final Potash spray for fibre quality",
                    "Defoliate if needed using Thidiazuron spray",
                    "Prepare for first picking when bolls open",
                ],
                advice=(
                    "Cotton bolls are maturing and opening. Reduce "
                    "irrigation to help bolls open properly. First "
                    "picking should only be of fully open, clean bolls."
                ),
            ),
            CropStage(
                name="Picking",
                week_start=23,
                week_end=23,
                priority="high",
                tasks=[
                    "First picking — collect fully opened, white bolls only",
                    "Second picking after 10-14 days for remaining bolls",
                    "Keep picked cotton clean — no leaves or twigs",
                    "Dry cotton in sun before selling at ginning factory",
                ],
                advice=(
                    "Quality matters more than quantity. Only pick clean, "
                    "white, fully opened bolls. Mixed and dirty cotton "
                    "fetches lower prices at the ginning factory."
                ),
            ),
            CropStage(
                name="Post-Harvest",
                week_start=24,
                week_end=24,
                priority="low",
                tasks=[
                    "Uproot and destroy cotton stalks after final picking",
                    "Shred and incorporate stalks to prevent pest carryover",
                    "Plan next crop rotation — avoid cotton on same land",
                    "Clean and store picking bags for next season",
                ],
                advice=(
                    "Destroying cotton stalks is legally mandatory in many "
                    "states. It breaks the pink bollworm cycle. Rotate "
                    "with a non-host crop like wheat or pulses."
                ),
            ),
        ],
    ),
}

# Lower-cased aliases for flexible crop name matching
_CROP_ALIASES: dict[str, str] = {
    "tomato": "tomato",
    "tamatar": "tomato",
    "onion": "onion",
    "pyaaz": "onion",
    "pyaj": "onion",
    "rice": "rice",
    "paddy": "rice",
    "dhan": "rice",
    "rice paddy": "rice",
    "wheat": "wheat",
    "gehu": "wheat",
    "maize": "maize",
    "corn": "maize",
    "makka": "maize",
    "makki": "maize",
    "cotton": "cotton",
    "kapas": "cotton",
    "sugarcane": "sugarcane",
    "ganna": "sugarcane",
    "groundnut": "groundnut",
    "moongfali": "groundnut",
    "peanut": "groundnut",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_crop_key(name: str) -> Optional[str]:
    """Resolve a user-supplied crop name to a canonical timeline key.

    Performs case-insensitive lookup with common Indian-language aliases.

    Args:
        name: Crop name as entered by the farmer.

    Returns:
        Canonical key (e.g. "tomato") or ``None`` if not found.
    """
    normalised = name.strip().lower()
    return _CROP_ALIASES.get(normalised)


def get_crop_timeline(crop_name: str) -> Optional[CropTimeline]:
    """Fetch the full lifecycle definition for a crop.

    Args:
        crop_name: Crop name (fuzzy-matched against the database).

    Returns:
        ``CropTimeline`` if the crop is supported, ``None`` otherwise.
    """
    key = resolve_crop_key(crop_name)
    if key is None:
        return None
    return CROP_TIMELINES.get(key)


def calculate_current_stage(
    sowing_date: date,
    today: Optional[date] = None,
) -> tuple[Optional[CropStage], int, int]:
    """Determine the current growth stage for a crop given its sowing date.

    Args:
        sowing_date: The date the crop was planted / sowed.
        today: Reference date (defaults to ``date.today()``).

    Returns:
        A tuple of ``(current_stage, week_number, days_since_sowing)``.
        ``current_stage`` is ``None`` if the crop is beyond its lifecycle.
    """
    if today is None:
        today = date.today()

    days = (today - sowing_date).days
    if days < 0:
        # Crop not yet sowed (future date)
        return None, 0, 0

    week_number = (days // 7) + 1  # 1-indexed
    return None, week_number, days


def get_stage_for_week(
    timeline: CropTimeline, week_number: int
) -> Optional[CropStage]:
    """Find the growth stage that contains the given week number.

    Args:
        timeline: The full crop lifecycle.
        week_number: Current week (1-indexed).

    Returns:
        The matching ``CropStage`` or ``None`` if beyond all stages.
    """
    for stage in timeline.stages:
        if stage.week_start <= week_number <= stage.week_end:
            return stage
    return None


def get_next_action(
    timeline: CropTimeline, week_number: int
) -> Optional[str]:
    """Return the first high-priority task from the current or next stage.

    Args:
        timeline: The full crop lifecycle.
        week_number: Current week (1-indexed).

    Returns:
        A human-readable action string, or ``None`` if lifecycle is complete.
    """
    stage = get_stage_for_week(timeline, week_number)
    if stage and stage.tasks:
        # Return the first task of the current stage as the next action
        return stage.tasks[0]

    # If past all stages, suggest harvest
    if week_number > timeline.total_weeks:
        return "Crop lifecycle complete — ensure proper post-harvest storage"

    return None


def build_calendar_items(
    crop_id: str,
    crop_name: str,
    sowing_date: Optional[date],
    today: Optional[date] = None,
) -> Optional[dict]:
    """Build a full calendar item dict for a single crop.

    Args:
        crop_id: Unique identifier of the crop.
        crop_name: Name of the crop.
        sowing_date: Date the crop was sowed.
        today: Reference date (defaults to ``date.today()``).

    Returns:
        A dict suitable for ``CropCalendarItem``, or ``None`` if the crop
        is not supported or has no sowing date.
    """
    if today is None:
        today = date.today()

    if sowing_date is None:
        return None

    timeline = get_crop_timeline(crop_name)
    if timeline is None:
        return None

    days = (today - sowing_date).days
    if days < 0:
        return None

    week_number = (days // 7) + 1
    stage = get_stage_for_week(timeline, week_number)

    if stage is None:
        # Beyond all defined stages
        return {
            "crop_id": crop_id,
            "crop_name": crop_name,
            "stage": "Harvest Complete",
            "week_number": week_number,
            "tasks": ["Plan post-harvest activities and next crop"],
            "advice": "This crop has completed its lifecycle. Consider crop rotation.",
            "priority": "low",
        }

    return {
        "crop_id": crop_id,
        "crop_name": crop_name,
        "stage": stage.name,
        "week_number": week_number,
        "tasks": stage.tasks,
        "advice": stage.advice,
        "priority": stage.priority,
    }


def build_daily_actions(
    crop_id: str,
    crop_name: str,
    sowing_date: Optional[date],
    today: Optional[date] = None,
) -> list[dict]:
    """Build daily priority actions for a single crop.

    Returns a list of action dicts. High-priority stages return the first
    2 tasks; medium and low return only 1.

    Args:
        crop_id: Unique identifier of the crop.
        crop_name: Name of the crop.
        sowing_date: Date the crop was sowed.
        today: Reference date (defaults to ``date.today()``).

    Returns:
        List of action dicts suitable for ``DailyAction``.
    """
    if today is None:
        today = date.today()

    if sowing_date is None:
        return []

    timeline = get_crop_timeline(crop_name)
    if timeline is None:
        return []

    days = (today - sowing_date).days
    if days < 0:
        return []

    week_number = (days // 7) + 1
    stage = get_stage_for_week(timeline, week_number)
    if stage is None:
        return []

    # Map stage names to icon and category
    icon_map: dict[str, tuple[str, str]] = {
        "Land Preparation": ("🚜", "preparation"),
        "Land Preparation & Sowing": ("🚜", "preparation"),
        "Nursery & Transplanting": ("🌱", "preparation"),
        "Nursery & Land Preparation": ("🌱", "preparation"),
        "Transplanting": ("🌾", "preparation"),
        "Seedling Establishment": ("💧", "irrigation"),
        "Germination & Early Growth": ("💧", "irrigation"),
        "Germination & Crown Root": ("💧", "irrigation"),
        "Establishment & Early Vegetative": ("🌱", "preparation"),
        "Vegetative Growth": ("🌿", "fertilizer"),
        "Vegetative Growth & Tillering": ("🌿", "fertilizer"),
        "Flowering & Fruit Set": ("🌸", "pest"),
        "Flowering & Boll Formation": ("🌸", "pest"),
        "Flowering & Grain Filling": ("🌾", "fertilizer"),
        "Reproductive Stage": ("🌾", "fertilizer"),
        "Fruit Development & Ripening": ("🍅", "harvest"),
        "Boll Maturity": ("☁️", "harvest"),
        "Harvest & Post-Harvest": ("🌾", "harvest"),
        "Harvest & Storage": ("🌾", "harvest"),
        "Picking": ("☁️", "harvest"),
        "Post-Harvest": ("📦", "harvest"),
        "Maturation & Harvest": ("🌾", "harvest"),
        "Maturity & Curing": ("🧅", "harvest"),
        "Grain Filling": ("🌾", "fertilizer"),
        "Tasseling & Silking": ("🌽", "irrigation"),
    }

    icon, category = icon_map.get(stage.name, ("🌱", "preparation"))

    # Determine how many tasks to surface as actions
    task_count = 2 if stage.priority == "high" else 1
    actions: list[dict] = []
    for task in stage.tasks[:task_count]:
        actions.append({
            "crop_id": crop_id,
            "crop_name": crop_name,
            "action": task,
            "priority": stage.priority,
            "icon": icon,
            "category": category,
        })

    return actions


def build_crop_detail(
    crop_id: str,
    crop_name: str,
    sowing_date: Optional[date],
    today: Optional[date] = None,
) -> dict:
    """Build extended crop detail with calendar stage information.

    Args:
        crop_id: Unique identifier of the crop.
        crop_name: Name of the crop.
        sowing_date: Date the crop was sowed.
        today: Reference date (defaults to ``date.today()``).

    Returns:
        Dict with ``current_stage``, ``days_since_sowing``,
        ``week_number``, and ``next_action`` keys.
    """
    if today is None:
        today = date.today()

    result: dict = {
        "current_stage": None,
        "days_since_sowing": None,
        "week_number": None,
        "next_action": None,
    }

    if sowing_date is None:
        return result

    days = (today - sowing_date).days
    if days < 0:
        return result

    week_number = (days // 7) + 1
    result["days_since_sowing"] = days
    result["week_number"] = week_number

    timeline = get_crop_timeline(crop_name)
    if timeline is None:
        return result

    stage = get_stage_for_week(timeline, week_number)
    if stage:
        result["current_stage"] = stage.name
    else:
        result["current_stage"] = "Harvest Complete"

    result["next_action"] = get_next_action(timeline, week_number)
    return result
