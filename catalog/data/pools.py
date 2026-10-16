"""Original/synthetic data pools for catalogue generation.

Every brand name, product name and description here is FICTIONAL and generated
for development/testing. No real marketplace data is copied.
"""
import random

# ---------- Fictional brand generator (500+ unique) ----------
_BRAND_PRE = [
    "Volt", "Nexa", "Zyro", "Kyno", "Brav", "Lumi", "Oro", "Pix",
    "Quant", "Rivo", "Sola", "Tera", "Urba", "Viva", "Wex", "Xeno",
    "Yara", "Zola", "Aero", "Blu", "Crest", "Dyna", "Echo", "Flux",
    "Glint", "Halo", "Ion", "Jolt", "Kite", "Loom", "Mira", "Nimbus",
    "Onyx", "Prism", "Quill", "Ridge", "Strata", "Tide", "Umbra", "Verve",
]
_BRAND_SUF = [
    "Core", "Tech", "Labs", "Works", "Line", "Craft", "Mode", "Pure",
    "Prime", "Edge", "Wave", "Forge", "Nest", "Point", "Studio", "Gear",
    "House", "Mark", "Lane", "Field",
]


def build_brands(n=520, seed=42):
    rng = random.Random(seed)
    names = set()
    # combinatoric fictional brands
    for pre in _BRAND_PRE:
        for suf in _BRAND_SUF:
            names.add(f"{pre}{suf}")
            if len(names) >= n:
                break
        if len(names) >= n:
            break
    names = sorted(names)[:n]
    return [{"name": nm, "description": f"Original development brand {nm}."} for nm in names]


# ---------- Shared pools ----------
COLORS_APPAREL = ["Black", "White", "Navy", "Red", "Green", "Grey", "Beige", "Maroon", "Olive", "Mustard"]
COLORS_ELECTRONICS = ["Black", "Silver", "Blue", "White", "Graphite", "Purple"]
COLORS_HOME = ["Brown", "Beige", "Grey", "White", "Walnut", "Black"]
SIZES_APPAREL = ["S", "M", "L", "XL", "XXL"]
SIZES_SHOES = ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11"]

MATERIALS = {
    "apparel": ["Cotton", "Polyester", "Cotton Blend", "Linen", "Denim"],
    "furniture": ["Engineered Wood", "Solid Sheesham Wood", "Metal", "Fabric", "Leatherette"],
    "kitchen": ["Stainless Steel", "Plastic", "Glass", "Aluminium"],
}

SPEC_VALUES = {
    "Display": ["6.1-inch HD+", "6.5-inch FHD+ AMOLED", "6.7-inch QHD+ 120Hz", "5.9-inch FHD+"],
    "Chipset": ["Octa-core 2.4GHz", "Octa-core 3.0GHz", "Hexa-core 2.8GHz"],
    "RAM": ["4GB", "6GB", "8GB", "12GB"],
    "Storage": ["64GB", "128GB", "256GB", "512GB"],
    "Rear Camera": ["50MP Dual", "64MP Triple", "108MP Triple", "12MP Dual"],
    "Battery": ["4000mAh", "5000mAh", "6000mAh"],
    "Processor": ["Intel Core i5 13th Gen", "Intel Core i7 13th Gen", "AMD Ryzen 5 7530U", "AMD Ryzen 7 7730U", "Apple M2"],
    "Screen Size": ['13.3-inch', '14-inch', '15.6-inch', '16-inch'],
    "Fabric": ["100% Cotton", "Cotton-Poly Blend", "Linen", "Denim 12oz"],
    "Capacity": ["1L", "1.5L", "1.8L", "2L", "5L"],
    "Power": ["750W", "1000W", "1500W", "2000W"],
}

# Archetype tuple:
# (product_type, model_lines, price_range, spec_names, variant_axes, weight_range, warranty)
# Categories 1-10
CATEGORIES = [
    ("Electronics", "Electronic devices and gadgets", [
        ("Smartphones", [
            ("5G Smartphone", ["AeroPhone", "NovaX", "Cirrus"], (8999, 79999),
             ["Display", "Chipset", "RAM", "Storage", "Rear Camera", "Battery"],
             {"storage": ["128GB", "256GB"], "color": COLORS_ELECTRONICS}, (0.16, 0.24),
             "1 Year Manufacturer Warranty"),
            ("4G Smartphone", ["TerraGo", "VoltLite"], (5999, 15999),
             ["Display", "Chipset", "RAM", "Storage", "Battery"],
             {"storage": ["64GB", "128GB"], "color": COLORS_ELECTRONICS}, (0.17, 0.22),
             "1 Year Manufacturer Warranty"),
        ]),
        ("Tablets", [
            ("WiFi Tablet", ["SlatePro", "TabEdge"], (9999, 45999),
             ["Display", "Chipset", "RAM", "Storage", "Battery"],
             {"storage": ["64GB", "128GB"], "color": COLORS_ELECTRONICS}, (0.45, 0.65),
             "1 Year Manufacturer Warranty"),
        ]),
        ("Headphones", [
            ("Wireless Headphones", ["SonicArc", "BassCrest"], (1499, 12999),
             ["Driver", "Battery", "Bluetooth", "Noise Cancellation"],
             {"color": COLORS_ELECTRONICS}, (0.2, 0.35),
             "1 Year Manufacturer Warranty"),
            ("True Wireless Earbuds", ["AirPulse", "DotBeat"], (999, 7999),
             ["Driver", "Battery", "Bluetooth", "Charging Case"],
             {"color": COLORS_ELECTRONICS}, (0.05, 0.08),
             "1 Year Manufacturer Warranty"),
        ]),
        ("Smartwatches", [
            ("Smartwatch", ["PulseFit", "ChronoX"], (1999, 19999),
             ["Display", "Battery", "Sensors", "Water Resistance"],
             {"color": COLORS_ELECTRONICS, "size": ["42mm", "46mm"]}, (0.04, 0.07),
             "1 Year Manufacturer Warranty"),
        ]),
        ("Cameras", [
            ("Mirrorless Camera", ["LumoShot", "OptiCam"], (34999, 129999),
             ["Sensor", "Lens Mount", "Video", "ISO Range"],
             {"color": ["Black"]}, (0.4, 0.7),
             "2 Year Manufacturer Warranty"),
        ]),
        ("Drones", [
            ("Camera Drone", ["SkyHawk", "AeroGlide"], (14999, 89999),
             ["Camera", "Flight Time", "Range", "Gimbal"],
             {"color": ["Grey", "Black"]}, (0.5, 0.9),
             "1 Year Manufacturer Warranty"),
        ]),
    ]),
    ("Mobiles & Accessories", "Mobile accessories and add-ons", [
        ("Phone Cases", [
            ("Back Cover", ["ShieldCase", "ArmorShell"], (199, 1499),
             ["Material", "Compatibility", "Protection"],
             {"color": COLORS_ELECTRONICS, "size": ["6.1 inch", "6.5 inch", "6.7 inch"]}, (0.03, 0.06),
             "7-day Replacement"),
        ]),
        ("Chargers & Cables", [
            ("Fast Charger", ["VoltBoost", "RapidCharge"], (399, 2499),
             ["Power", "Ports", "Compatibility"],
             {"color": ["White", "Black"]}, (0.08, 0.15),
             "6 Month Warranty"),
            ("USB Cable", ["LinkWire", "FlexCord"], (149, 899),
             ["Length", "Connector", "Speed"],
             {"color": ["White", "Black"], "size": ["1m", "1.5m", "2m"]}, (0.03, 0.06),
             "6 Month Warranty"),
        ]),
        ("Power Banks", [
            ("Power Bank", ["JuiceBox", "VoltPack"], (899, 3999),
             ["Capacity", "Ports", "Fast Charging"],
             {"color": COLORS_ELECTRONICS}, (0.2, 0.35),
             "6 Month Warranty"),
        ]),
        ("Screen Protectors", [
            ("Tempered Glass", ["ClearGuard"], (99, 599),
             ["Thickness", "Compatibility", "Hardness"],
             {"size": ["6.1 inch", "6.5 inch", "6.7 inch"]}, (0.01, 0.02),
             "7-day Replacement"),
        ]),
    ]),
    ("Computers & Laptops", "Computing devices and peripherals", [
        ("Laptops", [
            ("Thin & Light Laptop", ["BookAir", "SlimPro"], (34999, 129999),
             ["Processor", "RAM", "Storage", "Screen Size", "Battery"],
             {"storage": ["512GB SSD", "1TB SSD"], "color": ["Silver", "Grey", "Black"]}, (1.2, 1.8),
             "1 Year Onsite Warranty"),
            ("Gaming Laptop", ["StrikeForce", "NitroPlay"], (59999, 199999),
             ["Processor", "RAM", "Storage", "GPU", "Screen Size"],
             {"storage": ["512GB SSD", "1TB SSD"], "color": ["Black"]}, (2.0, 2.8),
             "1 Year Onsite Warranty"),
        ]),
        ("Monitors", [
            ("Office Monitor", ["ViewPanel", "ClearView"], (7999, 29999),
             ["Screen Size", "Resolution", "Refresh Rate", "Panel"],
             {"size": ['22-inch', '24-inch', '27-inch'], "color": ["Black"]}, (3.0, 5.5),
             "3 Year Warranty"),
        ]),
        ("Keyboards", [
            ("Mechanical Keyboard", ["KeyForge", "TypePro"], (1499, 8999),
             ["Switch Type", "Backlight", "Connectivity"],
             {"color": ["Black", "White"]}, (0.7, 1.2),
             "1 Year Warranty"),
        ]),
        ("Mice", [
            ("Wireless Mouse", ["GlidePoint", "SwiftClick"], (499, 3499),
             ["DPI", "Connectivity", "Battery"],
             {"color": ["Black", "White", "Grey"]}, (0.08, 0.12),
             "1 Year Warranty"),
        ]),
        ("Storage", [
            ("External SSD", ["DataVault", "SwiftStore"], (2999, 24999),
             ["Capacity", "Interface", "Speed"],
             {"storage": ["500GB", "1TB", "2TB"]}, (0.05, 0.1),
             "3 Year Warranty"),
        ]),
    ]),
    ("TVs & Home Entertainment", "Television and home theatre", [
        ("Smart TVs", [
            ("4K Smart TV", ["VisionMax", "CineView"], (24999, 149999),
             ["Screen Size", "Resolution", "OS", "Sound"],
             {"size": ['43-inch', '50-inch', '55-inch', '65-inch'], "color": ["Black"]}, (8.0, 25.0),
             "1 Year Comprehensive + 1 Year Panel Warranty"),
        ]),
        ("Soundbars", [
            ("Soundbar", ["BassBoom", "CinemaBar"], (3999, 24999),
             ["Channels", "Power", "Connectivity", "Subwoofer"],
             {"color": ["Black"]}, (2.5, 6.0),
             "1 Year Warranty"),
        ]),
        ("Streaming Devices", [
            ("Streaming Stick", ["StreamPlug"], (1499, 5999),
             ["Resolution", "Voice Remote", "Apps"],
             {"color": ["Black"]}, (0.05, 0.1),
             "1 Year Warranty"),
        ]),
        ("Projectors", [
            ("Home Projector", ["CineBeam", "LumoCast"], (12999, 59999),
             ["Resolution", "Brightness", "Throw"],
             {"color": ["White", "Black"]}, (1.5, 3.0),
             "1 Year Warranty"),
        ]),
    ]),
    ("Home Appliances", "Large home appliances", [
        ("Refrigerators", [
            ("Double Door Refrigerator", ["FrostFree", "CoolNest"], (24999, 89999),
             ["Capacity", "Energy Rating", "Compressor"],
             {"size": ["260L", "320L", "400L"], "color": ["Silver", "Black"]}, (55.0, 85.0),
             "1 Year Product + 10 Year Compressor Warranty"),
        ]),
        ("Washing Machines", [
            ("Front Load Washer", ["WashPro", "AquaClean"], (22999, 69999),
             ["Capacity", "RPM", "Programs"],
             {"size": ["7kg", "8kg", "9kg"], "color": ["White", "Silver"]}, (60.0, 75.0),
             "2 Year Product + 10 Year Motor Warranty"),
        ]),
        ("Air Conditioners", [
            ("Split AC", ["CoolBreeze", "ArcticAir"], (27999, 69999),
             ["Capacity", "Energy Rating", "Refrigerant"],
             {"size": ["1 Ton", "1.5 Ton", "2 Ton"], "color": ["White"]}, (35.0, 50.0),
             "1 Year Product + 5 Year Compressor Warranty"),
        ]),
        ("Air Purifiers", [
            ("Air Purifier", ["PureAir", "BreatheEasy"], (6999, 29999),
             ["CADR", "Filters", "Room Size"],
             {"color": ["White"]}, (5.0, 9.0),
             "1 Year Warranty"),
        ]),
        ("Vacuum Cleaners", [
            ("Robot Vacuum", ["DustBot", "CleanSweep"], (14999, 49999),
             ["Suction", "Battery", "Navigation"],
             {"color": ["Black", "White"]}, (3.0, 4.5),
             "1 Year Warranty"),
        ]),
    ]),
    ("Kitchen Appliances", "Kitchen helpers and cookware tech", [
        ("Mixer Grinders", [
            ("Mixer Grinder", ["GrindMaster", "MixPro"], (2499, 9999),
             ["Power", "Jars", "Speed Settings"],
             {"color": ["White", "Black", "Red"]}, (3.5, 5.5),
             "2 Year Warranty"),
        ]),
        ("Air Fryers", [
            ("Air Fryer", ["CrispAir", "FryLite"], (4999, 15999),
             ["Capacity", "Power", "Presets"],
             {"color": ["Black"]}, (4.0, 6.5),
             "1 Year Warranty"),
        ]),
        ("Microwave Ovens", [
            ("Convection Microwave", ["HeatWave", "CookPro"], (8999, 24999),
             ["Capacity", "Power", "Auto Cook Menus"],
             {"size": ["28L", "32L"], "color": ["Black", "Silver"]}, (12.0, 18.0),
             "1 Year Warranty"),
        ]),
        ("Coffee Makers", [
            ("Drip Coffee Maker", ["BrewBuddy", "CafePress"], (1999, 9999),
             ["Capacity", "Power", "Carafe"],
             {"color": ["Black", "Silver"]}, (1.5, 2.5),
             "1 Year Warranty"),
        ]),
        ("Electric Kettles", [
            ("Electric Kettle", ["BoilFast", "KettlePro"], (899, 3499),
             ["Capacity", "Power", "Auto Shut-off"],
             {"color": ["Black", "White", "Steel"]}, (0.9, 1.4),
             "1 Year Warranty"),
        ]),
    ]),
    ("Home & Furniture", "Furniture and home decor", [
        ("Sofas", [
            ("3-Seater Sofa", ["ComfortNest", "LoungePro"], (14999, 59999),
             ["Seating", "Fabric", "Frame"],
             {"color": COLORS_HOME}, (25.0, 45.0),
             "1 Year Warranty"),
        ]),
        ("Beds", [
            ("Queen Bed", ["SleepWell", "DreamRest"], (12999, 49999),
             ["Size", "Material", "Storage"],
             {"color": COLORS_HOME, "size": ["Queen", "King"]}, (40.0, 70.0),
             "1 Year Warranty"),
        ]),
        ("Office Chairs", [
            ("Ergonomic Chair", ["ErgoSit", "WorkEase"], (4999, 24999),
             ["Material", "Adjustments", "Weight Capacity"],
             {"color": ["Black", "Grey"]}, (12.0, 20.0),
             "1 Year Warranty"),
        ]),
        ("Lighting", [
            ("Table Lamp", ["GlowNest", "LumoDesk"], (799, 4999),
             ["Bulb Type", "Material", "Switch"],
             {"color": COLORS_HOME}, (0.8, 2.0),
             "6 Month Warranty"),
        ]),
    ]),
    ("Fashion - Men", "Men's apparel", [
        ("T-Shirts", [
            ("Cotton T-Shirt", ["EssentialTee", "UrbanCrew"], (299, 1499),
             ["Fabric", "Fit", "Neck"],
             {"color": COLORS_APPAREL, "size": SIZES_APPAREL}, (0.15, 0.25),
             "7-day Replacement"),
        ]),
        ("Shirts", [
            ("Casual Shirt", ["OxfordWeave", "LinenLook"], (599, 2499),
             ["Fabric", "Fit", "Sleeve"],
             {"color": COLORS_APPAREL, "size": SIZES_APPAREL}, (0.2, 0.3),
             "7-day Replacement"),
        ]),
        ("Jeans", [
            ("Slim Fit Jeans", ["DenimCraft", "IndigoRow"], (899, 3499),
             ["Fabric", "Fit", "Rise"],
             {"color": ["Blue", "Black", "Grey"], "size": ["30", "32", "34", "36"]}, (0.5, 0.7),
             "7-day Replacement"),
        ]),
        ("Jackets", [
            ("Winter Jacket", ["NorthPeak", "FrostLine"], (1499, 5999),
             ["Material", "Insulation", "Pockets"],
             {"color": ["Black", "Navy", "Olive"], "size": SIZES_APPAREL}, (0.8, 1.4),
             "7-day Replacement"),
        ]),
    ]),
    ("Fashion - Women", "Women's apparel", [
        ("Dresses", [
            ("Summer Dress", ["FloraBelle", "TwirlDress"], (699, 2999),
             ["Fabric", "Length", "Neckline"],
             {"color": COLORS_APPAREL, "size": SIZES_APPAREL}, (0.25, 0.4),
             "7-day Replacement"),
        ]),
        ("Sarees", [
            ("Silk Saree", ["KanchiWeave", "BanarasiLoom"], (1499, 9999),
             ["Fabric", "Border", "Blouse Piece"],
             {"color": COLORS_APPAREL}, (0.5, 0.9),
             "7-day Replacement"),
        ]),
        ("Kurtis", [
            ("Cotton Kurti", ["EthnicGrace", "KurtiKraft"], (499, 2499),
             ["Fabric", "Length", "Sleeve"],
             {"color": COLORS_APPAREL, "size": SIZES_APPAREL}, (0.2, 0.35),
             "7-day Replacement"),
        ]),
        ("Tops", [
            ("Casual Top", ["BreezeTop", "ChicWear"], (399, 1999),
             ["Fabric", "Fit", "Sleeve"],
             {"color": COLORS_APPAREL, "size": SIZES_APPAREL}, (0.15, 0.25),
             "7-day Replacement"),
        ]),
    ]),
    ("Fashion - Kids", "Kids' apparel", [
        ("Kids T-Shirts", [
            ("Kids Graphic Tee", ["JuniorPop", "TinyToon"], (199, 899),
             ["Fabric", "Print", "Fit"],
             {"color": COLORS_APPAREL, "size": ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]}, (0.1, 0.18),
             "7-day Replacement"),
        ]),
        ("Kids Dresses", [
            ("Party Frock", ["TwinkleTot", "FairyFrock"], (499, 2499),
             ["Fabric", "Length", "Occasion"],
             {"color": ["Pink", "Red", "Blue", "Yellow"], "size": ["2-3Y", "4-5Y", "6-7Y"]}, (0.2, 0.35),
             "7-day Replacement"),
        ]),
    ]),
]
