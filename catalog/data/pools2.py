
# Categories 11-20 (appended to CATEGORIES in pools.py)
from .pools import CATEGORIES, COLORS_APPAREL, COLORS_ELECTRONICS, COLORS_HOME, SIZES_APPAREL, SIZES_SHOES  # noqa

CATEGORIES.extend([
    ("Shoes", "Footwear for all occasions", [
        ("Running Shoes", [
            ("Road Running Shoes", ["StrideX", "PacePro"], (1499, 8999),
             ["Sole", "Upper", "Cushioning"],
             {"color": COLORS_APPAREL, "size": SIZES_SHOES}, (0.25, 0.4),
             "30-day Replacement"),
        ]),
        ("Sneakers", [
            ("Casual Sneakers", ["StreetKick", "UrbanSole"], (999, 5999),
             ["Upper", "Sole", "Closure"],
             {"color": COLORS_APPAREL, "size": SIZES_SHOES}, (0.3, 0.45),
             "30-day Replacement"),
        ]),
        ("Formal Shoes", [
            ("Oxford Shoes", ["ClassicStep", "Boardroom"], (1999, 8999),
             ["Material", "Sole", "Style"],
             {"color": ["Black", "Brown", "Tan"], "size": SIZES_SHOES}, (0.4, 0.6),
             "30-day Replacement"),
        ]),
        ("Sandals", [
            ("Comfort Sandals", ["BreezeWalk", "SoftStep"], (499, 2999),
             ["Sole", "Straps", "Footbed"],
             {"color": COLORS_APPAREL, "size": SIZES_SHOES}, (0.2, 0.35),
             "30-day Replacement"),
        ]),
    ]),
    ("Watches", "Wrist watches and timepieces", [
        ("Analog Watches", [
            ("Analog Watch", ["HeritageTime", "ClassicDial"], (1499, 24999),
             ["Movement", "Strap", "Water Resistance", "Dial"],
             {"color": ["Black", "Brown", "Silver", "Gold"]}, (0.06, 0.12),
             "2 Year Warranty"),
        ]),
        ("Chronographs", [
            ("Chronograph Watch", ["ChronoCraft", "TimerPro"], (3999, 49999),
             ["Movement", "Subdials", "Strap"],
             {"color": ["Black", "Silver", "Blue"]}, (0.08, 0.15),
             "2 Year Warranty"),
        ]),
    ]),
    ("Beauty & Personal Care", "Beauty, skincare and grooming", [
        ("Skincare", [
            ("Face Moisturizer", ["GlowDerma", "SkinMend"], (199, 1499),
             ["Skin Type", "Volume", "Key Ingredients"],
             {"size": ["50ml", "100ml"]}, (0.08, 0.15),
             "7-day Replacement"),
            ("Face Wash", ["ClearGlow", "PureFace"], (149, 799),
             ["Skin Type", "Volume"],
             {"size": ["100ml", "150ml", "200ml"]}, (0.12, 0.25),
             "7-day Replacement"),
        ]),
        ("Haircare", [
            ("Hair Shampoo", ["SilkStrand", "RootRevive"], (149, 899),
             ["Hair Type", "Volume", "Sulfate Free"],
             {"size": ["200ml", "340ml", "650ml"]}, (0.25, 0.7),
             "7-day Replacement"),
        ]),
        ("Fragrances", [
            ("Eau De Parfum", ["EssenceNoir", "CitrusVeil"], (499, 3999),
             ["Volume", "Notes", "Longevity"],
             {"size": ["50ml", "100ml"]}, (0.1, 0.2),
             "7-day Replacement"),
        ]),
        ("Grooming", [
            ("Electric Trimmer", ["SharpEdge", "GroomPro"], (899, 3999),
             ["Blades", "Battery", "Attachments"],
             {"color": ["Black"]}, (0.15, 0.25),
             "1 Year Warranty"),
        ]),
    ]),
    ("Grocery", "Everyday grocery and staples", [
        ("Staples", [
            ("Basmati Rice", ["GrainHarvest", "PaddyPure"], (299, 1499),
             ["Weight", "Grain Length", "Type"],
             {"size": ["1kg", "5kg", "10kg"]}, (1.0, 10.0),
             "Non-returnable"),
            ("Whole Wheat Flour", ["MillFresh", "ChakkiGold"], (199, 899),
             ["Weight", "Type"],
             {"size": ["1kg", "5kg", "10kg"]}, (1.0, 10.0),
             "Non-returnable"),
        ]),
        ("Snacks", [
            ("Potato Chips", ["CrunchFarm", "ChipChop"], (20, 199),
             ["Weight", "Flavour"],
             {"size": ["40g", "90g", "150g"]}, (0.05, 0.18),
             "Non-returnable"),
        ]),
        ("Beverages", [
            ("Instant Coffee", ["BrewBean", "CafeInstant"], (149, 899),
             ["Weight", "Type"],
             {"size": ["50g", "100g", "200g"]}, (0.08, 0.25),
             "Non-returnable"),
        ]),
        ("Spices", [
            ("Turmeric Powder", ["SpiceRoute", "HaldiPure"], (49, 399),
             ["Weight", "Ground"],
             {"size": ["100g", "200g", "500g"]}, (0.12, 0.55),
             "Non-returnable"),
        ]),
    ]),
    ("Health & Wellness", "Health supplements and devices", [
        ("Supplements", [
            ("Whey Protein", ["MuscleFuel", "ProGain"], (999, 4999),
             ["Weight", "Flavour", "Protein/Serving"],
             {"size": ["500g", "1kg", "2kg"], "color": ["Chocolate", "Vanilla", "Unflavoured"]}, (0.55, 2.2),
             "Non-returnable"),
            ("Multivitamin", ["VitaDaily", "NutriPlus"], (299, 1499),
             ["Count", "Type"],
             {"size": ["30 tabs", "60 tabs"]}, (0.05, 0.12),
             "Non-returnable"),
        ]),
        ("Medical Devices", [
            ("Digital Thermometer", ["TempCheck"], (199, 999),
             ["Type", "Accuracy", "Display"],
             {"color": ["White"]}, (0.05, 0.1),
             "1 Year Warranty"),
            ("BP Monitor", ["PressureTrack"], (1499, 4999),
             ["Type", "Cuff Size", "Memory"],
             {"color": ["White", "Grey"]}, (0.4, 0.6),
             "1 Year Warranty"),
        ]),
    ]),
    ("Sports & Fitness", "Sports gear and fitness equipment", [
        ("Strength", [
            ("Dumbbell Set", ["IronGrip", "PowerBell"], (899, 7999),
             ["Weight", "Material", "Grip"],
             {"size": ["5kg", "10kg", "15kg", "20kg"]}, (5.0, 20.0),
             "6 Month Warranty"),
        ]),
        ("Yoga", [
            ("Yoga Mat", ["ZenFlow", "FlexMat"], (399, 2499),
             ["Thickness", "Material", "Length"],
             {"color": COLORS_APPAREL, "size": ["4mm", "6mm", "8mm"]}, (0.8, 1.5),
             "30-day Replacement"),
        ]),
        ("Cycling", [
            ("Mountain Bike", ["TrailBlaze", "RidgeRide"], (8999, 49999),
             ["Frame", "Gears", "Wheel Size"],
             {"size": ['26"', '27.5"', '29"'], "color": ["Black", "Red", "Blue"]}, (13.0, 17.0),
             "1 Year Frame Warranty"),
        ]),
        ("Cricket", [
            ("Cricket Bat", ["WillowStrike", "CenturyHit"], (999, 8999),
             ["Willow", "Weight", "Handle"],
             {"size": ["SH", "LH", "Harrow"]}, (1.1, 1.3),
             "30-day Replacement"),
        ]),
    ]),
    ("Toys & Games", "Toys for kids and families", [
        ("Action Figures", [
            ("Action Figure", ["HeroVerse", "TinyLegends"], (299, 2499),
             ["Height", "Material", "Articulation"],
             {"color": ["Multicolor"]}, (0.15, 0.4),
             "7-day Replacement"),
        ]),
        ("Board Games", [
            ("Strategy Board Game", ["MindMaze", "EmpireBuild"], (499, 2999),
             ["Players", "Age", "Duration"],
             {"color": ["Multicolor"]}, (0.5, 1.5),
             "7-day Replacement"),
        ]),
        ("Building Blocks", [
            ("Building Set", ["BlockCraft", "ConstructKid"], (599, 4999),
             ["Pieces", "Age", "Theme"],
             {"size": ["250 pcs", "500 pcs", "1000 pcs"]}, (0.6, 2.0),
             "7-day Replacement"),
        ]),
        ("RC Toys", [
            ("RC Car", ["TurboWheel", "DriftKing"], (999, 7999),
             ["Scale", "Battery", "Range"],
             {"color": ["Red", "Blue", "Black"]}, (0.5, 1.2),
             "6 Month Warranty"),
        ]),
    ]),
    ("Books", "Books across genres", [
        ("Fiction", [
            ("Mystery Novel", ["InkQuill Press"], (199, 899),
             ["Pages", "Language", "Binding"],
             {"size": ["Paperback", "Hardcover"]}, (0.25, 0.6),
             "7-day Replacement"),
        ]),
        ("Non-Fiction", [
            ("Self-Help Book", ["MindScape Books"], (199, 999),
             ["Pages", "Language", "Binding"],
             {"size": ["Paperback", "Hardcover"]}, (0.25, 0.6),
             "7-day Replacement"),
        ]),
        ("Academic", [
            ("Exam Guide", ["ScholarPath"], (299, 1499),
             ["Pages", "Edition", "Subject"],
             {"color": [None]}, (0.4, 1.0),
             "7-day Replacement"),
        ]),
        ("Comics", [
            ("Graphic Novel", ["PanelVerse"], (299, 1499),
             ["Pages", "Age", "Volume"],
             {"color": ["Multicolor"]}, (0.3, 0.7),
             "7-day Replacement"),
        ]),
    ]),
    ("Baby Products", "Care for babies and toddlers", [
        ("Diapers", [
            ("Baby Diapers", ["SoftBottom", "DryNest"], (299, 1499),
             ["Count", "Size", "Type"],
             {"size": ["S-42", "M-36", "L-30", "XL-26"]}, (0.8, 2.5),
             "Non-returnable"),
        ]),
        ("Feeding", [
            ("Feeding Bottle", ["MilkMate", "SipSafe"], (199, 899),
             ["Capacity", "Material", "Nipple Flow"],
             {"size": ["125ml", "250ml"], "color": ["Blue", "Pink", "Clear"]}, (0.1, 0.2),
             "7-day Replacement"),
        ]),
        ("Strollers", [
            ("Baby Stroller", ["GlideTot", "StrollEase"], (3999, 19999),
             ["Weight Capacity", "Fold", "Wheels"],
             {"color": ["Grey", "Black", "Blue"]}, (6.0, 10.0),
             "1 Year Warranty"),
        ]),
    ]),
    ("Automotive", "Car and bike accessories", [
        ("Car Accessories", [
            ("Car Phone Mount", ["DriveGrip"], (299, 1499),
             ["Mount Type", "Compatibility"],
             {"color": ["Black"]}, (0.15, 0.3),
             "6 Month Warranty"),
            ("Car Vacuum Cleaner", ["AutoDust"], (999, 3999),
             ["Power", "Cord Length", "Attachments"],
             {"color": ["Black", "Red"]}, (0.8, 1.5),
             "1 Year Warranty"),
        ]),
        ("Bike Accessories", [
            ("Riding Gloves", ["ThrottleGrip"], (499, 2999),
             ["Material", "Protection", "Size"],
             {"color": ["Black"], "size": ["M", "L", "XL"]}, (0.15, 0.3),
             "30-day Replacement"),
        ]),
        ("Car Care", [
            ("Car Shampoo", ["ShineAuto"], (199, 899),
             ["Volume", "pH Neutral"],
             {"size": ["500ml", "1L"]}, (0.55, 1.1),
             "7-day Replacement"),
        ]),
    ]),
])
