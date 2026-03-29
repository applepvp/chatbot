=== APPLICATION DÉMO CHATBOT LOCAL ===

Cette application permet de générer un chatbot personnalisé (basé sur Gemini) 
pour des petites entreprises (restaurants, boutiques, etc.).

== PRÉREQUIS ==
1. Python 3.8 ou supérieur installé sur votre machine.
2. Une clé API Google Gemini (gratuite).

== INSTALLATION ET LANCEMENT ==
Ouvrez un terminal (Invite de commandes ou PowerShell) dans le dossier "chatbot-demo" et tapez :

1. Installer les dépendances :
   pip install -r requirements.txt

2. Définir votre clé API Gemini (remplacez 'VOTRE_CLE' par votre vraie clé) :
   Sur Windows (PowerShell) : $env:GEMINI_API_KEY="VOTRE_CLE"
   Sur Windows (CMD) : set GEMINI_API_KEY=VOTRE_CLE
   Sur Mac/Linux : export GEMINI_API_KEY="VOTRE_CLE"

3. Lancer le serveur :
   python app.py

== UTILISATION ==
1. Ouvrez votre navigateur sur: http://localhost:5000/
   -> Interface d'administration pour configurer l'entreprise.
   -> Remplissez les informations et cliquez sur "Sauvegarder et Générer".

2. Ouvrez votre navigateur sur: http://localhost:5000/demo
   -> Fausse page de démonstration "Le Petit Bouchon".
   -> Vous y trouverez le widget en bas à droite pour tester l'intelligence artificielle !

== INTÉGRATION CHEZ LE CLIENT ==
Sur le site de votre client final, ajoutez simplement cette ligne juste avant la balise </body> :
<script src="http://localhost:5000/widget.js"></script>
