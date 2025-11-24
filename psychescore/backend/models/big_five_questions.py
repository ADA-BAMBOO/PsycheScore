BIG_FIVE_QUESTIONS = [
    # Openness to Experience (O)
    {"id": "O1", "trait": "O", "text": "I have a vivid imagination.", "positive": True},
    {"id": "O2", "trait": "O", "text": "I am interested in many different things.", "positive": True},
    {"id": "O3", "trait": "O", "text": "I prefer work that is routine.", "positive": False}, # Reverse scored
    {"id": "O4", "trait": "O", "text": "I like to reflect on things.", "positive": True},

    # Conscientiousness (C)
    {"id": "C1", "trait": "C", "text": "I am always prepared.", "positive": True},
    {"id": "C2", "trait": "C", "text": "I pay attention to details.", "positive": True},
    {"id": "C3", "trait": "C", "text": "I often forget to put things back in their proper place.", "positive": False}, # Reverse scored
    {"id": "C4", "trait": "C", "text": "I make plans and stick to them.", "positive": True},

    # Extraversion (E)
    {"id": "E1", "trait": "E", "text": "I am the life of the party.", "positive": True},
    {"id": "E2", "trait": "E", "text": "I don't mind being the center of attention.", "positive": True},
    {"id": "E3", "trait": "E", "text": "I keep in the background.", "positive": False}, # Reverse scored
    {"id": "E4", "trait": "E", "text": "I start conversations easily.", "positive": True},

    # Agreeableness (A)
    {"id": "A1", "trait": "A", "text": "I sympathize with others' feelings.", "positive": True},
    {"id": "A2", "trait": "A", "text": "I take time out for others.", "positive": True},
    {"id": "A3", "trait": "A", "text": "I insult people.", "positive": False}, # Reverse scored
    {"id": "A4", "trait": "A", "text": "I feel others' emotions.", "positive": True},

    # Neuroticism (N)
    {"id": "N1", "trait": "N", "text": "I get stressed out easily.", "positive": True},
    {"id": "N2", "trait": "N", "text": "I worry about things.", "positive": True},
    {"id": "N3", "trait": "N", "text": "I am relaxed most of the time.", "positive": False}, # Reverse scored
    {"id": "N4", "trait": "N", "text": "I get upset easily.", "positive": True},
]

# Response scale: 1 (Strongly Disagree) to 5 (Strongly Agree)
RESPONSE_SCALE = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree"
}