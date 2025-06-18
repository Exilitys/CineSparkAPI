from fpdf import FPDF
from scriptdata import ScriptData

# Data strcutre example 
data = {
    "logline": "A lonely lighthouse keeper discovers a mysterious sea creature that challenges everything he believes about isolation and connection.",
    "synopsis": "Marcus, a reclusive lighthouse keeper on a remote island, has spent five years in solitude after a tragic accident. His monotonous routine is shattered when he discovers Naia, a wounded sea creature with intelligence beyond human understanding. As Marcus nurses Naia back to health, he learns that she comes from an ancient underwater civilization facing extinction due to ocean pollution. Together, they must overcome their fear of the outside world to save both their species, discovering that true connection transcends the boundaries of species and solitude.",
    "characters": [
        {
            "name": "Marcus",  
            "description": "A weathered 45-year-old former marine biologist turned lighthouse keeper",
            "motivation": "To find redemption and purpose after losing his research team in a diving accident",
            "arc": "From isolated and guilt-ridden to connected and purposeful"
        },
        {
            "name": "Naia",
            "description": "An intelligent sea creature from an ancient underwater civilization",
            "motivation": "To save her dying people and forge understanding between species",
            "arc": "From fearful and suspicious to trusting and collaborative"
        },
        {
            "name": "Dr. Sarah Chen",
            "description": "Marcus's former colleague and marine research director",
            "motivation": "To bring Marcus back to the scientific community and continue their work",
            "arc": "From professional concern to personal understanding and support"
        }
    ],
    "three_act_structure": {
        "act1": "Marcus maintains his isolated routine at the lighthouse, haunted by memories of the accident. During a fierce storm, he discovers Naia washed ashore, injured and unlike anything he's ever seen. Despite his fear, he decides to help her recover.",
        "act2": "As Naia heals, she and Marcus develop a unique form of communication. She reveals the dire situation of her underwater civilization and the connection to human pollution. Marcus must confront his past trauma and decide whether to help Naia contact the outside world, risking exposure of both their secrets.",
        "act3": "Marcus and Naia work together to establish contact with Dr. Chen and the scientific community. They face skepticism and danger as corporate interests threaten both the lighthouse and Naia's people. The climax involves Marcus overcoming his isolation to lead a mission that saves Naia's civilization and establishes a new era of interspecies cooperation."
    },
    "scenes": [
        {
            "id": "1",
            "title": "Morning Routine",
            "setting": "Lighthouse interior at dawn",
            "description": "Marcus performs his daily maintenance routine with mechanical precision",
            "characters": ["Marcus"],
            "key_actions": ["Checking lighthouse equipment", "Making coffee", "Looking out at empty ocean"]
        },
        {
            "id": "2",
            "title": "The Discovery",
            "setting": "Rocky shore after storm",
            "description": "Marcus finds Naia unconscious on the beach, making the choice to help",
            "characters": ["Marcus", "Naia"],
            "key_actions": ["Discovering Naia", "Initial fear and curiosity", "Decision to help"]
        },
        {
            "id": "3",
            "title": "First Contact",
            "setting": "Lighthouse basement pool",
            "description": "Naia awakens and first attempts at communication begin",
            "characters": ["Marcus", "Naia"],
            "key_actions": ["Naia's awakening", "Establishing basic communication", "Building trust"]
        }
    ]
}

black_rgb = (0, 0, 0)
white_rgb = (255, 255, 255)

class PDF(FPDF):
    def header(self):
        self.set_fill_color(*white_rgb)
        self.rect(0, 0, self.w, self.h, 'F')

    def project_title(self, title):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*black_rgb)
        self.cell(0, 15, title, ln=1, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*black_rgb)
        self.cell(0, 10, title, ln=1)
        self.ln(2)

    def sub_chapter_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*black_rgb)
        self.cell(0, 10, title, ln=1)
        self.ln(1)

    def chapter_body(self, text):
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*black_rgb)
        self.multi_cell(0, 10, text)
        self.ln()


def generate_story_pdf(project_name: str, data: ScriptData, file_path: str):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.project_title(project_name)

    pdf.chapter_title("Logline")
    pdf.chapter_body(data.logline)

    pdf.chapter_title("Synopsis")
    pdf.chapter_body(data.synopsis)

    pdf.chapter_title("Three-Act Structure")
    pdf.sub_chapter_title("Act 1 : Setup")
    pdf.chapter_body(data.three_act_structure["act1"])

    pdf.sub_chapter_title("Act 2 : Confrontation")
    pdf.chapter_body(data.three_act_structure["act2"])

    pdf.sub_chapter_title("Act 3 : Resolution")
    pdf.chapter_body(data.three_act_structure["act3"])

    pdf.chapter_title("Characters")
    for i, char in enumerate(data.characters):
        pdf.sub_chapter_title(f"{i+1}.{char.name}")
        pdf.sub_chapter_title("Description")
        pdf.chapter_body(char.description)
        pdf.sub_chapter_title("Motivation")
        pdf.chapter_body(char.motivation)
        pdf.sub_chapter_title("Character Arc")
        pdf.chapter_body(char.arc)

    pdf.chapter_title("Scenes")
    for i, scene in enumerate(data.scenes):
        pdf.sub_chapter_title(f"Scene {i+1} - {scene.title}")
        pdf.sub_chapter_title("Setting")
        pdf.chapter_body(scene.setting)
        pdf.sub_chapter_title("Description")
        pdf.chapter_body(scene.description)
        pdf.sub_chapter_title("Characters")
        pdf.chapter_body(", ".join(scene.characters))
        pdf.sub_chapter_title("Key Actions")
        pdf.chapter_body(", ".join(scene.key_actions))

    pdf.output(file_path)



