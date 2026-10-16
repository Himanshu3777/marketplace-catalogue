
# Categories 21-30 (appended to CATEGORIES)
from .pools import CATEGORIES, COLORS_APPAREL, COLORS_ELECTRONICS, COLORS_HOME, SIZES_APPAREL  # noqa

CATEGORIES.extend([
    ("Pet Supplies", "Food and care for pets", [
        ("Dog Food", [
            ("Dry Dog Food", ["PawNutri", "BarkBite"], (399, 2999),
             ["Weight", "Flavour", "Life Stage"],
             {"size": ["1kg", "3kg", "10kg"], "color": ["Chicken", "Lamb", "Veg"]}, (1.1, 10.5),
             "Non-returnable"),
        ]),
        ("Cat Food", [
            ("Dry Cat Food", ["WhiskerMeal", "PurrPlate"], (349, 2499),
             ["Weight", "Flavour"],
             {"size": ["1kg", "3kg", "7kg"]}, (1.1, 7.5),
             "Non-returnable"),
        ]),
        ("Pet Toys", [
            ("Chew Toy", ["ChewChamp"], (149, 899),
             ["Material", "Size"],
             {"color": ["Red", "Blue", "Green"], "size": ["S", "M", "L"]}, (0.1, 0.3),
             "7-day Replacement"),
        ]),
        ("Aquariums", [
            ("Fish Tank", ["AquaWorld"], (1499, 14999),
             ["Capacity", "Material", "Filter"],
             {"size": ["20L", "40L", "80L"]}, (4.0, 15.0),
             "6 Month Warranty"),
        ]),
    ]),
    ("Office Products", "Office and workspace essentials", [
        ("Notebooks", [
            ("Spiral Notebook", ["WriteWell", "PaperTrail"], (99, 599),
             ["Pages", "Size", "Ruling"],
             {"size": ["A5", "A4"], "color": ["Blue", "Black", "Red"]}, (0.2, 0.5),
             "7-day Replacement"),
        ]),
        ("Pens", [
            ("Ball Pen Set", ["InkFlow", "SmoothWrite"], (49, 499),
             ["Count", "Tip", "Ink"],
             {"size": ["Pack of 5", "Pack of 10"], "color": ["Blue", "Black"]}, (0.05, 0.15),
             "7-day Replacement"),
        ]),
        ("Organizers", [
            ("Desk Organizer", ["DeskTidy", "WorkSort"], (299, 1999),
             ["Material", "Compartments"],
             {"color": ["Black", "White", "Wood"]}, (0.4, 1.2),
             "30-day Replacement"),
        ]),
    ]),
    ("Bags & Luggage", "Bags, backpacks and luggage", [
        ("Backpacks", [
            ("Laptop Backpack", ["TrekPack", "CarryAll"], (899, 4999),
             ["Capacity", "Laptop Size", "Water Resistant"],
             {"color": COLORS_APPAREL, "size": ["25L", "32L", "45L"]}, (0.6, 1.2),
             "1 Year Warranty"),
        ]),
        ("Suitcases", [
            ("Hard Suitcase", ["GlobeTrot", "VoyagePro"], (2499, 14999),
             ["Size", "Material", "Wheels"],
             {"color": ["Black", "Blue", "Red"], "size": ['20"', '24"', '28"']}, (2.5, 4.5),
             "3 Year Warranty"),
        ]),
        ("Duffel Bags", [
            ("Travel Duffel", ["WeekendGo"], (799, 3999),
             ["Capacity", "Material"],
             {"color": COLORS_APPAREL, "size": ["40L", "60L"]}, (0.7, 1.3),
             "1 Year Warranty"),
        ]),
    ]),
    ("Jewellery", "Fashion and fine jewellery", [
        ("Necklaces", [
            ("Pendant Necklace", ["GleamCraft", "AuraJewels"], (499, 19999),
             ["Material", "Plating", "Chain Length"],
             {"color": ["Gold", "Silver", "Rose Gold"]}, (0.02, 0.08),
             "6 Month Warranty"),
        ]),
        ("Earrings", [
            ("Stud Earrings", ["SparkPair"], (299, 9999),
             ["Material", "Stone"],
             {"color": ["Gold", "Silver"]}, (0.01, 0.03),
             "6 Month Warranty"),
        ]),
        ("Rings", [
            ("Fashion Ring", ["BandBloom"], (399, 12999),
             ["Material", "Size"],
             {"color": ["Gold", "Silver"], "size": ["12", "14", "16", "18"]}, (0.01, 0.03),
             "6 Month Warranty"),
        ]),
    ]),
    ("Garden & Outdoor", "Gardening and outdoor living", [
        ("Plants", [
            ("Indoor Plant", ["GreenNest"], (199, 1499),
             ["Type", "Pot Included"],
             {"color": ["Green"]}, (0.5, 3.0),
             "7-day Replacement"),
        ]),
        ("Gardening Tools", [
            ("Tool Set", ["GrowGear"], (499, 2999),
             ["Pieces", "Material"],
             {"size": ["5 pc", "9 pc"]}, (0.8, 2.0),
             "6 Month Warranty"),
        ]),
        ("Camping", [
            ("Camping Tent", ["CampWild", "TrailNest"], (1999, 14999),
             ["Capacity", "Season", "Poles"],
             {"size": ["2 Person", "4 Person", "6 Person"], "color": ["Green", "Orange", "Blue"]}, (2.5, 7.0),
             "1 Year Warranty"),
        ]),
    ]),
    ("Tools & Hardware", "Power tools and hand tools", [
        ("Power Tools", [
            ("Cordless Drill", ["TorquePro", "DrillMaster"], (2499, 14999),
             ["Voltage", "Chuck", "Battery"],
             {"color": ["Yellow", "Red", "Blue"]}, (1.2, 2.5),
             "1 Year Warranty"),
        ]),
        ("Hand Tools", [
            ("Tool Kit", ["FixItAll"], (899, 5999),
             ["Pieces", "Case"],
             {"size": ["46 pc", "108 pc"]}, (2.0, 5.0),
             "6 Month Warranty"),
        ]),
        ("Safety Gear", [
            ("Safety Gloves", ["GuardHand"], (149, 899),
             ["Material", "Size"],
             {"color": ["Yellow", "Black"], "size": ["M", "L", "XL"]}, (0.1, 0.25),
             "30-day Replacement"),
        ]),
    ]),
    ("Musical Instruments", "Instruments for learners and pros", [
        ("Guitars", [
            ("Acoustic Guitar", ["StrumCraft", "MelodyWood"], (2999, 29999),
             ["Size", "Strings", "Wood"],
             {"color": ["Natural", "Black", "Sunburst"], "size": ['38"', '41"']}, (1.8, 2.8),
             "1 Year Warranty"),
        ]),
        ("Keyboards", [
            ("Digital Piano", ["KeyHarmony"], (8999, 59999),
             ["Keys", "Voices", "Pedals"],
             {"color": ["Black"]}, (8.0, 15.0),
             "1 Year Warranty"),
        ]),
        ("Drums", [
            ("Cajon Drum", ["BeatBox"], (2499, 9999),
             ["Wood", "Snare"],
             {"color": ["Natural"]}, (3.5, 5.5),
             "6 Month Warranty"),
        ]),
    ]),
    ("Gaming", "Gaming gear and accessories", [
        ("Consoles", [
            ("Game Console", ["PlaySphere"], (24999, 59999),
             ["Storage", "Resolution", "Controller"],
             {"storage": ["512GB", "1TB"], "color": ["White", "Black"]}, (3.5, 5.0),
             "1 Year Warranty"),
        ]),
        ("Controllers", [
            ("Wireless Controller", ["PadPro"], (1499, 6999),
             ["Connectivity", "Battery", "Haptics"],
             {"color": ["Black", "White", "Blue"]}, (0.2, 0.3),
             "6 Month Warranty"),
        ]),
        ("VR Headsets", [
            ("VR Headset", ["ImmerseVR"], (19999, 79999),
             ["Resolution", "Refresh", "Tracking"],
             {"color": ["White", "Black"]}, (0.5, 0.8),
             "1 Year Warranty"),
        ]),
        ("Gaming Chairs", [
            ("Gaming Chair", ["ThronePlay"], (8999, 29999),
             ["Material", "Recline", "Armrests"],
             {"color": ["Black-Red", "Black-Blue", "Black"]}, (18.0, 25.0),
             "1 Year Warranty"),
        ]),
    ]),
    ("Stationery", "Stationery and art supplies", [
        ("Art Supplies", [
            ("Acrylic Paint Set", ["ColorSplash"], (299, 1999),
             ["Colors", "Volume"],
             {"size": ["12 colors", "24 colors"], "color": ["Multicolor"]}, (0.3, 0.8),
             "7-day Replacement"),
            ("Sketchbook", ["DrawLine"], (149, 899),
             ["Pages", "Size", "GSM"],
             {"size": ["A5", "A4"]}, (0.2, 0.5),
             "7-day Replacement"),
        ]),
        ("Paper Products", [
            ("Sticky Notes", ["StickMemo"], (49, 299),
             ["Count", "Size"],
             {"size": ["Pack of 4", "Pack of 12"], "color": ["Yellow", "Multicolor"]}, (0.05, 0.15),
             "7-day Replacement"),
        ]),
    ]),
    ("Other Marketplace Products", "Gifts, collectibles and more", [
        ("Gift Cards", [
            ("Gift Card", ["GiftMint"], (100, 10000),
             ["Value", "Delivery"],
             {"size": ["₹100", "₹500", "₹1000", "₹5000"]}, (0.01, 0.02),
             "Non-returnable"),
        ]),
        ("Collectibles", [
            ("Figurine", ["ShelfHero"], (499, 9999),
             ["Height", "Material", "Edition"],
             {"color": ["Multicolor"]}, (0.2, 0.8),
             "7-day Replacement"),
        ]),
        ("Party Supplies", [
            ("Party Decor Kit", ["CelebratePop"], (299, 1999),
             ["Pieces", "Theme"],
             {"color": ["Multicolor"], "size": ["30 pc", "60 pc"]}, (0.3, 0.8),
             "7-day Replacement"),
        ]),
    ]),
])
