
def detect_category(description):
    if not description:
        return "generique"
    desc = str(description).lower()
    if any(x in desc for x in ["restaurant", "gastronomie", "cuisine", "bistrot", "manger", "plat", "déjeuner", "dîner", "carte", "menu"]):
        return "restaurant"
    if any(x in desc for x in ["boulangerie", "pain", "viennoiserie", "pâtisserie", "pâtissier", "croissant", "baguette", "fournil"]):
        return "boulangerie"
    if any(x in desc for x in ["coiffeur", "coiffure", "barbier", "coupe", "cheveux", "salon de coiffure", "visagiste"]):
        return "coiffeur"
    if any(x in desc for x in ["esthétique", "institut", "beauté", "onglerie", "massage", "soin", "visage", "spa", "ongle", "manucure"]):
        return "esthetique"
    if any(x in desc for x in ["garage", "voiture", "mécanique", "réparation", "auto", "pneu", "vidange"]):
        return "garage"
    return "generique"

print(f"Test Resto: {detect_category('Un excellent restaurant italien avec des pâtes fraîches.')}")
print(f"Test Ongles: {detect_category('Institut de beauté spécialisé dans l''onglerie et les massages.')}")
print(f"Test None: {detect_category(None)}")
