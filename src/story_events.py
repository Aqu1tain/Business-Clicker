from dataclasses import dataclass

@dataclass
class StoryEvent:
    title: str
    description: str
    trigger_value: int
    event_type: str = 'money'
    triggered: bool = False
    display_time: int = None
    display_duration: int = 5000

def initialize_story_events():
    return [
        StoryEvent(
            "Premier Jour",
            "Bienvenue dans l'entreprise ! On vous a assigné un bureau avec un ordinateur qui tourne sous Windows 95. Le chef vous rappelle gentiment qu'il faut remplir la feuille de présence tous les matins.",
            0
        ),
        StoryEvent(
            "Premier Café",
            "Vous découvrez la machine à café. La pause de 10h ne sera plus jamais la même ! Les collègues vous initient au sacro-saint rituel du café-clope-potins.",
            10
        ),
        StoryEvent(
            "Premier Salaire",
            "Votre premier salaire ! Maintenant vous pouvez vous acheter des sandwichs à la cafétéria. Plus besoin de manger des pâtes tous les midis.",
            100
        ),
        StoryEvent(
            "La Routine",
            "Vous commencez à maîtriser l'art de paraître occupé pendant les heures creuses. Votre technique de la double fenêtre Excel-Facebook est maintenant au point.",
            100,
            "clicks"
        ),
        StoryEvent(
            "Expert Excel",
            "Vous savez maintenant faire des tableaux croisés dynamiques. Vos collègues vous regardent différemment. Le stagiaire vous demande même des conseils !",
            200,
            "clicks"
        ),
        StoryEvent(
            "Première Réunion",
            "Vous êtes invité à une réunion qui aurait pu être un email. Mais vous avez découvert où se cachaient les meilleurs gâteaux de la salle de pause !",
            3,
            "upgrades"
        ),
        StoryEvent(
            "Maître du Café",
            "Les gens viennent maintenant de l'autre bout du bâtiment pour votre café. Vous êtes une légende vivante de la pause café. Même le DRH vous demande votre secret.",
            8,
            "upgrades"
        ),
        StoryEvent(
            "Promotion : Assistant",
            "Félicitations ! Vous êtes promu Assistant. Vous avez maintenant accès à la grande imprimante et aux fournitures de bureau premium. Les Post-it de luxe, ça change la vie !",
            200,
            "money"
        ),
        StoryEvent(
            "Promotion : Chargé de Mission",
            "Vous êtes maintenant Chargé de Mission ! On vous a donné un badge pour la salle de réunion VIP et une place de parking presque couverte. La classe !",
            500,
            "money"
        ),
        StoryEvent(
            "Promotion : Chef de Projet",
            "Vous êtes maintenant Chef de Projet ! Votre équipe vous respecte. Vous avez accès au distributeur de snacks de luxe et aux toilettes VIP.",
            2000,
            "money"
        ),
        StoryEvent(
            "Promotion : Directeur Adjoint",
            "Vous êtes maintenant Directeur Adjoint ! On vous a donné une secrétaire personnelle et une place de parking couverte. Les affaires sont sérieuses.",
            5000,
            "money"
        ),
        StoryEvent(
            "Promotion : Directeur",
            "Vous êtes maintenant Directeur ! On vous a offert un fauteuil de direction. Les gens se lèvent quand vous entrez dans la salle de réunion.",
            10000,
            "money"
        ),
        StoryEvent(
            "Promotion : PDG",
            "Vous êtes maintenant PDG ! On vous a offert un jet privé. Les décisions sont maintenant prises dans votre tour d'ivoire.",
            50000,
            "money"
        )
    ]