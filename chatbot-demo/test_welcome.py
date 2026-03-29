
def get_welcome_message(category, name):
    name_str = name if name else "l'entreprise"
    welcomes = {
        "restaurant": f"Bienvenue chez {name_str} ! Je suis votre assistant pour découvrir notre carte et réserver votre table. Que puis-je pour vous ?",
        "boulangerie": f"Bienvenue chez {name_str} ! Nos pains et viennoiseries sont prêts. Je suis là pour vous conseiller. Quel délice cherchez-vous ?",
        "coiffeur": f"Bienvenue chez {name_str} ! Je suis ravi de vous aider à choisir une prestation ou prendre rendez-vous. Comment puis-je vous sublimer ?",
        "esthetique": f"Bienvenue dans votre institut {name_str} ! Je suis votre assistant bien-être. Souhaitez-vous découvrir nos soins ou un moment de détente ?",
        "garage": f"Bienvenue au garage {name_str} ! Je suis là pour vos questions mécaniques ou vos prises de rendez-vous entretien. Quel est votre besoin ?",
        "generique": f"Bonjour et bienvenue chez {name_str} ! Je suis votre assistant virtuel. Comment puis-je vous renseigner aujourd'hui ?"
    }
    return welcomes.get(category, welcomes["generique"])

print(f"Resto: {get_welcome_message('restaurant', 'Chez Gusto')}")
print(f"Ongles: {get_welcome_message('esthetique', 'Belle à Croquer')}")
print(f"Générique: {get_welcome_message('generique', None)}")
